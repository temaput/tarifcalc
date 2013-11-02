#! /bin/env python2
#set encoding=utf-8

from UserDict import UserDict
from decimal import Decimal

from collections import namedtuple


ZonesTuple = namedtuple("ZonesTuple", "zone1, zone2, zone3, zone4, zone5")

D = lambda _float: Decimal(str(_float))
class ZonesTupleWrapper(object):
    def __init__(self, ztuple):
        self.data = ZonesTuple(*(D(price) for price in ztuple))
    def __getitem__(self, index):
        return self.data[index - 1]
    def __getattr__(self, attr):
        return getattr(self.data, attr)
    def __repr__(self):
        return self.data.__repr__()

zonestuple = lambda *ztuple: ZonesTupleWrapper(ztuple)


DEFAULTS = dict(
    # бандероль
    letterpacket = dict(
        name = u'Бандероль',
        main_charge = zonestuple(46.61, 59.35, 67.14, 78.47, 86.14),
        extra_charge = zonestuple(46.61, 59.35, 67.14, 78.47, 86.14),
        extrastep_threshold = D(500),
        maximum_threshold = D(2000),
        airmail_charge = D(82.60),
        airmail_reloading_charge = D(26.79),
        # плата за ценность (4 коп за рубль)
        insurance_rate = D(0.04)


    ),
    # посылка
    parcel = dict(
        name = u'Посылка',
        main_charge = zonestuple(138.80, 140.70, 146.40, 178.30, 199),
        extra_charge = zonestuple(12, 13.90, 20.30, 29.20, 33.7),
        heavyweight_rate = D(1.3),
        oversized_rate = D(1.3),
        airmail_charge = D(275.1),
        airmail_heavyweight_charge = D(82.6),
        airmail_oversized_charge = D(82.6),
        insurance_rate = D(0.04),
        extrastep_threshold = D(500),
        heavy_threshold = D(10000),
        maximum_threshold = D(20000)
        )
    )



class TarifConfig(UserDict): 
    def __init__(self, settings = None):
        UserDict.__init__(self, DEFAULTS)
        if settings is not None:
            if 'zonesdbcfg' in settings:
                import getzones
                getzones.__dict__.update(settings.pop('zonesdbcfg'))
            self.data.update(settings)
