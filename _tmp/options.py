#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import config

settings_file = 'vi-settings.json'

# *********************************************************************
def _options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        required=False,
        default=settings_file,
    )
    parser.add_argument(
        '--method',
        required=False,
        choices=[
            'СБИС.ЗаписатьДокумент',
            'СБИС.ПодготовитьДействие',
            'СБИС.ВыполнитьДействие',
        ],
        default='СБИС.ЗаписатьДокумент',
        help='Имя метода, по которому собирается статистика; например: `СБИС.ЗаписатьДокумент`',
    )
    parser.add_argument(
        '--ip',
        required=False,
        default='10.76.158.227',
        help='IP-адрес, для которого собирается статистика; по умолчанию `10.76.158.227`',
    )
    parser.add_argument(
        '--csv',
        required=False,
        default=None,
        help='Имя csv-файла для вывода данных; если не задано, то выводится на stdout',
    )
    parser.add_argument(
        '--start',
        # required=True,
        help='Время начала очереди в любом формате, понятном dateutil.parser',
    )
    parser.add_argument(
        '--end',
        help='Время окончания очереди в любом формате, понятном dateutil.parser',
        # required=True,
    )

    return parser.parse_args()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
_o = _options()
cfg = config.config(settings_file)

if _o.config != settings_file:
    cfg.update(read_config(cfg_name=o.config))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    pass
