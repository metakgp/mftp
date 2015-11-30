import requests
from os import environ as env
from bs4 import BeautifulSoup as bs
import sys
import re
from functools import partial

ERP_HOMEPAGE_URL = 'https://erp.iitkgp.ernet.in/IIT_ERP2/welcome.jsp'
ERP_LOGIN_URL = 'https://erp.iitkgp.ernet.in/SSOAdministration/auth.htm'
ERP_SECRET_QUESTION_URL = 'https://erp.iitkgp.ernet.in/SSOAdministration/getSecurityQues.htm'
ERP_CDC_MODULE_URL = 'https://erp.iitkgp.ernet.in/IIT_ERP2/welcome.jsp?module_id=26&menu_id=11&delegated_by=&parent_menu_id=10'
ERP_TPSTUDENT_URL = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/TPStudent.jsp'


timeout = 20

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
    'Referer': 'https://erp.iitkgp.ernet.in/SSOAdministration/login.htm?sessionToken=595794DC220159D1CBD10DB69832EF7E.worker3&requestedUrl=https://erp.iitkgp.ernet.in/IIT_ERP2/welcome.jsp',
}


def erp_login(func):

    def wrapped_func(*args, **kwargs):

        print 'Running erp_login called with', func, args, kwargs

        s = requests.Session()

        r = s.get(ERP_HOMEPAGE_URL, timeout=timeout)
        soup = bs(r.text, 'html.parser')
        sessionToken = soup.find_all(id='sessionToken')[0].attrs['value']

        r = s.post(ERP_SECRET_QUESTION_URL, data={'user_id': env['ERP_USERNAME']},
                   timeout=timeout)
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

        r = s.post(ERP_LOGIN_URL, headers=headers, data=login_details,
                   timeout=timeout)
        ssoToken = re.search(r'\?ssoToken=(.+)$',
                             r.history[1].headers['Location']).group(1)

        func(session=s, sessionData={'ssoToken': ssoToken,
                                     'sessionToken': sessionToken},
             *args, **kwargs)

    return wrapped_func


def tnp_login(func):

    @erp_login
    def wrapped_func(session, sessionData, *args, **kwargs):

        ssoToken = sessionData['ssoToken']
        session.post(ERP_TPSTUDENT_URL,  # headers=headers,
                     data=dict(ssoToken=ssoToken, menu_id=11, module_id=26),
                     timeout=timeout)
        func(session=session, sessionData=sessionData, *args, **kwargs)

    return wrapped_func
