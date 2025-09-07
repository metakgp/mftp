import db
import env
import mail
import time
import ntfy
import notice
import company
import shortlist

import requests
import argparse
from datetime import datetime
import iitkgp_erp_login.erp as erp

import logging
import re

# mtfp doctor
def check_error(logs):
    error_words = ["error", "failed"]
    resp = None

    if any(re.search(word, logs, re.I) for word in error_words):
      logging.info(" ERROR(s) DETECTED!")

      try:
        resp = send_notification(logs)
      except Exception as e:
        logging.error(f" FAILED TO SEND NOTIFICATION : {str(e)}")
      finally:
        logging.info(f" NOTIFICATION STATUS : {resp}")
    else:
      logging.info(" NO ERROR(s) DETECTED!")

def send_notification(logs):
    query_params = f"message={logs}"
    request_url = f"{env.TOPIC_URL}?{query_params}"

    headers = {
        "Priority": "5",
        "Tags": "warning,skull,rotating_light,mftp,error",
        "Title": "MFTP encountered an error",
        "Markdown": "yes"
    }

    print(query_params)

    if env.EMAIL:
      headers["Email"] = env.EMAIL

    response = requests.put(request_url, headers=headers)
    return response.status_code

# mftp

headers = {
    "timeout": "20",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36",
}
session = requests.Session()

parser = argparse.ArgumentParser(
    description="One stop mailing solution for CDC NoticeBoard at IIT KGP"
)
parser.add_argument(
    "--smtp", action="store_true", help="Use SMTP for sending the mails", required=False
)
parser.add_argument(
    "--gmail-api",
    action="store_true",
    help="Use GMAIL API for sending the mails",
    required=False,
)
parser.add_argument(
    "--ntfy",
    action="store_true",
    help="Use NTFY to broadcast notifications",
    required=False,
)
parser.add_argument(
    "--cron",
    action="store_true",
    help="Act as cronjob, bypass the continuous loop",
    required=False,
)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)

while True:
    now = datetime.now()
    print(
        f"================ <<: {now.strftime('%H:%M:%S %d-%m-%Y')} :>> ================",
        flush=True,
    )

    runtime_logs = []

    try:
        print("[ERP LOGIN]", flush=True)
        _, ssoToken = erp.login(
            headers,
            session,
            ERPCREDS=env,
            OTP_CHECK_INTERVAL=2,
            LOGGING=True,
            SESSION_STORAGE_FILE=".session",
        )

        if env.COMPANY_NOTIFIER:
            if args.gmail_api or args.smtp:
                _, new, modified = company.fetch(session, headers, ssoToken)

                filtered = []
                if new + modified:
                    filtered = company.filter(new + modified, "OPEN_N")
                    if filtered:
                        latest_ssoToken = session.cookies.get("ssoToken")
                        companies_mail = mail.format_companies(
                            latest_ssoToken, filtered
                        )
                        mail.send_companies(companies_mail, args.gmail_api, args.smtp)
                else:
                    print("[NO NEW COMPANIES]")

        notice_db = db.NoticeDB(
            config={"uri": env.MONGO_URI, "db_name": env.MONGO_DATABASE},
            collection_name=env.MONGO_COLLECTION,
        )
        notice_db.connect()

        notices = notice.fetch(headers, session, ssoToken, notice_db)
        if notices:
            if args.ntfy:
                notifications = ntfy.format_notices(notices)
                if notifications:
                    ntfy.send_notices(notifications, notice_db)
            else:
                if env.SHORTLIST_NOTIFIER:
                    shortlists = shortlist.search(notices)
                    if shortlists:
                        shortlists_mails = mail.format_shortlists(shortlists)
                        if shortlists_mails:
                            mail.send_shortlists(shortlists_mails, args.gmail_api, args.ntfy)
                mails = mail.format_notices(notices)
                if mails:
                    mail.send_notices(mails, args.smtp, args.gmail_api, notice_db)
        else:
            print("[NO NEW NOTICES]", flush=True)

    except Exception as e:
            runtime_logs.append(str(e))

    check_error("\n".join(runtime_logs))
    if args.cron:
        break

    print("[PAUSED FOR 2 MINUTES]", flush=True)
    time.sleep(120)
