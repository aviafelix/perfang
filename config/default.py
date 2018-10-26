"""
Где-нибудь здесь должны быть записаны все настройки по умолчанию,
которые должнны переписываться пользовательскими настройками
в пользовательском конфиге (например, config.py), которые не должны
храниться в гите (либо файл, либо конфигурационная папка, исключённые
из индексации через .gitignore)
"""

cfg = {
    'master': {
        # 'host': '0.0.0.0',
        # 'host': 'localhost',
        # 'host': 'usd-okruginaa',
        'host': 'test-node-one',
        'port': 5000,
        'threaded': True,
        'use_reloader': False,
        'debug': True,
    },
    'slave': {
        # 'host': '0.0.0.0',
        # 'host': 'localhost',
        # 'host': 'usd-okruginaa',
        'host': 'test-node-two',
        'port': 5001,
        'threaded': True,
        'use_reloader': False,
        'debug': True,
    },
}
