from bs4 import BeautifulSoup as bs, CData
from pymongo import MongoClient
from os import environ as env
import re

from erp import erp_login, tnp_login, headers, timeout
import hooks

mc = MongoClient(env['MONGOLAB_URI'])

ERP_COMPANIES_URL = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/ERPMonitoring.htm?action=fetchData&jqqueryid=37&_search=false&nd=1448725351715&rows=20&page=1&sidx=&sord=asc&totalrows=50'
ERP_NOTICEBOARD_URL = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/Notice.jsp'
ERP_NOTICES_URL = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/ERPMonitoring.htm?action=fetchData&jqqueryid=54&_search=false&nd=1448884994803&rows=20&page=1&sidx=&sord=asc&totalrows=50'
ERP_ATTACHMENT_URL = 'https://erp.iitkgp.ernet.in/TrainingPlacement/TPJNFDescriptionShow?filepath='


@tnp_login
def check_notices(session, sessionData):
    r = session.get(ERP_NOTICEBOARD_URL, headers=headers, timeout=timeout)
    headers['Referer'] = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/Notice.jsp'
    headers['Accept'] = 'application/xml, text/xml, */*; q=0.01'
    r = session.get(ERP_NOTICES_URL, headers=headers, timeout=timeout)

    notices_list = bs(r.text, 'html.parser')
    notices = []
    for row in notices_list.find_all('row'):
        notice = {}

        cds = filter(lambda x: isinstance(x, CData), row.find_all(text=True))

        notice['subject'] = cds[2].string
        notice['company'] = cds[3].string

        a = bs(cds[4].string, 'html.parser').find_all('a')[0]
        notice['text'] = a.attrs['title']
        notice['time'] = cds[6].string

        a = bs(cds[7].string, 'html.parser').find_all('a')[0]
        if a.attrs['title'] == 'Download':
            onclick = a.attrs['onclick']
            m = re.search(r'TPNotice\("(.+)"\)', onclick)
            notice['attachment'] = ERP_ATTACHMENT_URL + m.group(1)

        notices.append(notice)
        print notice

    handle_notices_diff(notices)


def handle_notices_diff(notices):
    notices_coll = mc.get_default_database().notices

    different_notices = []
    print 'Checking ', len(notices), 'notices'
    for notice in notices:
        db_notice = notices_coll.find_one(notice)
        if db_notice is None:
            different_notices.append(notice)

    print 'Different notices: ', different_notices
    if len(different_notices) > 0:
        hooks.notices_updated(different_notices)
        notices_coll.insert(different_notices)


@tnp_login
def check_companies(session, sessionData):
    headers['Referer'] = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/TPStudent.jsp'
    headers['Accept'] = 'application/xml, text/xml, */*; q=0.01'
    r = session.get(ERP_COMPANIES_URL, headers=headers, timeout=timeout)

    companies_list = bs(r.text, 'html.parser')
    companies = []
    for row in companies_list.find_all('row')[:1]:
        company = {}
        cds = filter(lambda x: isinstance(x, CData), row.find_all(text=True))

        a = bs(cds[0].string, 'html.parser').find_all('a')[0]
        company['name'], company['name_link'] = a.attrs['title'], a.attrs['onclick']

        a = bs(cds[3].string, 'html.parser').find_all('a')[0]
        company['job'], company['job_link'] = a.attrs['title'], a.attrs['onclick']

        a = bs(cds[7].string, 'html.parser').find_all('a')[0]
        company['description_link'] = a.attrs['onclick']

        company['start_date'], company['end_date'] = cds[9], cds[10]
        companies.append(company)

    handle_companies_diff(companies)


def handle_companies_diff(companies):

    companies_coll = mc.get_default_database().companies

    different_companies = []
    print 'Checking ', len(companies), 'companies'
    for company in companies:
        db_company = companies_coll.find_one(company)
        if db_company is None:
            different_companies.append(company)

    print 'Different companies:', different_companies
    if len(different_companies) > 0:
        hooks.companies_updated(different_companies)
        companies_coll.insert(different_companies)
