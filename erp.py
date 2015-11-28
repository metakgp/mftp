import requests
from os import environ as env
from bs4 import BeautifulSoup as bs, CData
import sys
import re
from pymongo import MongoClient
mc = MongoClient(env['MONGOLAB_URI'])

import hooks

def check_companies():

    ERP_HOMEPAGE_URL = 'https://erp.iitkgp.ernet.in/IIT_ERP2/welcome.jsp'
    ERP_LOGIN_URL = 'https://erp.iitkgp.ernet.in/SSOAdministration/auth.htm'
    ERP_SECRET_QUESTION_URL = 'https://erp.iitkgp.ernet.in/SSOAdministration/getSecurityQues.htm'
    ERP_CDC_MODULE_URL = 'https://erp.iitkgp.ernet.in/IIT_ERP2/welcome.jsp?module_id=26&menu_id=11&delegated_by=&parent_menu_id=10'
    ERP_TPSTUDENT_URL = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/TPStudent.jsp'
    ERP_COMPANIES_URL = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/ERPMonitoring.htm?action=fetchData&jqqueryid=37&_search=false&nd=1448725351715&rows=20&page=1&sidx=&sord=asc&totalrows=50'

    s = requests.Session()

    r = s.get(ERP_HOMEPAGE_URL)
    soup = bs(r.text, 'html.parser')
    sessionToken = soup.find_all(id='sessionToken')[0].attrs['value']

    r = s.post(ERP_SECRET_QUESTION_URL, data={'user_id': env['ERP_USERNAME']})
    secret_question = r.text
    secret_answer = None
    for i in xrange(1, 4):
        if env['ERP_Q%d' % i] == secret_question:
            secret_answer = env['ERP_A%d' % i]
            break

    if secret_answer is None:
        print 'No secret question matched:', secret_question
        sys.exit(1)

    login_details = {
        'user_id': env['ERP_USERNAME'],
        'password': env['ERP_PASSWORD'],
        'answer': secret_answer,
        'sessionToken': sessionToken,
        'requestedUrl': 'https://erp.iitkgp.ernet.in/IIT_ERP2/welcome.jsp',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
        'Referer': 'https://erp.iitkgp.ernet.in/SSOAdministration/login.htm?sessionToken=595794DC220159D1CBD10DB69832EF7E.worker3&requestedUrl=https://erp.iitkgp.ernet.in/IIT_ERP2/welcome.jsp',
    }

    r = s.post(ERP_LOGIN_URL, headers=headers, data=login_details)
    ssoToken = re.search(r'\?ssoToken=(.+)$',
                         r.history[1].headers['Location']).group(1)

    r = s.post(ERP_TPSTUDENT_URL, headers=headers,
               data=dict(ssoToken=ssoToken, menu_id=11, module_id=26))

    headers['Referer'] = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/TPStudent.jsp'
    headers['Accept'] = 'application/xml, text/xml, */*; q=0.01'
    r = s.get(ERP_COMPANIES_URL, headers=headers)

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

    companies_coll = mc.get_default_database().companies

    different_companies = []
    print 'Checking ', len(companies), 'companies'
    for company in companies:
        db_companies = companies_coll.find({'name': company['name']})
        found = False
        for db_company in db_companies:
            for k in company.keys():
                if k not in db_company or db_company[k] != company[k]:
                    break
            else:
                found = True
        if found is False:
            different_companies.append(company)
            companies_coll.insert_one(company)

    print 'Different companies:', different_companies
    if len(different_companies) > 0:
        hooks.companies_updated(different_companies)
