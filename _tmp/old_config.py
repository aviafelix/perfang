#!python3
# -*- coding: utf-8 -*-

"""
Создан: 16 Октября 2014

Автор: Александр Округин
E-mail: alexander.okrugin@gmail.com

"""
import logging
import gettext
import time
import simplejson as json
# Слегка модифицированный модуль JsonComment, который теперь обрабатывает
# комментарии в стиле C ("\\")
from jsoncomment import JsonComment
# import configparser
import namespace as ns
import pickle
import __main__ as main

# TODO: Попробовать локализовать с помощью gettext и файлов .po:
# https://docs.python.org/3/library/gettext.html
# http://wiki.maemo.org/Internationalize_a_Python_application
# gettext.install('ru_RU', 'locale')

def ru_translate_argparse(txt):
    txt = txt.replace("usage", "*** Использование")
    txt = txt.replace("positional arguments", "Позиционные аргументы")
    txt = txt.replace("optional arguments", "Необязательные аргументы")
    txt = txt.replace("show this help message and exit", \
        "Показывает сообщение помощи и выходит")
    txt = txt.replace("error:", "*** ошибка,")
    txt = txt.replace("the following arguments are required", \
        "следующие аргументы обязательны")
    # txt = txt.replace("", "")
    return txt

gettext.gettext = ru_translate_argparse

import argparse

mname = main.__file__[main.__file__.rfind('\\') + 1: \
    main.__file__.rfind('.')]

logging.basicConfig(filename='./{0}.log'.format(mname),
                    level=logging.DEBUG,
                    format='%(module)s::[%(levelname)s]: ' \
                    '%(asctime)s: `%(message)s`',
                    datefmt='%d/%m/%Y %H:%M:%S')

# Имя конфигурационного файла, содержащего общие опции
# командной строки. Каждый конфигурационный файл может содержать
# свои опции командной строки или перезаписывать ранее определённые.
CLI_ARGS_CONFIG = "lo_cliargs.config"

LLEVELS = {
    'notset':   logging.NOTSET,
    'debug':    logging.DEBUG,
    'info':     logging.INFO,
    'warning':  logging.WARNING,
    'error':    logging.ERROR,
    'critical': logging.CRITICAL
}

class Options(object):
    """
    Класс, реализующий получение опций командной строки и
    представляющий их в виде конфигурационных настроек.

    """
    def __init__():
        pass

def time_convarg(tv):
    return time.strptime(tv, '%Y-%m-%d %H:%M:%S')

def options():
    parser = argparse.ArgumentParser(prog="layzer", \
        description="Статистика для методов БЛ")

    sites_list = list(config['sites-conf'].keys())
    parser.add_argument('--test-site',
        dest="test-site",
        required=False,
        choices=sites_list,
        help="Тестируемый сайт из списка: {0}" \
            .format(", ".join(sites_list)))

    parser.add_argument('--time-start', '-ts',
        dest="time-start",
        required=True,
        # nargs=2,
        # type=time_convarg,
        type=time_convarg,
        help='Начальное время, с которого проводить анализ' \
            ' в формате "%%Y-%%m-%%d %%H:%%M:%%S", например: ' + \
            time.strftime('"%Y-%m-%d %H:%M:%S"'),
        )

    parser.add_argument('--time-end', '-te',
        dest="time-end",
        required=True,
        # nargs=2,
        type=time_convarg,
        help='Конечное время, по которое проводить анализ' \
            ' в формате "%%Y-%%m-%%d %%H:%%M:%%S", например: ' + \
            time.strftime('"%Y-%m-%d %H:%M:%S"'),
        )

    parser.add_argument('--quantile', '-q',
        required=False,
        type=float,
        help="Вычислить процентиль Q (0.5, 0.95 и т.д.)"
        )

    parser.add_argument('--average', '-avr',
        required=False,
        action="store_true",
        help="Вычислить среднее значение"
        )

    parser.add_argument('--std-dev', '-std',
        dest="std-dev",
        required=False,
        action="store_true",
        help="Вычислить стандартное отклонение"
        )

    parser.add_argument('--count', '-c',
        required=False,
        action="store_true",
        help="Показать количество запросов"
        )

    parser.add_argument('--log-level', '-ll',
        dest="log-level",
        required=False,
        help = 'Задаёт уровень подробности логов',
        # default='error',
        # default='debug',
        choices=LLEVELS.keys(),
        )

    parser.add_argument('--log-file', '-lf',
        dest="log-file",
        required=False,
        help='Задаёт путь к файлу логов',
        # default='./{0}.log'.format(mname),
        )

    parser.add_argument('--config',
        required=False,
        help='Задаёт путь к конфигурации',
        # default='./{0}.config'.format(mname),
        )

    return vars(parser.parse_args())
    # return parser.parse_args()

# class OptCfg(object):
class OptConfig(object):
    pass

class Config(object):
    """
    Класс для чтения и записи конфигурации, хранящейся в JSON-формате.
    Если данные не прочитаны, записывает ошибку в лог.

    Осторожно, при сохранении конфигурации теряются комментарии!

    NB Комментарии в файле могут быть однострочными ("//")
    и многострочными ("/* ... */")

    Ограничения на комментарии:

    * в строке перед "//" и "/*" могут быть только пробелы
    или знаки табуляции;

    * в строке за "*/" могут быть только пробелы или знаки табуляции;

    * разделяющая запятая в конце строки должна быть последним символом.

    """
    def __init__(
            self,
            config_path=None,
            config=None,
            encoding='utf-8',
            logger=None):
        """
        Конструктор класса,
        конфигурация может быть прочитана так:
            config = Config('\path\to\config.config').parsed()

        """ 
        self.logger = logger or logging.getLogger(__name__)

        if config_path != None:
            self._config_path = config_path
            self.load(config_path = config_path,
                config=config,
                encoding = encoding)
        else:
            self._config_data = config
            self._config_path = None

    def load(self, config_path=None, config=None, encoding='utf-8'):
        """
        Парсит файл `config_path` с конфигурацией.

        Кодировка файла по умолчанию utf-8.

        """
        parser = JsonComment(json)
        if config_path != None:
            try:
                self._config_data = parser.load(open(config_path, 'r', \
                    encoding=encoding))
            except IOError as e:
                self.logger.error('Ошибка при чтении конфигурации [{0}]:' \
                    ' "{1}" (I/O error #{2})'
                    .format(config_path, e.strerror, e.errno))
                print("Ошибка при чтении конфигурации")
                exit(-1)
            except json.scanner.JSONDecodeError as e:
                self.logger.error('Ошибка при чтении конфигурации: ' \
                    'ошибка в конфигурационном файле [{0}] (`{1}`)'
                    .format(config_path, str(e)))
                print("Ошибка при чтении конфигурации из файла")
                exit(-1)
        if config != None:
            # self._config_data.update(config)
            self._config_data.update({k:v for k,v in config.items() if v})

    def save(self, config_path=None,
        config=None, encoding='utf-8'):
        """
        Сохраняет конфигурацию в файл.

        Кодировка по умолчанию utf-8.

        Если путь не указан, сохраняется в файл,
        из которого конфигурация была прочитана.

        """
        if config_path == None and self._config_path == None:
            self.logger.warn('Ошибка при сохранении конфигурации: ' \
                              'не указан путь к файлу')

        if config == None and self._config_data == None:
            self.logger.warn('Ошибка при сохранении конфигурации: ' \
                             'пустая конфигурация')

        try:
            json.dump(config or self._config_data,
                      open(config_path or self._config_path,
                           'w', encoding=encoding),
                      indent = 4 * ' ',
                      sort_keys=False, ensure_ascii=False)

        except IOError as e:
            self.logger.error('Ошибка при сохранении конфигурации: "{0}" ' \
                '(I/O error #{1})'.format(e.strerror, e.errno))

    def parsed(self):
        """
        Возвращает разобранную конфигурацию.

        """
        return dict(self._config_data)

# adict = {'opts': ['--zooline', '-z', 'choices=LEVELS.keys()',
#         {'help': 'helpmsg',
#         'default': 'ygygy'}]}

# locals().update(adict)
# optns = ns.Namespace(adict)

# print(__name__)
# print(main.__file__[main.__file__.rfind('\\') + 1:main.__file__.rfind('.')])
# print(sys.argv[0][sys.argv[0].rfind('\\') + 1:sys.argv[0].rfind('.')])

# parser = configparser.ConfigParser()
# parser.read('./tmp/example.ini')
# print(parser['DEFAULT']['inival'])
# with open('./tmp/examplex.ini', 'w') as configfile:
#     parser.write(configfile)

config = Config(mname + '.config').parsed()
logging.debug("Вызван модуль config")
config = Config(mname + '.config', options()).parsed()
config['name'] = mname

if 'log-level' not in config:
    config['log-level'] = 'debug'.format(mname)

if 'log-file' not in config:
    config['log-file'] = './{0}.log'.format(mname)

if 'config' not in config:
    config['config'] = './{0}.config'.format(mname)
