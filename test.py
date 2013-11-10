#! /bin/env python2
# set encoding=utf-8
import unittest

import logging

logging.basicConfig(
        format = "%(name)s:%(levelname)s:\t%(message)s",
        level=logging.INFO)

from tarifcalc import tarifcalc



class NoInputTest(unittest.TestCase):

    def testSimple(self):
        result = tarifcalc.calc()()
        self.assertEqual(float(result), 118.7)

    def testParcel(self):
        result = tarifcalc.calc().parcel 
        self.assertEqual(float(result['amount']), 154.6)
        calc = result['calculation']
        self.assertEqual(calc.Name, u"Посылка")
        self.assertEqual(calc.Quantity, 1)
        self.assertEqual(calc.Insurance, 0)

    def testPacket(self):
        result = tarifcalc.calc().letterpacket 
        self.assertEqual(float(result['amount']), 118.7)
        calc = result['calculation']
        self.assertEqual(calc.Name, u"Бандероль")
        self.assertEqual(calc.Quantity, 1)
        self.assertEqual(calc.Insurance, 0)

request1 = dict(
        From = '101000',
        To = '394075',
        Weight = 3100,
        Valuation = 1500,
        )
request2 = dict(
        From = '101000',
        To = '101000',
        Weight = 4321,
        Valuation = 1477.8
        )

class GoodInputTest(unittest.TestCase):

    def testSimple(self):
        result = tarifcalc.calc(request1)()
        self.assertEqual(float(result), 270.8)

    def testParcel(self):
        result = tarifcalc.calc(request1).parcel 
        self.assertEqual(float(result['amount']), 210.8)
        calc = result['calculation']
        self.assertEqual(calc.Name, u"Посылка")
        self.assertEqual(calc.Quantity, 1)
        self.assertEqual(float(calc.Insurance), 60.0)
        self.assertEqual(float(calc.Total), 270.8)

    def testPacket(self):
        result = tarifcalc.calc(request1).letterpacket 
        self.assertEqual(float(result['amount']), 326.27)
        calc = result['calculation']
        self.assertEqual(calc.Name, u"Бандероль")
        self.assertEqual(calc.Quantity, 2)
        self.assertEqual(float(calc.Insurance), 60.0)
        self.assertEqual(float(calc.Total), 386.27)


class SameCityTest(unittest.TestCase):

    def testSimple(self):
        result = tarifcalc.calc(request2)()
        self.assertEqual(float(result), 293.91)

    def testParcel(self):
        result = tarifcalc.calc(request2).parcel 
        self.assertEqual(float(result['amount']), 234.80)
        calc = result['calculation']
        self.assertEqual(calc.Name, u"Посылка")
        self.assertEqual(calc.Quantity, 1)
        self.assertEqual(float(calc.Insurance), 59.11)
        self.assertEqual(float(calc.Total), 293.91)

    def testPacket(self):
        result = tarifcalc.calc(request2).letterpacket 
        self.assertEqual(float(result['amount']), 419.49)
        calc = result['calculation']
        self.assertEqual(calc.Name, u"Бандероль")
        self.assertEqual(calc.Quantity, 3)
        self.assertEqual(float(calc.Insurance), 59.11)
        self.assertEqual(float(calc.Total), 478.6)

class BadInputTest(unittest.TestCase):

    def testAutoConversion(self):
        result = tarifcalc.calc(dict(
            To = 650000, 
            Weight = 400,
            Valuation = 177.8,
            date = '14.11.2013'))()
        self.assertEqual(float(result), 74.25)

    def testBadRequest(self):

        BadTarifRequest = tarifcalc.BadTarifRequest
        self.assertRaises(BadTarifRequest, tarifcalc.calc, dict(
                    Weight = '12dФ.3'))

        self.assertRaises(BadTarifRequest, tarifcalc.calc, dict(
                    Weight = 0))
                    
        self.assertRaises(BadTarifRequest, tarifcalc.calc, dict(
                    Valuation = -12.3))

        self.assertRaises(BadTarifRequest, tarifcalc.calc, dict(
                    To = '1233214'))

        self.assertRaises(BadTarifRequest, tarifcalc.calc, dict(
                    To = '123ы14'))

class OfflineTest(unittest.TestCase): pass


class CustomizationTest(unittest.TestCase):

    def testCustomZonesDBLocation(self):
        from tarifcalc import getzones
        from os.path import expanduser, exists, join
        from os import remove
        getzones.DBPATH = expanduser('~/doc')
        getzones.TMPPATH = expanduser('~/tmp')
        tmpfile = join(getzones.TMPPATH, 'tmp.zip')
        if exists(tmpfile):
            remove(tmpfile)
        dbfile = join(getzones.DBPATH, 'zonesdb')
        if exists(dbfile):
            remove(dbfile)
        tarifcalc.calc()
        import time
        time.sleep(40)
        self.assertTrue(exists(dbfile))
        result = tarifcalc.calc()()
        self.assertEqual(float(result), 118.7)
        getzones.DBPATH = ''
        getzones.TMPPATH = ''

    def testZonesDBLocationConfigure(self):
        from os.path import expanduser, exists, join
        from os import remove
        zonesdbcfg = dict(
            DBPATH = expanduser('~/doc'),
            TMPPATH = expanduser('~/tmp')
            )
        tmpfile = join(zonesdbcfg['TMPPATH'], 'tmp.zip')
        if exists(tmpfile):
            remove(tmpfile)
        dbfile = join(zonesdbcfg['DBPATH'], 'zonesdb')
        if exists(dbfile):
            remove(dbfile)
        tarifcalc.calc(config = {'zonesdbcfg': zonesdbcfg})
        import time
        time.sleep(40)
        self.assertTrue(exists(dbfile))
        result = tarifcalc.calc()()
        self.assertEqual(float(result), 118.7)
        from tarifcalc import getzones
        getzones.DBPATH = ''
        getzones.TMPPATH = ''

    def testZonesDBAbsentLocationConfigure(self):
        from os.path import expanduser, exists, join
        from tema.utils import removeany
        zonesdbcfg = dict(
            DBPATH = expanduser('~/.dbpath'),
            TMPPATH = expanduser('~/.zonestmp')
            )
        removeany(zonesdbcfg['DBPATH'])
        removeany(zonesdbcfg['TMPPATH'])
        tarifcalc.calc(config = {'zonesdbcfg': zonesdbcfg})
        import time
        time.sleep(40)
        dbfile = join(zonesdbcfg['DBPATH'], 'zonesdb')
        self.assertTrue(exists(dbfile))
        result = tarifcalc.calc()()
        self.assertEqual(float(result), 118.7)
        from tarifcalc import getzones
        getzones.DBPATH = ''
        getzones.TMPPATH = ''
        removeany(zonesdbcfg['DBPATH'])
        removeany(zonesdbcfg['TMPPATH'])

if __name__ == '__main__':
    unittest.main()
