from bs4 import BeautifulSoup as bs, CData
from pymongo import MongoClient
from os import environ as env
from sys import setrecursionlimit
import re
import hashlib
from copy import copy as shallow_copy

import settings

from erp import tnp_login, req_args
import hooks

# Checking all the notices is ideal, but too slow to do quickly, since
# we're fetching attachments. Instead, check enough notices that the
# likelihood of missing an update is low.
NUM_NOTICES_DIFFED = 50

# The new format of ERP is poorly formatted and hence 10000 recursion limit
# is required by BS4.
# TODO(#28): Look for a better solution
setrecursionlimit(10000)

mc = MongoClient(env['MONGODB_URI'])


ERP_COMPANIES_URL = 'https://erp.iitkgp.ac.in/TrainingPlacementSSO/ERPMonitoring.htm?action=fetchData&jqqueryid=37&_search=false&nd=1448725351715&rows=20&page=1&sidx=&sord=asc&totalrows=50'
ERP_NOTICEBOARD_URL = 'https://erp.iitkgp.ac.in/TrainingPlacementSSO/Notice.jsp'
ERP_NOTICES_URL = 'https://erp.iitkgp.ac.in/TrainingPlacementSSO/ERPMonitoring.htm?action=fetchData&jqqueryid=54&_search=false&nd=1448884994803&rows=20&page=1&sidx=&sord=asc&totalrows=50'
ERP_ATTACHMENT_URL = 'https://erp.iitkgp.ac.in/TrainingPlacementSSO/AdmFilePDF.htm?type=NOTICE&year={}&id={}'
ERP_NOTICE_CONTENT_URL = 'https://erp.iitkgp.ac.in/TrainingPlacementSSO/ShowContent.jsp?year=%s&id=%s'


@tnp_login
def check_notices(session, sessionData):
    r = session.get(ERP_NOTICEBOARD_URL, **req_args)
    r = session.get(ERP_NOTICES_URL, **req_args)

    print "ERP and TNP login completed!"

    notices_list = bs(r.text, 'html.parser')

    print "Total number of notices fetched: %d" % len(notices_list.find_all('row'))

    notices = []
    # Only check the first 50 notices
    for row in notices_list.find_all('row')[:NUM_NOTICES_DIFFED]:
        notice = {}

        cds = filter(lambda x: isinstance(x, CData), row.find_all(text=True))

        notice['subject'] = cds[2].string
        notice['company'] = cds[3].string

        a = bs(cds[4].string, 'html.parser').find_all('a')[0]
        try :
            m = re.search(r'ViewNotice\("(.+?)","(.+?)"\)', a.attrs['onclick'])
        except KeyError :
            print("Poorly formatted notice found")
            continue
        year, id_ = m.group(1), m.group(2)
        content = bs(session.get(ERP_NOTICE_CONTENT_URL % (year, id_)).text, 'html.parser')
        content_div = bs.find_all(content, 'div', {'id': 'printableArea'})[0]
        notice['text'] = content_div.decode_contents(formatter='html')
        notice['time'] = cds[6].string
        notice['uid'] = id_ + "_" + year

        a = bs(cds[7].string, 'html.parser').find_all('a')[0]
        if a.attrs['title'] == 'Download':
            notice['attachment_url'] = ERP_ATTACHMENT_URL.format(year, id_)
            r = session.get(notice['attachment_url'], stream=True)
            r.raw.decode_content = True
            hash_ = hashlib.md5()
            notice['attachment_raw'] = b""
            for chunk in r.iter_content(4096):
                notice['attachment_raw'] += chunk
                hash_.update(chunk)
            notice['attachment_md5'] = hash_.hexdigest()
            notice['uid'] += "_"+notice['attachment_md5']

        notices.append(notice)

    handle_notices_diff(notices)


def handle_notices_diff(notices):
    notices_coll = mc.get_default_database().notices

    different_notices = []
    print 'Checking ', len(notices), 'notices'
    for notice in notices:
        sanitised_notice = sanitise_notice_for_database(notice)
        notice_cpy = shallow_copy(sanitised_notice)
        try:
            del notice_cpy['uid']
        except KeyError:
            pass

        db_notice = notices_coll.find_one({'$or':[{'uid' : sanitised_notice['uid']}, notice_cpy]})
        if db_notice is None:
            different_notices.append(notice)


    print 'Different notices: ', [sanitise_notice_for_database(notice) for notice in different_notices]
    if len(different_notices) > 0:
        for notice in different_notices:
            sanitised_notice = sanitise_notice_for_database(notice)
            hooks.notices_updated([notice])
            notices_coll.insert_one(sanitised_notice)

def sanitise_notice_for_database(notice):
    sanitised_notice = shallow_copy(notice)

    try:
        del sanitised_notice['attachment_raw']
    except KeyError:
        pass

    return sanitised_notice
