import env
import mail
import time
import notice
import requests
import argparse
from datetime import datetime
import iitkgp_erp_login.erp as erp

lsnif = ".lsnif"
headers = {
    'timeout': '20',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
}
session = requests.Session()

parser = argparse.ArgumentParser(description='One stop mailing solution for CDC NoticeBoard at IIT KGP')
parser.add_argument('--smtp', action="store_true", help='Use SMTP for sending the mails', required=False)
parser.add_argument('--gmail-api', action="store_true", help='Use GMAIL API for sending the mails', required=False)
args = parser.parse_args()

print(f"================ <<: {datetime.now()} :>> ================", flush=True)
print('[ERP LOGIN]', flush=True)
_, ssoToken = erp.login(headers, session, ERPCREDS=env, OTP_CHECK_INTERVAL=2, LOGGING=True, SESSION_STORAGE_FILE='.session')
     
notices = notice.fetch(headers, session, ssoToken, lsnif)
mails = mail.format_notice(notices, session)
mail.send(mails, args.smtp, args.gmail_api, lsnif, notices)
    
