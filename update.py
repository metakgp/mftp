from bs4 import BeautifulSoup as bs, CData
from pymongo import MongoClient
from os import environ as env

from erp import erp_login, tnp_login, headers, timeout
import hooks

mc = MongoClient(env['MONGOLAB_URI'])


ERP_COMPANIES_URL = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/ERPMonitoring.htm?action=fetchData&jqqueryid=37&_search=false&nd=1448725351715&rows=20&page=1&sidx=&sord=asc&totalrows=50'


@tnp_login
def check_companies(session, sessionData):

    headers['Referer'] = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/TPStudent.jsp'
    headers['Accept'] = 'application/xml, text/xml, */*; q=0.01'
    r = session.get(ERP_COMPANIES_URL, headers=headers, timeout=timeout)

    companies_list = bs(r.text, 'html.parser')
    companies = []
    for row in companies_list.find_all('row'):
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
