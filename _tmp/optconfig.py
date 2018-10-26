# -*- coding: utf-8 -*-

class OptConfig(dict):
    def __init__(self, *args, **kwargs):
        super(OptConfig, self).__init__(*args, **kwargs)
        self.__dict__ = self

config = OptConfig()

config.logs = {
    'log-level':  'warning',
    # "log-file": "dev-warnings.log",
    # "config": "log-config.config",
}

config.data = [
    {
        'engine': 'postgres.psycopg2',
        'params': {
                "host": "dev-inside-pg.unix.tensor.ru",
                "port": 6432,
                "dbname": "log",
                "user": "postgres",
                "password": "postgres",
                "x-logic": "dev-servcs-app.corp.tensor.ru:90",
        },
        'requests': None
    }
]
