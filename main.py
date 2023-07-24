import env
import mail
import notice
import requests
import iitkgp_erp_login.erp as erp

headers = {
    'timeout': '20',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
}
session = requests.Session()

if not erp.session_alive(session):
    print ('>> [LOGGING IN]')
    _, ssoToken = erp.login(headers, session, ERPCREDS=env, OTP_CHECK_INTERVAL=2, LOGGING=True, SESSION_STORAGE_FILE='.session')
else:
    print(">> [PREVIOUS SESSION]")
    _, ssoToken = erp.get_tokens_from_file('.session')
    
try:
    notices = notice.fetch(headers, session, ssoToken)
    print ('>> [FETCHED NOTICES]')
except Exception as e:
    raise e
    

try:
    mails = mail.format(notices)
    print ('>> [FORMATTED MAIL]')
except Exception as e:
    raise e

try:
    mail.send(mails)
    print ('>> [SENT MAILS]')
except Exception as e:
    raise e
