import re
import time
import docker
import logging
import requests
import argparse
from datetime import datetime
from env import DOCTOR_TOPIC_URL, TOPIC_URL, EMAIL

def get_logs():
  client = docker.from_env()
  try:
    mftp = client.containers.get("mftp")
    logs = mftp.logs().decode('utf-8')
    return logs
  except Exception as e:
    logging.error(f" FAILED TO GET MFTP CONTAINR : {str(e)}")
    return ""


def parse_latest_runtime_logs(logs):
    delim = "================ <<:"
    parts = logs.split(delim)
    last_part_with_timestamp = parts[-1].strip()

    delim = " :>> ================"
    parts = last_part_with_timestamp.split(delim)
    if len(parts) == 2:
      timestamp = parts[0].strip()
      global last_notification_sent_time
      last_notification_sent_time = timestamp
      latest_runtime_logs = parts[1].strip()
    else:
      timestamp = "NULL"
      latest_runtime_logs = "NO PREVIOUS LOGS AVAILABLE"
    
    return timestamp, latest_runtime_logs


def check_error(logs):
    error_words = ["error", "failed"]

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

def check_downtime():
    downtime_threshold = 30

    if last_notification_sent_time == "NULL":
      logging.info(" LAST SENT TIME IS NULL, SKIPPING DOWNTIME CHECK")
      return

    try:
      last_time = datetime.strptime(last_notification_sent_time, '%H:%M:%S %d-%m-%Y')
      diff = (datetime.now() - last_time).total_seconds() / 60

      if diff > downtime_threshold:
        logging.info(f" DOWNTIME DETECTED (Last log was {diff:.2f} minutes ago)")

        try:
          body = f"DOWNTIME DETECTED.\n\nPlease check the CDC Noticeboard from your ERP account until MFTP is back online.\n"
          body += '''
--------------

⚠️ DISCLAIMER ⚠️

MFTP is unofficial. Not affiliated with CDC, ERP, or Placement Committee. Do not rely solely on MFTP for updates. MFTP-related issues cannot be used as arguments with official authorities.

--------------
            '''
          resp = send_notification(body, TOPIC_URL)
        except Exception as e:
          logging.error(f" FAILED TO SEND NOTIFICATION : {str(e)}")
        finally:
          logging.info(f" NOTIFICATION STATUS : {resp}")
      else:
        logging.info(" NO DOWNTIME DETECTED")
    except Exception as e:
      logging.error(f" FAILED TO CHECK DOWNTIME : {str(e)}")

def send_notification(logs, topic_url=DOCTOR_TOPIC_URL):
    query_params = f"message={logs}"
    request_url = f"{topic_url}?{query_params}"

    headers = {
        "Priority": "5",
        "Tags": "warning,mftp,error",
        "Title": "MFTP encountered an error",
        "Markdown": "yes"
    }

    if EMAIL:
      headers["Email"] = EMAIL

    response = requests.put(request_url, headers=headers)
    return response.status_code


def parse_args():
  parser = argparse.ArgumentParser(description='Doctor aka Health Checkup Service for MFTP - One stop mailing solution for CDC NoticeBoard at IIT KGP')
  parser.add_argument('--cron', action="store_true", help='Act as cronjob, bypass the continuous loop', required=False)
  return parser.parse_args()


def health_check():
  logs = get_logs()
  timestamp, latest_runtime_logs = parse_latest_runtime_logs(logs)

  delim = ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
  logging.info(f" [ LATEST RUNTIME LOGS | {timestamp} ] \n{delim}\n{latest_runtime_logs}\n{delim}")

  check_downtime()
  check_error(latest_runtime_logs)


args = parse_args()
logging.basicConfig(level=logging.INFO)
last_notification_sent_time = "NULL"

while True:
  now = datetime.now()
  print(f"================ <<: {now.strftime('%H:%M:%S %d-%m-%Y')} :>> ================", flush=True)

  health_check()

  if args.cron:
    break

  print("[PAUSED FOR 2 MINUTES]", flush=True)
  time.sleep(120)
