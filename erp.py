import requests
from os import environ as env
from bs4 import BeautifulSoup as bs
import sys
import re
import settings

ERP_HOMEPAGE_URL = 'https://erp.iitkgp.ernet.in/IIT_ERP3/welcome.jsp'
ERP_LOGIN_URL = 'https://erp.iitkgp.ernet.in/SSOAdministration/auth.htm'
ERP_SECRET_QUESTION_URL = 'https://erp.iitkgp.ernet.in/SSOAdministration/getSecurityQues.htm'
ERP_CDC_MODULE_URL = 'https://erp.iitkgp.ernet.in/IIT_ERP3/menulist.htm?module_id=26'
ERP_TPSTUDENT_URL = 'https://erp.iitkgp.ernet.in/TrainingPlacementSSO/TPStudent.jsp'


req_args = {
    'timeout': 20,
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
        'Referer':
        'https://erp.iitkgp.ernet.in/SSOAdministration/login.htm?sessionToken=595794DC220159D1CBD10DB69832EF7E.worker3',
    },
    'verify': False
}


def erp_login(func):

    def wrapped_func(*args, **kwargs):

        print "Started erp_login!"

        s = requests.Session()

        r = s.get(ERP_HOMEPAGE_URL, **req_args)
        soup = bs(r.text, 'html.parser')

        print "Length of the fetched HTML: " + str(len(str(r.text)))
        # print str(r.text)
        if soup.find(id='sessionToken'):
            sessionToken = soup.find(id='sessionToken').attrs['value']
        else:
            raise Exception("Could not get the sessionToken!")

        r = s.post(ERP_SECRET_QUESTION_URL, data={'user_id': env['ERP_USERNAME']},
                   **req_args)
        secret_question = r.text
        print "Secret question from the ERP: " + secret_question
        secret_answer = None
        for i in xrange(1, 4):
            print env['ERP_Q%d' % i]
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
            'requestedUrl': 'https://erp.iitkgp.ernet.in/IIT_ERP3/welcome.jsp',
        }


        r = s.post(ERP_LOGIN_URL, data=login_details,
                   **req_args)
        ssoToken = re.search(r'\?ssoToken=(.+)$',
                             r.history[1].headers['Location']).group(1) 

        print "ERP Login completed!"
        r = s.get("https://erp.iitkgp.ernet.in/IIT_ERP3/?%s" % ssoToken, **req_args)

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
                     **req_args)
        print "TNP Login completed!"
        func(session=session, sessionData=sessionData, *args, **kwargs)

    return wrapped_func
