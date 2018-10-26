#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import simplejson as json

# *********************************************************************
def read_config(cfg_name):
    """
    Чтение конфигурации
    """
    with open(cfg_name, 'r', encoding='utf-8') as f:
        return json.load(f)

# *********************************************************************
class Config(object):
    """
    Хранит информацию о конфигурации; может перезаписываться информация
    содержимым из конфигурационного файла json, передаваемого в конфиг
    через метод __call__.
    """
    cfg = {}
    def __init__(self, configname=None):
        if configname is not None:
            self.cfg = read_config(configname)
    def __call__(self, configname):
        j = read_config(configname)
        self.cfg.update(j)
        return self.cfg
    def __setitem__(self, attr, value):
        self.cfg[attr] = value

# *********************************************************************
operations = {
    'startswith': ['str', 'startswith'],
    'endswith': ['str', 'endswith'],
    'matches': ['str', 'matches'],
    'eq': '__eq__',
    'equal': '__eq__',
}

# *********************************************************************
# Здесь соглашение по записям в getstat следующее.
# Если тип по ключу не список и не словарь, то подразумевается
# равенство. Если словарь, то действие определяется на основе операций,
# определённых в operations. Если список, то значение может быть
# любым из списка. Таким образом, 'key': {'eq': value} или 'key': {'equal': value}
# равнозначно определению 'key': value (сокращённая форма).
collect = [
    # Описание структуры для сбора статистики по методам
    {
        'method': 'СБИС.ЗаписатьДокумент',
        'getstat': [
            {   # [pd][start]
                'level': 0,
                'type': '[pd]',
                'state': 'begin',
            },
            {   # [pd][finish]
                'level': 0,
                'type': '[pd]',
                'state': 'end',
            },
            {   # [w][finish]
                'level': 0,
                'type': '[w]',
                'state': 'end',
            },
            {   # - ЭДО.ЗаписатьДокумент
                'level': 0,
                'type': 'method',
                'state': 'end',
                'name': {
                    'equal': 'ЭДО.ЗаписатьДокумент',
                },
            },
            {   # -- Контрагент.* (Контрагент.НайтиПоИКК, Контрагент.ПоИННКППКФ, Контрагент.Find)
                'level': 1,
                'type': 'method',
                'state': 'end',
                'name': {
                    'startswith': 'Контрагент.',
                    # 'matches': 'Контрагент.*',
                },
            },
            {   # -- *.Создать (ДокОтгрИсх.Создать)
                'level': 1,
                'type': 'method',
                'state': 'end',
                'name': {
                    'endswith': '.Создать',
                    # 'matches': '*.Создать',
                },
            },
            {   # -- *.ПослеЗагрузки (ЭДОНакл.ПослеЗагрузки и ещё несколько)
                'level': 1,
                'type': 'method',
                'state': 'end',
                'name': {
                    'endswith': '.ПослеЗагрузки',
                    # 'matches': '*.ПослеЗагрузки',
                },
            },
            {   # -- Документ.ЕстьПодписьНаСервере
                'level': 1,
                'type': 'method',
                'state': 'end',
                'name': {
                    'equal': 'Документ.ЕстьПодписьНаСервере',
                },
            },
            {   # - ЭДО.ОпределитьФорматИПодстановку
                'level': 0,
                'type': 'method',
                'state': 'end',
                'name': {
                    'equal': 'ЭДО.ОпределитьФорматИПодстановку',
                },
                # 'method': 'max',
                # 'method': 'avg',
            },
            {   # - Контрагент.UpdateP
                'level': 0,
                'type': 'method',
                'state': 'end',
                'name': {
                    'equal': 'Контрагент.UpdateP',
                },
            },
        ]
    },
    {
        'method': 'СБИС.ПодготовитьДействие',
    },
    {
        'method': 'СБИС.ВыполнитьДействие',
    }
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
config = Config()
config['collect'] = collect
config['operations'] = operations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    pass
