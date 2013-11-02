#! /bin/env python2
# set encoding=utf-8

import logging
log = logging.getLogger(__name__)

from decimal import Decimal
from decimal import InvalidOperation
D = lambda _float: Decimal(str(_float))
from decimal import ROUND_UP
from datetime import datetime
today = datetime.today

DEFAULTS = dict(
        From = '101000', # Москва
        To = '190000',  # Питер
        Weight = D(1000),  # Вес
        Valuation = D(0),  # Объявленная Стоимость отправки
        Date = today(),  # Дата расчета
        Country = 'RU'
        )

from UserDict import UserDict


from .tarifconfig import TarifConfig
from collections import namedtuple
from .getzones import acquireZoneByIndex

Calculation = namedtuple("Calculation", 
                        "Name, Quantity, Amount, Insurance, Total")
AdditionalFees = namedtuple("AdditionalFees", "AirMail, HeavyWeight, Oversize")
Limitation = namedtuple("Limitation", 
                    "Index, Since, Till, AirOnly, Forbidden, ReloadIndex")


class TarifResponse(UserDict):

    def __init__(self, request, config):
        UserDict.__init__(self, request)
        self.zone = acquireZoneByIndex(self.data['To'])
        self.config = config
        self.__calculation = dict()

    @property
    def parcel(self): 
        return dict(
                calculation = self.calculation('parcel'),
                amount = self.calculation('parcel').Amount,
                total = self.calculation('parcel').Total,
                additionalfees = self.detalization('parcel')
                )

    @property
    def letterpacket(self):
        return dict(
                calculation = self.calculation('letterpacket'),
                amount = self.calculation('letterpacket').Amount,
                total = self.calculation('letterpacket').Total,
                additionalfees = self.detalization('letterpacket')
                )

    def __call__(self):
        log.debug("selecting optimal price")
        log.debug("letterpacket total = %s", self.letterpacket['total'])
        log.debug("parcel total = %s", self.parcel['total'])

        return min(self.letterpacket['total'],
                self.parcel['total'])

    def __repr__(self):
        print u'Стоимость отправки: {}'.format(self())

    def detalization(self, parceltype): return None

    def calculation(self, parceltype):
        if parceltype in self.__calculation:
            return self.__calculation[parceltype]
        log.debug("calculating parcel type %s", parceltype)
        config = self.config[parceltype]
        weight = self.data['Weight']

        def calcamount(weight):
            # calculate amount of every parcel
            amount = config['main_charge'][self.zone]
            extraCount = D(weight / config['extrastep_threshold']
                    or weight).to_integral(rounding=ROUND_UP) - 1
            log.debug("extrasteps count = %s", extraCount)
            log.debug("extracharge  = %s", config['extra_charge'][self.zone])
            amount += config['extra_charge'][self.zone]*extraCount
            return amount

        log.debug("zone is %s, weight is %s", self.zone, weight)
        amount = D(0)
        maxamount = D(0)
        quant = 0
        while weight:
            if weight > config['maximum_threshold']:
                log.debug("total weight is more than max (%s)",
                        config['maximum_threshold'])
                if not maxamount:
                    maxamount = calcamount(config['maximum_threshold'])
                amount += maxamount
                weight -= config['maximum_threshold']
                quant += 1
            else:
                amount += calcamount(weight)
                quant += 1
                break

        insurance = self.data['Valuation'] * config['insurance_rate']
        insurance = insurance.quantize(D(0.01))
        amount = amount.quantize(D(0.01))
        log.debug("calculated amount is %s, insurance = %s", amount, insurance)
        total = amount + insurance

        return self.__calculation.setdefault(parceltype, Calculation(
                config['name'], quant, amount, insurance, total))
        
class BadTarifRequest(ValueError): pass
        
class TarifRequest(UserDict):

    def __init__(self, dct = None):
        UserDict.__init__(self, DEFAULTS)
        if dct:
            self.data.update(dct)
        self.check()

    def check(self):
        # here some data checking occurs (datatype)
        for key in ('Weight', 'Valuation'):
            try:
                self.data[key] = D(self.data[key])
            except InvalidOperation:
                raise BadTarifRequest, "Weight and Valuation should be numbers"
            if self.data[key] < 0:
                raise BadTarifRequest, "Weight and Valuation should be positive"
        if self.data['Weight'] == 0:
            raise BadTarifRequest, "Weight should not be 0"
        self.data['From'] = str(self.data['From'])
        self.data['To'] = str(self.data['To'])
        for i in (self.data['From'], self.data['To']):
            if not i.isalnum() or len(i) != 6:
                raise BadTarifRequest, "From and To should be 6 digits postal codes"
        if isinstance(self.data['Date'], datetime):
            return
        if isinstance(self.data['Date'], str):
            try:
                datetime.strptime(self.data['Date'], "%d.%m.%Y")
            except ValueError:
                log.warning("Bad date %s", self.data['date'])
                self.data['Date'] = today()



    
def calc(request = None, config = None):
    tarifrequest = TarifRequest(request)
    tarifconfig = TarifConfig(config)

    return TarifResponse(tarifrequest, tarifconfig)



