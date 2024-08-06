import re
import time
import docker
import logging
from flask import request
import requests
import argparse
from datetime import datetime
from env import TOPIC_URL, EMAIL

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


def send_notification(logs):
    query_params = f"message={logs}"
    request_url = f"{TOPIC_URL}?{query_params}"

    headers = {
        "Priority": "5",
        "Tags": "warning,skull,rotating_light,mftp,error",
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

  check_error(latest_runtime_logs)


args = parse_args()
logging.basicConfig(level=logging.INFO)
while True:
  now = datetime.now()
  print(f"================ <<: {now.strftime('%H:%M:%S %d-%m-%Y')} :>> ================", flush=True)

  health_check()

  if args.cron:
    break

  print("[PAUSED FOR 2 MINUTES]", flush=True)
  time.sleep(120)