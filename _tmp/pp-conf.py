#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import regex, re
import simplejson as json
from simplezabbixapi import zabbixcaller
import argparse
import datetime
import sys
import os
import hashlib

# Функция хэширования, которая применяется в случае,
# когда файл не находится в каком-то подкаталоге.
hashf = hashlib.sha256

# Как вариант:
# https://github.com/seperman/deepdiff

settings_file = 'pp-conf-settings.json'
hlink = 'http://zabbix.sbis.ru/history.php?itemid={hostid}&action=showvalues'

# *********************************************************************
class RedirectStdStreams(object):
    """
    Перенаправляет вывод из stdout/stderr в файл, если имя файла задано.

    Пример использования:
    with RedirectStdStreams(filename=filename):
        print("Сообщение появится в файле, если filename не None")
    """

    _output_stream = None
    _filename = None

    def __init__(self, filename):
        if filename is not None:
            self._filename = filename
            self._output_stream = open(filename, 'a', encoding='utf-8')

        self.oldstdout = sys.stdout
        self.oldstderr = sys.stderr

    def __enter__(self):
        self.oldstdout.flush()
        self.oldstderr.flush()

        if self._output_stream is not None:
            sys.stdout = self._output_stream
            sys.stderr = self._output_stream

    def __exit__(self, exc_type, exc_value, traceback):
        if self._output_stream is not None:
            self._output_stream.flush()
            sys.stdout = self.oldstdout
            sys.stderr = self.oldstderr

# *********************************************************************
def list2dict(l):
    """
    Строит по списку словарь, в котором ключи определяют
    номер элемента в списке
    """
    return dict(zip(range(len(l)), l))

# *********************************************************************
def compare(d1, d2, key=None):
    """
    Функция, которая сравнивает между собой словари/списки
    и возвращает структуру, описывающую изменения.

    Для списков имеет значение порядок,
    т.е. [1, 2, 3, 5] != [2, 3, 5, 1] != [5, 1, 3, 2]
    """

    if type(d1) is not type(d2):
        # print("Изменился", d1, "на", d2)
        return({'modified': (d1, d2), 'key': key})

    # Теперь можно, на самом деле, определять тип
    # только первого или только второго аргумента
    # Здесь сравниваются словари
    if type(d1) is dict:

        d1_keys = set(d1)
        d2_keys = set(d2)

        intersect_keys = d1_keys.intersection(d2_keys)

        added = d2_keys - d1_keys
        removed = d1_keys - d2_keys

        modified = [o for o in intersect_keys if d1[o] != d2[o]]
        same = set(o for o in intersect_keys if d1[o] == d2[o])

        cmp = {}

        if len(added) != 0:
            cmp['added'] = {g: d2[g] for g in added}

        if len(removed) != 0:
            cmp['removed'] = {g: d1[g] for g in removed}

        if len(modified) != 0:
            cmp['modified'] = [compare(d1[g], d2[g], key=g) for g in modified]

        if len(same) != 0:
            cmp['same'] = {g: d1[g] for g in same}

        cmp['key'] = key

        return cmp

    # Здесь сравниваются списки.
    # Список преобразуется в словарь, и для него рекурсивно
    # вызывается функция.
    if type(d1) is list:
        return compare(list2dict(d1), list2dict(d2), key=key)

    # Здесь сравниваются строки и числа
    if type(d1) is str or type(d1) is int:
        if d1 != d2:
            return {
                'modified': (d1, d2),
                'key': key,
            }

# *********************************************************************
def path2str(path, basestr='', sepstr='', ):
    """
    Возвращает строку в виде [key1][key2]... по пути,
    заданному списком [key1, key2, ...]
    """
    return sepstr.join(
        [
            basestr if p is None else '[{p!r}]'.format(p=p) for p in path
        ]
    )

# *********************************************************************
def get_changes(diff, path=None):
    """
    Возвращает отсортированные списки, хранящие отдельно информацию
    об изменениях, добавлениях и удалениях значений по ключам.
    """

    if path is None:
        path = []

    modified = []
    added = []
    removed = []
    same = []

    path.append(diff['key'])

    if 'modified' in diff:
        if isinstance(diff['modified'], tuple):
            modified.append({
                'path': path[:],
                'changes': diff['modified'],
            })
        else:
            for g in diff['modified']:
                _modified, _added, _removed, _same = get_changes(g, path=path)

                modified.extend(_modified)
                added.extend(_added)
                removed.extend(_removed)
                same.extend(_same)

                path.pop()

    if 'added' in diff:
        for g in diff['added']:
            path.append(g)
            added.append({
                'path': path[:],
                'value': diff['added'][g],
            })
            path.pop()

    if 'removed' in diff:
        for g in diff['removed']:
            path.append(g)
            removed.append({
                'path': path[:],
                'value': diff['removed'][g],
            })
            path.pop()

    if 'same' in diff:
        for g in diff['same']:
            path.append(g)
            same.append({
                'path': path[:],
                'value': diff['same'][g],
            })
            path.pop()

    # sort_func = lambda x: path2str(x['path'])
    # sort_func = lambda x: len(x['path'])
    sort_func = lambda x: [len(x['path']), path2str(x['path'])]

    modified.sort(key=sort_func)
    added.sort(key=sort_func)
    removed.sort(key=sort_func)
    same.sort(key=sort_func)

    return modified, added, removed, same

# *********************************************************************
def print_iron_changes_fmt(modified, added, removed, same, show_nochanged=False,
                           host='', port='', enable_zabbix=False,):
    """
    Выводит информацию об изменениях в формате вида:

    <дата> | <время> | <IP> | <имя хоста> | <тип> | <старое значение> | <новое значение> | <ссылка на историю>

    Пример записи:

    2015.05.29 | 12:17:55 | 10.76.156.230 | sb-osr-static2.unix.tensor.ru | MEMORY | 4.01 Gb | 1.96 Gb | http://zabbix.sbis.ru/history.php?itemid=77630&action=showvalues
    """
    now = datetime.datetime.now()

    link = hlink.format(hostid=zabbixcaller.get_host_id(host)) if (host != '') and enable_zabbix else ''

    # 
    if len(modified) != 0:
        # Изменились параметры
        for g in modified:
            print(
                "{datetime:%Y.%m.%d} | {datetime:%H:%M:%S} | {ip} | {host}:{port} |" \
                " {path} | {changes[0]!r} | {changes[1]!r} | {link}"
                    .format(
                        datetime=now,
                        ip='0.0.0.0',
                        host=host,
                        port=port,
                        path=path2str(g['path']),
                        changes=g['changes'],
                        link=link,
                    )
            )

    # 
    if len(added) != 0:
        # Добавлены параметры
        for g in added:
            print(
                "{datetime:%Y.%m.%d} | {datetime:%H:%M:%S} | {ip} | {host}:{port} |" \
                " {path} | - | {added} | {link}"
                    .format(
                        datetime=now,
                        ip='0.0.0.0',
                        host=host,
                        port=port,
                        path=path2str(g['path']),
                        added=g['value'],
                        link=link,
                    )
            )

    # 
    if len(removed) != 0:
        # Убраны параметры
        for g in removed:
            print(
                "{datetime:%Y.%m.%d} | {datetime:%H:%M:%S} | {ip} | {host}:{port} |" \
                " {path} | {removed} | - | {link}"
                    .format(
                        datetime=now,
                        ip='0.0.0.0',
                        host=host,
                        port=port,
                        path=path2str(g['path']),
                        removed=g['value'],
                        link=link,
                    )
            )

    # 
    if show_nochanged and len(same) != 0:
        # Не изменились
        for g in same:
            print(
                "{datetime:%Y.%m.%d} | {datetime:%H:%M:%S} | {ip} | {host}:{port} |" \
                " {path} | {same} | {same} | {link}"
                    .format(
                        datetime=now,
                        ip='0.0.0.0',
                        host=host,
                        port=port,
                        path=path2str(g['path']),
                        same=g['value'],
                        link=link,
                    )
            )

# *********************************************************************
def print_changes(modified, added, removed, same, show_nochanged=True):
    """
    Выводит на экран (или в файл, если включено перенаправление из stdout)
    информацию об изменениях в виде записей об изменившихся, добавленных
    или убранных параметрах.
    """
    print("====================================================\n")
    # 
    if len(modified) != 0:
        print("* [ Изменились параметры ] *\n")
        for g in modified:
            print(
                # "параметр {path}\nбыло:  {changes[0]!r}\nстало: {changes[1]!r}\n"
                # "Изменился параметр {path}:\n{changes[0]!r} -> {changes[1]!r}\n"
                "{path}: {changes[0]!r} -> {changes[1]!r}"
                    .format(
                        path=path2str(g['path']),
                        changes=g['changes'],
                    )
            )
        print()

    # 
    if len(added) != 0:
        print(" * [Добавлены параметры] *\n")
        for g in added:
            print(
                "{path} = {value!r}"
                    .format(
                        path=path2str(g['path']),
                        value=g['value'],
                )
            )
        print()

    # 
    if len(removed) != 0:
        print(" * [Убраны параметры] *\n")
        for g in removed:
            print(
                "{path} = {value!r}"
                    .format(
                        path=path2str(g['path']),
                        value=g['value'],
                )
            )
        print()

    # 
    if show_nochanged and len(same) != 0:
        print(" == Не изменились == ")
        for g in same:
            print(
                "{path} = {value!r}"
                    .format(
                        path=path2str(g['path']),
                        value=g['value'],
                )
            )
    print()

# *********************************************************************
def print_diffs(diff, path=None):
    """
    Выводит на stdout неотсортированные сообщения об различиях в конфигурациях
    препроцессора на основе структуры, хранящей информацию о разнице словарей.
    """

    if path is None:
        path = []

    path.append(diff['key'])

    if 'modified' in diff:
        if isinstance(diff['modified'], tuple):
            print("Изменились значения:")
            print(
                " с {path} = {changes[0]!r}\n на {path} = {changes[1]!r}"
                .format(
                    changes=diff['modified'],
                    path=path2str(path),
                )
            )
            return
        else:
            for g in diff['modified']:
                print_diffs(g, path=path)
                path.pop()

    if 'added' in diff:
        print("Добавлены ключи:")
        for g in diff['added']:
            print(
                "{path}[{key!r}] = {value!r}"
                    .format(
                        path=path2str(path),
                        key=g,
                        value=diff['added'][g]
                    )
            )

    if 'removed' in diff:
        print("Удалены ключи:")
        for g in diff['removed']:
            print(
                "{path}[{key!r}] = {value!r}"
                    .format(
                        path=path2str(path),
                        key=g,
                        value=diff['removed'][g]
                    )
            )

    if 'same' in diff:
        print("Не изменились:")
        for g in diff['same']:
            print(
                "{path}[{key!r}] = {value!r}"
                    .format(
                        path=path2str(path),
                        key=g,
                        value=diff['same'][g]
                    )
            )

# *********************************************************************
def compare_pp_configs(c1, c2,
        show_nochanged=False,
        draft_view=True,
        host='',
        port='',
        enable_zabbix=False,
    ):
    """
    Сравнивает две конфигурации препроцессора
    """
    changes = compare(c1, c2)
    if draft_view:
        print_diffs(diff=changes)
    else:
        # print_changes(*get_changes(diff=changes), show_nochanged=show_nochanged)
        print_iron_changes_fmt(*get_changes(diff=changes),
            show_nochanged=show_nochanged,
            host=host,
            port=port,
            enable_zabbix=enable_zabbix
        )

# *********************************************************************
def read_pp_config(filename, encoding='utf-8'):
    """
    Читает конфигурации препроцессора из файлов
    (возвращает словарь, хранящий структуру json'а)
    """
    with open(filename, 'r', encoding=encoding) as f:
        try:
            j = json.load(f)
        except json.scanner.JSONDecodeError:
            return {}

    return j

# *********************************************************************
def show_cmp_dict(cmp):
    """
    Отображает структуру, описывающую различия в параметрах
    """
    print(
        json.dumps(
            cmp,
            sort_keys=True,
            indent=4,
            separators=(',', ':'),
        )
    )

# *********************************************************************
def _options():
    """
    Опции утилиты
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--config',
        required=False,
        default=settings_file,
    )
    parser.add_argument(
        '--compare-files',
        required=True,
        type=str,
        # nargs=2,
        nargs='+',
        help='Файлы для сравнения. Если задан один аргумент, ' \
             'то файл сравнивается с версией, которая находится ' \
             'в хранилище (если он файл) или же, если это директория, ' \
             'то происходит итерирование по файлам в подкаталогах; ' \
             'если два аргумента, то конфиги сравниваются ' \
             'между собой, в хранилище ни один из них не попадает.',
        dest='pp_configs',
    )
    parser.add_argument(
        '--show-nochanged',
        required=False,
        default=False,
        action='store_true',
        help='Отображать список неизменившихся параметров',
    )
    parser.add_argument(
        '--no-update',
        required=False,
        default=False,
        action='store_true',
        help='Не обновлять данные в хранилище',
    )
    parser.add_argument(
        '--enable-zabbix',
        required=False,
        default=False,
        action='store_true',
        help='Включить получение данных из Заббикса для URL (папка, в которой лежит файл, должна совпадать с именем хоста)',
    )
    parser.add_argument(
        '--output-file',
        required=False,
        default=None,
        help='Файл, в который выводится информация об изменениях; ' \
             'если параметр не задан, то это будет stdout',
    )
    parser.add_argument(
        '--draft-view',
        required=False,
        default=False,
        action='store_true',
        help='Отобразить в черновом виде',
    )

    return parser.parse_args()

# *********************************************************************
class XonfigStorage(object):
    """
    Хранит информацию по файлам из предыдущей конфигурации,
    с которой в дальнейшем сравниваются конфиги текущей версии
    """
    def __init__(self, cfg):
        self._cfg = cfg

    def __call__(self, filename, update=True):

        c = self._get(filename)

        if update:
            self._update(filename)

        return c

    def _update(self, filename):
        pass

    def _get(self, filename):
        pass

# *********************************************************************
class XonfigTextStorage(XonfigStorage):
    """
    Реализовано хранение конфигурационных файлов в виде
    обычных файлов в файловой системе.
    """
    def _update(self, filename):
        """
        Обновляет данные в хранилище на текущую версию
        (берёт их из файла filename).
        """
        path = self._filename2savepath(filename)
        os.makedirs(os.path.split(path)[0], exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f_o, \
             open(filename, 'r', encoding='utf-8') as f_i:
            f_o.write(
                f_i.read()
            )

    def _get(self, filename):
        """
        Возвращает данные, если они есть в хранилище.
        В противном случае помещает данные в хранилище
        и возвращает {} (в результате появятся записи
        о добавлении новых параметров в конфиг).
        """
        path = self._filename2savepath(filename)
        os.makedirs(os.path.split(path)[0], exist_ok=True)

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f_i:
                return f_i.read()
        else:
            self._update(filename)
            return None
            # return '{}'

    def _filename2savepath(self, filepath):
        """
        Определять путь к файлу в локальном хранилище.

        Предполагается, что путь к файлу имеет вид:
        <..prefix..>\<hostname>\<filename>. То есть, для примера:
        U:\Абрамов Р.В\prepr\dev-ca-static\dev-ca.tensor.ru-2210.json
        """
        pathlist = os.path.normpath(filepath).split(os.sep)
        filepathhash = hashf(os.path.split(os.path.normpath(filepath))[0].encode('utf-8')).hexdigest()
        # filepathhash = hashf(filepath.encode('utf-8')).hexdigest()

        if len(pathlist) > 2:
            dirname, filename = pathlist[-2:]
        else:
            dirname = ''
            filename, = pathlist[-1:]

        return os.path.join(
            self._cfg['savefolder'],
            filepathhash,
            dirname, filename,
        )

# *********************************************************************
class PPConfigCmp(object):
    """
    Сравнивает конфигурации препроцессора и выводит информацию об изменениях
    """
    _path = None

    def __init__(self, path, storage=XonfigTextStorage(cfg={'savefolder': '.storage'})):
        self._path = path
        self._storage = storage

    def run(self, update=True, enable_zabbix=False):

        if os.path.isdir(self._path):
            dirs = next(os.walk(self._path))[1]

            for _dir in dirs:
                for root, subdirs, files in os.walk(self._path+'/'+_dir):
                    for filename in files:
                        if filename.endswith('.json'):
                            configpath = root + '/' + filename
                            # print(configpath)

                            j2 = read_pp_config(configpath)

                            spath = os.path.normpath(os.path.realpath(configpath)).split(os.sep)
                            host = '' if len(spath) < 2 else spath[-2]
                            port = '' if 'port' not in j2 else j2['port']

                            try:
                                j1 = json.loads(
                                    self._storage(configpath, update=update)
                                )
                            except json.scanner.JSONDecodeError:
                                j1 = {}
                            except TypeError:
                                # Если вернулось None, выходим, в логи ничего не пишем
                                now = datetime.datetime.now()
                                print(
                                    "{datetime:%Y.%m.%d} | {datetime:%H:%M:%S} | {ip} | {host}:{port} |" \
                                    " {path} | - | - | {link}"
                                        .format(
                                            datetime=now,
                                            ip='0.0.0.0',
                                            host=host,
                                            port=port,
                                            path='Появился новый конфиг',
                                            link='',
                                        )
                                )
                                continue

                            compare_pp_configs(
                                j1,
                                j2,
                                show_nochanged=o.show_nochanged,
                                draft_view=o.draft_view,
                                host=host,
                                port=port,
                                enable_zabbix=enable_zabbix,
                            )
        else:

            j2 = read_pp_config(self._path)

            spath = os.path.normpath(os.path.realpath(self._path)).split(os.sep)
            host = '' if len(spath) < 2 else spath[-2]
            port = '' if 'port' not in j2 else j2['port']

            try:
                j1 = json.loads(
                    self._storage(self._path, update=update)
                )
            except json.scanner.JSONDecodeError:
                j1 = {}
            except TypeError:
                # Если вернулось None, выходим, в логи ничего не пишем
                now = datetime.datetime.now()
                print(
                    "{datetime:%Y.%m.%d} | {datetime:%H:%M:%S} | {ip} | {host}:{port} |" \
                    " {path} | - | - | {link}"
                        .format(
                            datetime=now,
                            ip='0.0.0.0',
                            host=host,
                            port=port,
                            path='Появился новый конфиг',
                            link='',
                        )
                )
                return

            compare_pp_configs(
                j1,
                j2,
                show_nochanged=o.show_nochanged,
                draft_view=o.draft_view,
                host=host,
                port=port,
                enable_zabbix=enable_zabbix,
            )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':

    o = _options()

    # Если задано имя выходного файла,
    # то перенаправляем вывод из stdout в него.
    with RedirectStdStreams(filename=o.output_file):

        if len(o.pp_configs) == 1:
            ppc_cmp = PPConfigCmp(o.pp_configs[0])
            ppc_cmp.run(update=not o.no_update, enable_zabbix=o.enable_zabbix)

        elif len(o.pp_configs) == 2:
            compare_pp_configs(
                read_pp_config(o.pp_configs[0]),
                read_pp_config(o.pp_configs[1]),
                show_nochanged=o.show_nochanged,
                draft_view=o.draft_view,
                enable_zabbix=o.enable_zabbix,
            )

        else:
            print("Число файлов с конфигами для сравнения больше 2")
