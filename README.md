estimate russian post delivery charges
======================================

for now works only for Moscow as sending point
can estimate delivery charges for parcel and letterpackage

invocation
----------
tarifcalc.calc(request=None, config=None) -> respond

request
-------
dict(
    From='101000' #Moscow
    To='000000' # Postal code where to send
    Weight=20000 # weight in gramms (20 kg max)
    Valuation=1000.00 # price of parcel for insurance calculation
    )

config
------
dict that contains all the prices, look at tarifconfig.py
may also contain special key 'zonesdbcfg' which supposed to be the dict itself
with keys 'DBPATH' and 'TMPPATH' to store zonesdb wich holds all info about
russian post zones (obtained by getzones.py from info.russianpost.ru)
