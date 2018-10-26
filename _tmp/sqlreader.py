#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from options import cfg
import pandas as pd
import psycopg2
import dateutil.parser
import datetime
# import sqlite3
# import time

# *********************************************************************
def _read_file(filename, encoding='utf-8'):
    """
    Просто функция, которая читает данные из текстового файла
    в кодировке utf-8
    """
    with open(filename, 'r', encoding=encoding) as f:
        return f.read()

# *********************************************************************
class DBReader(object):
    """
    Класс для чтения данных из базы данных
    """

    _request_pattern = None
    _read_interval = None
    _db_cfg = None
    _cfg = None

    def __init__(
        self,
        cfg,
        source=None,
        read_interval=datetime.timedelta(minutes=5),
    ):

        self._cfg = cfg
        self._request_pattern = _read_file(self._cfg['sql-read-request'])
        self._read_interval = read_interval

        if source is not None:
            self._db_cfg = self._cfg[source]

    def set_db_cfg(self, source):
        if source in self._cfg['db']:
            self._db_cfg = self._cfg['db'][source]
        else:
            print("unknown source")

    def _(
        self,
        dt_start,
        dt_end,
        method,
        ip,
        preprocessors=None,
    ):
        """
        Делает запросы к БД и возвращает результат этих запросов.

        ===
        Не сортируем полученный DataFrame перед возвратом
        данных, так как это неэффективно и замедляет работу
        в случае больших объёмов данных.
        Лучше сортировать отфильтрованные данные.
        """

        if self._db_cfg is None:
            print("db config is empty")
            return None

        dts = dateutil.parser.parse(dt_start)
        dte = dateutil.parser.parse(dt_end)

        dfx = None

        for host in self._db_cfg['hosts']:
            print("Connecting to db...")
            conn_postgres = psycopg2.connect(
                "host = '{host}' " \
                "dbname = '{dbname}' " \
                "user = '{user}' " \
                "password = '{password}' " \
                "port = {port}"
                .format(
                    host=host,
                    dbname=self._db_cfg['dbname'],
                    user=self._db_cfg['user'],
                    password=self._db_cfg['password'],
                    port=self._db_cfg['port'],
                )
            )

            print("Reading db...")
            for ti in time_intervals(
                dt1=dts,
                dt2=dte,
                intervals=self._read_interval,
            ):

                df = pd.read_sql(
                    self._request_pattern
                        .format(
                            day=ti[0].day,
                            time_start=ti[0],
                            time_end=ti[1],
                            method=method,
                            ip=ip,
                        ),
                    conn_postgres,
                    coerce_float=False,
                )

                if preprocessors is not None:
                    for ppl, ppf in preprocessors.items():
                        df[ppl] = df[ppl].apply(ppf)

                if dfx is None:
                    dfx = df
                    print(" ::: create ::: ", len(dfx))
                else:
                    dfx = dfx.append(df)
                    print(" ::: read ::: ", len(df))
                    print(" ::: add ::: total = ", len(dfx))

                # df.to_sql(
                #     'Log',
                #     conn_sqlite,
                #     if_exists='append',
                #     index=False,
                #     index_label=["@Log", "TimeStamp"]
                # )

                del df
            
            conn_postgres.close()

        return dfx

# *********************************************************************
def time_intervals(dt1, dt2, intervals=None):
    """
    Возвращает итератор для временных интервалов, на которые разбивает
    указанный промежуток времени.

    intervals -- timedelta-объект (длительностью меньше суток);
        если значение не None, то интервалы времени, кроме
        разбиения по суткам (через 00:00), делятся на указанные
        промежутки.
    """
    # Если правая граница лежит слева, то ничего не возвращаем.
    # Но можно предусмотреть возможность произвольного порядка
    # временных границ.
    if dt2 < dt1:
        # dt2, dt1 = dt1, dt2
        yield None

    r = []

    dt_left = dt1
    next_day = dt_left.replace(
        day=dt_left.day,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    tdelta = datetime.timedelta(days=1)
    next_day += tdelta

    if intervals == None:
        next_right = dt2
    else:
        next_right = dt1 + intervals

    while dt_left < dt2:
        dt_right = min(next_day, next_right)
        dt_right = min(dt_right, dt2)

        yield [dt_left, dt_right]
        dt_left = dt_right

        next_day = dt_left.replace(
            day=dt_left.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        next_day += tdelta

        if intervals != None and dt_right == next_right:
            next_right += intervals

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dbreader = DBReader(cfg)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    pass
