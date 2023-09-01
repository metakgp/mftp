import env
import mail
import time
import notice
import requests
import argparse
from datetime import datetime
import iitkgp_erp_login.erp as erp

headers = {
    'timeout': '20',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
}
session = requests.Session()


def parse_args():
    parser = argparse.ArgumentParser(description='One stop mailing solution for CDC NoticeBoard at IIT KGP')
    parser.add_argument('--smtp', action="store_true", help='Use SMTP for sending the mails', required=False)
    parser.add_argument('--gmail-api', action="store_true", help='Use GMAIL API for sending the mails', required=False)
    return parser.parse_args()


args = parse_args()

while True:
    print(f"=============== <<: {datetime.now()} :>> ===============", flush=True)
    if not erp.session_alive(session):
        print ('>> [LOGGING IN]', flush=True)
        _, ssoToken = erp.login(headers, session, ERPCREDS=env, OTP_CHECK_INTERVAL=2, LOGGING=True, SESSION_STORAGE_FILE='.session')
    else:
        print(">> [PREVIOUS SESSION]", flush=True)
        _, ssoToken = erp.get_tokens_from_file('.session', log=True)
        
    try:
        notices, session = notice.fetch(headers, session, ssoToken)
        print ('>> [NOTICES FETCHED]', flush=True)
    except Exception as e:
        raise e
        
    try:
        notice.save(notices)
        print ('>> [SAVED NEW NOTICES]', flush=True)
    except Exception as e:
        raise e

    try:
        mails = mail.format_notice(notices, session)
        print ('>> [NOTICES FORMATTED]', flush=True)
    except Exception as e:
        raise e
        
    try:
        mail.send(mails, args.smtp, args.gmail_api)
        print ('>> [MAILS SENT]', flush=True)
    except Exception as e:
        raise e
    
    print(">> [PAUSED FOR 2 MINS]", flush=True)
    time.sleep(120) # Sleep for 2 minutes
