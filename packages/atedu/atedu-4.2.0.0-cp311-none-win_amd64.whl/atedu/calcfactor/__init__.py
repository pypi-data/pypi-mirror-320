# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 14:39:04 2018

@author: kunlin.l
"""

import numpy as np
import pandas as pd

import atedu.enums as enums
from atedu.setting import get_setting, get_support, set_setting, get_version
# noinspection PyUnresolvedReferences
from atedu.tframe.sysclsbase import smm
# noinspection PyUnresolvedReferences
from atedu.tframe.sysclsbase import gv
# noinspection PyUnresolvedReferences
from atedu.tframe.utils.utilcls import OrderedDotDict
from atedu.tframe.utils.argchecker import apply_rule, verify_that
from atedu.tframe import clear_cache
from atedu.tframe.snapshot import ContextFactor
from atedu.api import fundamental as fundamental_api
from atedu.api import riskmodel as riskmodel_api

# noinspection PyUnresolvedReferences
from atedu.api.bpfactor import *
# noinspection PyUnresolvedReferences
from atedu.api.history import *
# noinspection PyUnresolvedReferences
from atedu.api.regfuncs import *
from atedu.api import bpfactor as factors_api, history as history_api, regfuncs as reg_api
# noinspection PyUnresolvedReferences
from atedu.api.fundamental import *
# noinspection PyUnresolvedReferences
from atedu.api.riskmodel import *

from atedu.tframe.udefs import ONE_YEAR_AGO, ZERO_YEAR_AGO
from atedu.tframe.ufuncs import convert_str_or_datetime_to_int_date

__all__ = [
    'np',
    'pd',
    'enums',
    'set_setting',
    'get_setting',
    'get_support',
    'get_version',
    'clear_cache',
    'run_factor',
    'ContextFactor',
    'get_auto_value',
    *factors_api.__all__,
    *history_api.__all__,
    *reg_api.__all__,
    *fundamental_api.__all__,
    *riskmodel_api.__all__,
]


@smm.force_mode(gv.RUNMODE_CONSOLE)
@smm.force_phase(gv.RUMMODE_PHASE_DEFAULT)
@apply_rule(verify_that('factor_name').is_instance_of(str),
            verify_that('targets').is_instance_of(str),
            verify_that('begin_date').is_valid_date(),
            verify_that('end_date').is_valid_date(allow_empty_str=True),
            verify_that('fq').is_in((enums.FQ_BACKWARD,
                                     enums.FQ_FORWARD,
                                     enums.FQ_NA)))
def run_factor(factor_name='',
               file_path='.',
               targets='',
               begin_date=ONE_YEAR_AGO,
               end_date=ZERO_YEAR_AGO,
               fq=enums.FQ_NA):
    if isinstance(begin_date, str) and begin_date.strip() == '':
        begin_date = ONE_YEAR_AGO

    if isinstance(end_date, str) and end_date.strip() == '':
        end_date = ZERO_YEAR_AGO

    config, strategyInfo = OrderedDotDict(), OrderedDotDict()
    strategyInfo.fq = fq
    strategyInfo.factor_name = factor_name
    strategyInfo.begin_date = convert_str_or_datetime_to_int_date(begin_date)
    strategyInfo.end_date = convert_str_or_datetime_to_int_date(end_date)
    strategyInfo.targets = str.upper(targets)
    strategyInfo.strategy_path = file_path
    config.entry = strategyInfo
    config.entry_point = 'run_factor'

    from .main import main_run_factor
    return main_run_factor(dict(config))


@smm.force_phase(gv.RUMMODE_PHASE_CALC_FACTOR)
@apply_rule(verify_that('length').is_instance_of(int))
def get_auto_value(length=1):
    from ._calcfactor import _get_auto_value
    column_index = ['date', 'code', 'target_idx', 'value', ]
    auto_value_matrix = _get_auto_value(length)

    return pd.DataFrame(auto_value_matrix, columns=column_index)
