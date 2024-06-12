import requests
from bs4 import BeautifulSoup as bs
import logging
from notice import update_lsni
from endpoints import NOTICE_CONTENT_URL, ATTACHMENT_URL

def format_notice(notices, session):
  notifications=[]

  for notice in reversed(notices):
    id_, year = notice['UID'].split('_')

    try:
      data = parseBody(session, year, id_)
    except Exception as e:
      logging.error(f"Failed to parse notification body ~ {str(e)}")

    if notice['Subject'] == 'Urgent':
      priority="5"
    else:
      priority="4"

    notifications.append(
      {"Title":  f"#{id_} | {notice['Type']} | {notice['Subject']} | {notice['Company']}",
        "Data": data,
        "Tags": f"{notice['Type']}, {notice['Subject']}, {notice['Company']}",
        "Priority": priority})
  
  return notifications

def send(notifications, lsnif, notices):
  for i, notification in enumerate(notifications, 1): 
    try:
      requests.post("http://172.18.0.2:8000/mftp",
        data=notification["Data"],
        headers={ 
          "Title": notification["Title"],
          "Tags": notification["Tags"],
          "Priority": notification["Priority"],
          "Markdown": "yes"})
      update_lsni(lsnif, notices, i)
      print(f'Sent notification {notification["Title"]}')
    except Exception as e:
      logging.error(f"Failed to send notification to ntfy server ~ {str(e)}")  

def parseBody(session, year, id_):
  content = session.get(NOTICE_CONTENT_URL.format(year, id_))
  content_html = bs(content.text, 'html.parser')
  content_html_div = bs.find_all(content_html, 'div', {'id': 'printableArea'})[0]

  body = ''
  for br in content_html_div.find_all('br'):
    body = body + br.next_sibling.strip() + '\n'

  return str(body)
