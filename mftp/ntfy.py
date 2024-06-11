import requests
from bs4 import BeautifulSoup as bs
import logging
from notice import update_lsni
from endpoints import NOTICE_CONTENT_URL

def format_notice(notices, session):
  notifications=[]

  for notice in reversed(notices):
    id_, year = notice['UID'].split('_')
    try:
      data = parseBody(session, year, id_)
    except Exception as e:
      logging.error(f" Failed to parse notification body ~ {str(e)}")

    notifications.append(
      {"Title": f"{notice['Type']} : {notice['Company']} {notice['Subject']}", 
       "Data": data})
  
  return notifications

def send(notifications, lsnif, notices):
  for i, notification in enumerate(notifications, 1): 
    try:
      requests.post("http://172.18.0.2:8000/mftp", 
        data=notification["Data"],
        headers={ 
          "Title": notification["Title"],
          "Markdown": "yes"})
      update_lsni(lsnif, notices, i)
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
