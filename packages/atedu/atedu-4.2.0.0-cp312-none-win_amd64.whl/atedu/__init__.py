# -*- coding: utf-8 -*-
"""
变更日志
-----------
2018-11-12 增加更加详细的基本面数据 api, 见 atedu.fundamental 模块
"""

import pandas as pd
import numpy as np

import atedu.enums as enums
from atedu.calcfactor import *
from atedu.backtest import *
from atedu.realtrade import *
from atedu.api.bpfactor import *
from atedu.api.history import *
from atedu.api.orders import *
from atedu.api.regfuncs import *
from atedu.tframe.snapshot import *
from atedu.setting import set_setting, get_setting, get_version, get_support
from atedu.tframe import clear_cache
from atedu.tframe.snapshot import ContextBackReal as Context
from atedu.api import bpfactor as factors_api, history as history_api, orders as orders_api, regfuncs as reg_api
from atedu.api import fundamental as fundamental_api
# noinspection PyUnresolvedReferences
from atedu.api.fundamental import *
from atedu.api import riskmodel as riskmodel_api
# noinspection PyUnresolvedReferences
from atedu.api.riskmodel import *

__all__ = [
    'np',
    'pd',
    'set_setting',
    'get_setting',
    'get_version',
    'get_support',
    'clear_cache',
    'set_backtest',
    'run_factor',
    'run_backtest',
    'run_realtrade',
    *factors_api.__all__,
    *history_api.__all__,
    *orders_api.__all__,
    *reg_api.__all__,
    *fundamental_api.__all__,
    *riskmodel_api.__all__,
    'Context',
    'ContextFactor',
    'AccountSnapshot',
    'ExecutionSnapshot',
    'OrderSnapshot',
    'enums',
]

__version__ = get_version()
__author__ = 'www.bitpower.com.cn'
__mail__ = 'Contact@bitpower.com.con'
__telephone__ = '0755-86503293'
__address__ = '深圳市南山区粤海街道深圳湾科技生态园6栋413室'

# 不允许换行
pd.set_option('display.expand_frame_repr', False)
# 最大行数 500
pd.set_option('display.max_rows', 500)
# 最大允许列数 35
pd.set_option('display.max_columns', 35)
# 小数显示精度
pd.options.display.precision=5
# 绝对值小于0,001统一显示为0.0
pd.set_option('chop_threshold', 0.001)
# 对齐方式
pd.set_option('colheader_justify', 'right')

np.seterr(all='ignore')
