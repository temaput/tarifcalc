"""getting info about zones from info.russianpost.ru"""

import logging
log = logging.getLogger(__name__)

from os.path import join, exists
from os import makedirs

INDEXFIELD = 'index'
RATEFIELD = 'ratezone'
URL = 'http://vinfo.russianpost.ru/database/ops.html'
OBSOLETE = 30
DBPATH = ''
TMPPATH = ''
NOTFOUNDZONE = 3
maintenanceRunning = False

def parseDBF(dbffile):
    """parse dbf with ratezones return dict"""
    from dbf import Table, DbfError, FieldMissingError
    import shelve
    try:
        t = Table(dbffile)
        t.open()
    except DbfError:
        log.error('Cant open dbf file %s', dbffile)
        return None
    zones = {}
    for record in t:
        try:
            zones[str(record[INDEXFIELD])] = record[RATEFIELD]
        except FieldMissingError:
            log.error('Wrong fieldnames in dbf file %s', dbffile)
            return None
    return zones

def extractDBF(zipfile):
    """extracts dbf file from zip and returns its path"""
    from zipfile import is_zipfile, ZipFile
    if not is_zipfile(zipfile):
        log.error('Bad zipfile %s', zipfile)
        return None
    z = ZipFile(zipfile)
    for fn in z.namelist():
        if 'DBF' == fn.upper()[-3:]:
            return z.extract(fn, TMPPATH)
    log.error('No dbf files found in zipfile %s', zipfile)

def getLinks(url):
    """connects to the given url, returns all links"""
    from UserList import UserList
    try:
        from HTMLParser import HTMLParser
        from urllib2 import urlopen, HTTPError
    except ImportError:
        from html.parser import HTMLParser
        from urllib.request import urlopen, HTTPError

    class LinksGetter(HTMLParser):
        def reset(self):
            HTMLParser.reset(self)
            self.links = []
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                for name, value in attrs:
                    if name == 'href':
                        self.links.append(value)
    try:
        u = urlopen(url)
    except HTTPError as e:
        log.error("There was an error %s connecting to %s", e.code, url)
        return

    data = u.read()
    # charset = u.info().getparam('charset')
    #charset = u.info().get_content_charset()
    parser = LinksGetter()
    # parser.feed(data.decode(charset))
    parser.feed(data)
    parser.close()
    log.debug("Parsed %s and found %s links", url, len(parser.links))
    return parser.links

def downloadZIP(links):
    """filters and reverse-sort linklist, download the latest zip
    save it in TMPPATH, return its path"""
    try:
        from urllib import urlretrieve
    except ImportError:
        from urllib.request import urlretrieve
    from urlparse import urljoin
    if TMPPATH and not exists(TMPPATH):
        makedirs(TMPPATH)
    log.debug("links are: %s", links)
    for link in sorted(links,
            key = lambda x: x[-6:-4],
            reverse = True):
        if 'ZIP' == link.upper()[-3:]:
            fn, heading = urlretrieve(
                    urljoin(URL, link), join(TMPPATH, 'tmp.zip'))
            if heading['content-type'] == 'application/zip':
                log.debug("Downloaded zip %s", link)
                return fn

def checkObsolete(dbpath):
    """check if zones.db is obsolete"""
    import os
    from datetime import datetime
    if not os.path.exists(dbpath):
        log.debug("Zones db is obsolete")
        return True
    created = datetime.fromtimestamp(os.stat(dbpath).st_mtime)
    delta = datetime.today() - created
    if delta.days > OBSOLETE:
        log.debug("Zones db is obsolete")
        return True
    log.debug("Zones db is uptodate")
    return False

def maintenance():
    """Check if need to update zones info, get and save new db if needed"""
    global maintenanceRunning
    if maintenanceRunning:
        log.info("Maintenance is already running, exiting...")
        return
    dbfile = join(DBPATH, 'zonesdb')
    if DBPATH and not exists(DBPATH):
        log.warning("zonesdb path dir does not exist, creating new")
        makedirs(DBPATH)
    if checkObsolete(dbfile):
        maintenanceRunning = True
        log.info("Zones db is obsolete, starting maintenance")
        zones = None
        try:
            zones = parseDBF(extractDBF(downloadZIP(getLinks(URL))))
        except:
            import sys
            log.error("There was an unhandled error while maintaining"
                    " zones db %s", sys.exc_info()[0])
        if zones is not None:
            import shelve
            try:
                zonesdb = shelve.open(dbfile)
                zonesdb.update(zones)
                log.debug("Saved zones db as %s", dbfile)
            except IOError as e:
                log.error("Error trying to save zones db: %s", e)
            finally:
                zonesdb.close()
        else:
            log.warning("No zones info was obtained")
        maintenanceRunning = False
        log.info("Maintenance complete")

def acquireZoneByIndex(postalIndex):
    import shelve
    from anydbm import error as DBMError
    from threading import Thread

    t = Thread(name='maintenance', target=maintenance)
    t.start()

    zones = None
    from os import path
    try:
        zones = shelve.open(join(DBPATH, 'zonesdb'), flag='r')
        if postalIndex in zones:
            return zones[postalIndex]
        else:
            log.warning("Zone not found for index %s", postalIndex)
            return NOTFOUNDZONE  # index not found return middle zone
    except DBMError:
        log.warning("Error opening zones db")
        return NOTFOUNDZONE
    finally:
        if zones is not None:
            zones.close()

__all__ = ('acquireZoneByIndex',)
