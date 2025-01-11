# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 00:52:56 2018

@author: kunlin.l
"""

import atedu.enums as enums
from atedu.setting import get_setting, get_support, set_setting, get_version
from atedu.api.history import *
from atedu.api.bpfactor import *
from atedu.api import fundamental as fundamental_api
from atedu.api import riskmodel as riskmodel_api
# noinspection PyUnresolvedReferences
from atedu.api.fundamental import *
# noinspection PyUnresolvedReferences
from atedu.api.riskmodel import *

__all__ = [
    'get_kdata_n',
    'get_kdata',
    'get_tick_data',
    'get_code_list',
    'get_main_contract',
    'get_future_info',
    'get_future_contracts',
    'get_stock_info',
    'get_trading_days',
    'get_trading_time',
    'get_factor_by_factor',
    'get_factor_by_day',
    'get_factor_by_code',
    'get_setting',
    'get_support',
    'set_setting',
    'get_version',
    'enums',
    *fundamental_api.__all__,
    *riskmodel_api.__all__,
]
