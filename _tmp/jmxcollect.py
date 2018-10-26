#!python3
# -*- coding: utf-8 -*-

from optconfig import config
import os
from argparse import ArgumentParser
import logging
import pickle
import simplejson as json
import time
import urllib.parse as urlparse
from xml.sax.saxutils import escape
from jinja2 import Environment, PackageLoader
from browsermobproxy.server import Server
from selenium import webdriver
import requests
from harpy.har import Har

module_name = (__file__
                .split('/')[-1]     # unix-like path
                .split('\\')[-1]    # windows paths
                .split('.')[0]      # without extension
            )

env = Environment(
    loader=PackageLoader(
        module_name,
        config.general['jinja2-environment'])
)

logging.basicConfig(filename='./{0}.log'.format(module_name),
                    # level=logging.DEBUG,
                    level=logging.INFO,
                    format='%(module)s::[%(levelname)s]: ' \
                    '%(asctime)s: `%(message)s`',
                    datefmt='%d/%m/%Y %H:%M:%S')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
conformatter = logging.Formatter('%(module)s::[%(levelname)s]: ' \
                '%(asctime)s: `%(message)s`')
console.setFormatter(conformatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

def is_request_blacklisted(url):
    parsed_url = urlparse.urlparse(url)
    return (parsed_url.netloc not in config.whitelisted_hosts
            # Проверка, содержит ли строка любую из подстрок из чёрного списка
            or any(s in parsed_url.path for s in config.blacklisted_requests))

# Получает распарсенный в словарь har-файл
# и по нему строит сценарий JMeter в формате .jmx:
# 
# jmx_settings содержать словарь с ключами формата:
#   'proto' (протокол)
#   'host' (имя хоста)
#   'login' (логин для аутентификации в сценарии)
#   'password' (пароль для аутентификации в сценарии)
#   ... (остальные здесь не интересны)
def make_jmx(har, jmx_settings, path):
    requests = []
    enable_sampler = True
    for entry in har['entries']:
        # Устанавливаем галочку "Follow Redirects" для сэмплера
        # с запросом, если код ответа не в списке 30x
        follow_redirects = entry['response']['status'] not in (301, 302, 303)

        # Фильтруем запросы, которые войдут в итоговый jmx
        if not is_request_blacklisted(entry['request']['url']):

            # Создаём сэмплер для запроса
            jmx_request = make_request(entry=entry,
                enable_sampler=enable_sampler,
                follow_redirects=follow_redirects)

            if jmx_request:
                requests.append(jmx_request)
        else:
            logger.info("** Запрос исключён из сценария (нет в whitelist): " +
                entry['request']['url'])

    jtemplate = env.get_template('test_plan.j2')
    threadgroupname = "Thread Group (BrowserMob Proxy)"
    jmx_conf = env.get_template('config_element.j2').render()
    jmx_auth = env.get_template('authentication.j2').render()
    jmx_timer = env.get_template('timer.j2').render()
    jmx_assert = env.get_template('assertion.j2').render()
    xml = jtemplate.render(dict(
        requests=requests,
        threadgroupname=threadgroupname,
        config_element=jmx_conf,
        authentication=jmx_auth,
        timer=jmx_timer,
        assertion=jmx_assert,
        hostname=jmx_settings['host'],
        login=jmx_settings['login'],
        password=jmx_settings['password'],
        pagename=config.pages_list[path]['name'],
        report_path=config.jmx_vars["report_path"],
        reportfile_path=config.jmx_vars["reportfile_path_1"] + \
            config.pages_list[path]['name'] + \
            config.jmx_vars["reportfile_path_2"]
        ))

    logger.info("Сценарий собран")

    return xml.encode("utf-8")

def make_request(entry, enable_sampler=True, follow_redirects=True):
    parsed_url = urlparse.urlparse(entry["request"]["url"])
    arguments = []
    headers = []
    path = parsed_url.path
    protocol = parsed_url.scheme
    if parsed_url.port != None:
        http_port = parsed_url.port
    else:
        http_port = ""
    sampler_name = path
    host = parsed_url.netloc

    # Для бизнес-логики меняем имя семплера на имя метода БЛ
    if (config.general['rename-bl-samplers'] and (
            entry['request']['url'].find('/sbis-rpc-service300.dll') != -1 or
            entry['request']['url'].find('/service') == 0)):

        # Для POST-запросов имя метода забираем из json
        if entry['request']['method'] == 'POST':
            with open('___dbg___.dmp', 'a', encoding='utf-8') as f:
                f.write(entry['request']['postData']['text'])
            try:
                json_post_data = json.loads(entry['request']['postData']['text'])
            except:
                print(':::', bytes(entry['request']['postData']['text'], encoding='utf-8'))
                quit()
            sampler_name = json_post_data['method']

        # Для GET-запросов имя метода получаем из параметра
        # method в query string
        elif entry['request']['method'] == 'GET':
            sampler_name = urlparse.parse_qs(
                    urlparse.urlparse(entry['request']['url']).query
                )['method'][0]

    # Семплер для GET-запросов
    if entry["request"]["method"] == 'GET':

        # Аргументы для семплера с GET-запросом
        for arg in entry["request"]["queryString"]:
            jmx_arg = make_argument_get(arg)
            arguments.append(jmx_arg)

        # Заголовки запроса
        for header in entry["request"]["headers"]:
            if header["name"] not in config.blacklisted_headers:
                jmx_header = make_header(header)
                headers.append(jmx_header)

        # Собирается сэмплер для GET-запроса
        jtemplate = env.get_template('request_get.j2')
        logger.info(" Добавлен GET-запрос: "+sampler_name)
        result = jtemplate.render(dict(sampler_name=sampler_name,
                                       host=host,
                                       enable_sampler=enable_sampler,
                                       follow_redirects=follow_redirects,
                                       path=path,
                                       protocol=protocol,
                                       http_port=http_port,
                                       headers=headers,
                                       arguments=arguments,
                                       method=entry["request"]["method"]))
    # Семплер для POST-запросов
    elif entry["request"]["method"] == 'POST':

        # Если нет данных в POST-запросе
        if "postData" not in entry['request'].keys():
            logger.info("**  POST-запрос исключён из сценария " \
                  "(нет поля с данными POST-запроса): " + \
                  entry['request']['url'])
            return False

        # Убираются запросы без поля "text" ("CONNECT" к proxy)
        if "text" not in entry['request']['postData'].keys():
            return False

        jtemplate = env.get_template('request_post.j2')

        # Экранирование символов в json для хранения в xml
        arg_value = escape(entry['request']['postData']['text'], {'"': '&quot;'})
        # Убираем пробелы и переносы строки в начале и в конце строки
        arg_value = arg_value.strip()

        logger.info(" Добавлен POST-запрос:"+sampler_name)

        result = jtemplate.render(dict(sampler_name=sampler_name,
                                       host=host,
                                       enable_sampler=enable_sampler,
                                       follow_redirects=follow_redirects,
                                       path=path,
                                       protocol=protocol,
                                       arg_value= arg_value))

    return result

# Создаёт элемент для аргументов GET-запросов
def make_argument_get(har_argument):
    jtemplate = env.get_template('argument_get.j2')
    arg_name = har_argument["name"]

    if arg_name != "method":
        arg_value = urlparse.quote_plus(har_argument["value"])
    else:
        arg_value = har_argument["value"]

    result = jtemplate.render(dict(arg_name=arg_name,
                                   arg_value=arg_value))
    return result

# Создаёт элемент для заголовков HTTP-запросов
def make_header(har_header):
    jtemplate = env.get_template('header.j2')
    header_name = har_header["name"]
    header_value = har_header["value"]

    result = jtemplate.render(dict(header_name=header_name,
                                   header_value=header_value))
    return result

def get_har(site_id, page):
    # Получение HAR-данных из BrowserMob Proxy

    if config.general['get-pages-from-proxy']:
        server = Server(config.general['browsermob-proxy-path'], {"port":9090})
        server.start()

        proxy = server.create_proxy()
        profile = webdriver.FirefoxProfile(config.general['ff-profile-dir'])
        profile.native_events_enabled = True
        profile.accept_untrusted_certs = True
        # profile.set_proxy(proxy.selenium_proxy())
        driver = webdriver.Firefox(firefox_profile=profile,
                                   proxy=proxy.selenium_proxy(),
        )
        resp = requests.get('http://localhost:9090/proxy')
        port = resp.json()['proxyList'][0]['port']
        logger.info(resp.json())

        # Задержка перед началом открытия страницы в браузере
        time.sleep(config.timings['url-open-delay'])

        # Готовим url для разводящей страницы
        url = config.pages[site_id]['proto'] + \
              config.pages[site_id]['host'] + \
              config.pages[site_id]['pages'][0]

        # Пытаемся сделать предварительный запрос
        # proxies = {
        #     'http': 'localhost:'+str(port),
        #     'https': 'localhost:'+str(port),
        # }
        # requests.get(url,
        #              proxies=proxies,
        #              verify=False)

        # Открывается разводящая страница
        driver.get(url)

        # Задержка перед вводом логина и пароля
        time.sleep(config.timings['before-auth-delay'])

        # Авторизуемся на сайте. Ввод логина и пароля. Проверка того,
        # что форма загружена, происходит по наличию кнопки <Войти>.
        driver.find_element_by_id(
            config.login_form['login-button-id'])
        driver.find_element_by_id(
            config.login_form['login-field-id']
            ).clear()
        driver.find_element_by_id(
            config.login_form['login-field-id']
            ).send_keys(config.pages[site_id]['login'])
        driver.find_element_by_id(
            config.login_form['password-field-id']
            ).clear()
        driver.find_element_by_id(
            config.login_form['password-field-id']
            ).send_keys(config.pages[site_id]['password'])
        driver.find_element_by_id(
            config.login_form['login-button-id']
            ).click()

        # Задержка после авторизации, прежде чем будет
        # открыта страница
        time.sleep(config.timings['after-auth-delay'])

        proxy.new_har(
            "collect_requests",
            options={
                "captureHeaders": True,
                "captureContent": True,
                "captureBinaryContent": True,
            }
        )

        url = config.pages[site_id]['proto'] + \
              config.pages[site_id]['host'] + page
        driver.get(url)
        # Ожидание окончания загрузки страницы
        time.sleep(config.timings['page-wait'])

        resp = requests.get('http://localhost:9090/proxy/'+str(port)+'/har')

        with open(config.general['har-output-dir'] + \
            config.pages[site_id]['host'] + '-' + \
            config.pages_list[page]['name'] + '.har', 'wb') as f:
                f.write(resp.content)

        # har = proxy.har
        # har = json.loads(resp.content.decode('utf-8'))
        har = json.loads(resp.text)

        with open(config.general['har-output-dir'] + \
            config.pages[site_id]['host'] + '-' + \
            config.pages_list[page]['name'] + '_.har', 'w') as f:
                f.write(json.dumps(har))

        logger.info("Selenium: quit")
        driver.quit()
        logger.info("BrowserMob Proxy: stop")
        server.stop()
        # В Windows не убивается процесс `java.exe` после server.stop()
        os.system('taskkill /f /im java.exe /t')

    return har['log']

# Парсинг опций командной строки
def options():
    parser = ArgumentParser()
    parser.add_argument(
        '-s',
        '--site-id',
        default='',
        help='Имя хоста, к которому пойдет обращение')
    parser.add_argument(
        '--page',
        '--pages',
        '-p',
        default='',
        help='адрес вызываемой страницы или "all"')
    parser.add_argument(
        '--output-file',
        '-o',
        default='',
        help='Имя выходного файла jmx')
    parser.add_argument(
        '--output-jmx-path',
        '-jp',
        default="",
        help='Папка, в которой сохраняются сценарии jmx')
    parser.add_argument(
        '--output-har-path',
        '-hp',
        default="",
        help='Папка, в которую сохраняются har-файлы')
    parser.add_argument(
        '--page-name',
        '-n',
        default='Страница',
        help='Название страницы в сценарии')

    return parser.parse_args()

# Получаем har-файл для указанной страницы для сайта, заданного параметром site_id
def get_scenarios(site_id, page):

    har = get_har(site_id, page)
    jmx_data = make_jmx(har, config.pages[site_id], page)

    with open(config.general['jmx-output-dir'] + site_id + '-' + \
        config.pages_list[page]['name']+'.jmx', 'wb') as f:
            f.write(jmx_data)

    del jmx_data
    del har

if __name__ == '__main__':

    # har = Har('./har-o/fix-inside.tensor.ru-contacts.html.har', encoding='utf-8')
    # for entry in har.entries:
    #     logger.info(entry.request.method+' '+entry.request.url)
    #     if entry.request.url.find('/service/sbis-rpc-service300.dll') != -1:
    #         try:
    #             logger.info(entry.request.post_data['text']
    #                 .encode('windows-1251')
    #                 .decode('utf-8')
    #                 # .strip('\x00')
    #             )
    #         except:
    #             logger.info(entry.request.post_data['text']
    #                 # .strip('\x00')
    #             )
    #         json_post_data = json.loads(entry.request.post_data['text'].encode('windows-1251').decode('utf-8').strip('\x00'))
    #         sampler_name = json_post_data['method']
    #         logger.info(sampler_name)
    # quit()
    # -----------------------------------

    o = options()
    # Создаём каталоги, в которых будем сохранять данные
    # Не будет ошибки, если каталоги уже существуют
    os.makedirs(config.general['har-output-dir'], exist_ok=True)
    os.makedirs(config.general['jmx-output-dir'], exist_ok=True)

    # Создаём сценарии JMeter'а и har-файлы:
    if o.site_id == '' or o.site_id == 'all':
        # для всех записей
        logger.info("*[Собираются сценарии для всех известных сайтов]")
        for site_id in config.pages.keys():
            if o.page == '' or o.page == 'all':
                # и всех страниц
                logger.info("*>>>[Собираются сценарии для всех страниц]")
                for page in config.pages[site_id]['pages']:
                    get_scenarios(site_id=site_id, page=page)
            else:
                # или указанной страницы
                logger.info("*>>>[Собирается сценарий для страницы {}]".format(o.page))
                get_scenarios(site_id=site_id, page=o.page)
    else:
        # для указанной записи, начинающейся с указанной строки:
        for site_id in config.pages.keys():
            if site_id.startswith(o.site_id):
                logger.info("*[Собираются сценарии для всех известных сайтов]")
                if o.page == '' or o.page == 'all':
                    # и всех страниц
                    logger.info("*>>>[Собираются сценарии для всех страниц]")
                    for page in config.pages[site_id]['pages']:
                        get_scenarios(site_id=site_id, page=page)
                elif o.page in config.pages[site_id]['pages']:
                    # для указанной страницы
                    logger.info("*>>>[Собирается сценарии для страницы {}]".format(o.page))
                    get_scenarios(site_id=site_id, page=o.page)
