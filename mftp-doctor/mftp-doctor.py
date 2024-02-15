import re
import time
import docker
import logging
import requests
import argparse

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
    delim = " ================"
    parts = logs.split(delim)
    return parts[-1].strip()


def check_error(logs):
    error_words = ["error", "failed"]

    if any(re.search(word, logs, re.I) for word in error_words):
      logging.info(" ERROR(s) DETECTED!")

      try: 
        resp = send_notification("https://ntfy.sh", "proffapt-mftp", logs)
      except Exception as e:
        logging.error(f" FAILED TO SEND NOTIFICATION : {str(e)}")
      finally:
        logging.info(f" NOTIFICATION STATUS : {resp}")
    else:
      logging.info(" NO ERROR(s) DETECTED!")


def send_notification(ntfy_server_url, topic, logs):
    topic_url = f"{ntfy_server_url}/{topic}"

    headers = {
        "Priority": "5",
        "Tags": "warning,skull,rotating_light,mftp,error",
        "Title": "MFTP encountered an error",
        "Markdown": "yes",
        # "Email": "proffapt@gmail.com",
    }

    response = requests.post(topic_url, headers=headers,
                             data=logs)
    return response.status_code


def parse_args():
  parser = argparse.ArgumentParser(description='Doctor aka Health Checkup Service for MFTP - One stop mailing solution for CDC NoticeBoard at IIT KGP')
  parser.add_argument('--cron', action="store_true", help='Act as cronjob, bypass the continuous loop', required=False)
  return parser.parse_args()


def health_check():
  logs = get_logs()
  latest_runtime_logs = parse_latest_runtime_logs(logs)
  logging.info(f" [LATEST RUNTIME LOGS] \n\n=============\n{latest_runtime_logs}\n=============\n")
  check_error(latest_runtime_logs)


args = parse_args()
logging.basicConfig(level=logging.INFO)
while True:
  health_check()

  if args.cron:
    break

  logging.info(" [PAUSED FOR 2 MINUTES]")
  time.sleep(120)