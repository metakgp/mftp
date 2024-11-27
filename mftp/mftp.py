import db
import env
import mail
import time
import ntfy
import notice
import company

import requests
import argparse
import iitkgp_erp_login.erp as erp
from datetime import datetime, timedelta

headers = {
  'timeout': '20',
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
}
session = requests.Session()

parser = argparse.ArgumentParser(description='One stop mailing solution for CDC NoticeBoard at IIT KGP')
parser.add_argument('--smtp', action="store_true", help='Use SMTP for sending the mails', required=False)
parser.add_argument('--gmail-api', action="store_true", help='Use GMAIL API for sending the mails', required=False)
parser.add_argument('--ntfy', action="store_true", help='Use NTFY to broadcast notifications', required=False)
parser.add_argument('--cron', action="store_true", help='Act as cronjob, bypass the continuous loop', required=False)
args = parser.parse_args()

# Initialize the last execution time for companies email logic
# Set it to run immediately on the first iteration
last_companies_email_time = datetime.now() - timedelta(hours=1)

while True:
  now = datetime.now()
  print(f"================ <<: {now.strftime('%H:%M:%S %d-%m-%Y')} :>> ================", flush=True)

  print('[ERP LOGIN]', flush=True)
  _, ssoToken = erp.login(headers, session, ERPCREDS=env, OTP_CHECK_INTERVAL=2, LOGGING=True, SESSION_STORAGE_FILE='.session')

  if now - last_companies_email_time >= timedelta(hours=1):
    companies = company.fetch(session, headers, ssoToken)
    open_not_applied_companies = company.filter(companies, "OPEN_N")
    companies_update_mail = mail.format_companies(session.cookies.get('ssoToken'), open_not_applied_companies)
    mail.send_companies(companies_update_mail, args.gmail_api, args.smtp)
    last_companies_email_time = now

  notice_db = db.NoticeDB(config={
    'uri': env.MONGO_URI,
    'db_name': env.MONGO_DATABASE
  }, collection_name=env.MONGO_COLLECTION)
  notice_db.connect()

  notices = notice.fetch(headers, session, ssoToken, notice_db)
  if notices:
    if args.ntfy:
      notifications = ntfy.format_notices(notices)
      if notifications:
          ntfy.send_notices(notifications, notice_db)
    else:
      mails = mail.format_notices(notices)
      if mails:
          mail.send_notices(mails, args.smtp, args.gmail_api, notice_db)
  else:
    print('[NO NEW NOTICES]', flush=True)

  if args.cron:
    break

  print('[PAUSED FOR 2 MINUTES]', flush=True)
  time.sleep(120)
