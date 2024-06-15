import os
import re
import base64
import logging
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup as bs
from notice import update_lsni, has_idx_mutated
from endpoints import NOTICE_CONTENT_URL, ATTACHMENT_URL
from env import NTFY_BASE_URL, NTFY_TOPIC, NTFY_TOPIC_ICON, NTFY_USER, NTFY_PASS

def ntfy_priority(subject):
    match subject:
        case 'Urgent':
            priority="5"
        case _:
            priority="3"
    
    return priority

def ntfy_emoji(subject):
    match subject:
        case 'Urgent':
            emoji="exclamation"
        case 'CV Submission':
            emoji="rotating_light"
        case 'Result':
            emoji="newspaper"
        case 'Shortlist':
            emoji="postbox"
        case 'Date extension':
            emoji="date"
        case 'PPT/Workshop/Seminars etc':
            emoji="briefcase"
        case 'Schedule':
            emoji="calendar"
        case 'Re-schedule':
            emoji="spiral_calendar"
        case _:
            emoji=""
    
    return emoji

def format_notice(notices, session):
    if notices: print(f'[FORMATTING NOTIFICATIONS]', flush=True)

    notifications=[]
    for notice in reversed(notices):
        id_, year = notice['UID'].split('_')

        try:
            data = parseBody(notice, session, year, id_)
            body, links = parseLinks(data)
        except Exception as e:
            logging.error(f" Failed to parse notification body ~ {str(e)}")

        # NTFY specific features
        priority = ntfy_priority(subject=notice['Subject'])
        emoji = ntfy_emoji(subject=notice['Subject'])

        notification = {
            "Title":  f"#{id_} | {notice['Type']} | {notice['Subject']} | {notice['Company']}",
            "Body": body,
            "Tags": f"{emoji}, {notice['Type']}, {notice['Subject']}, {notice['Company']}",
            "Priority": priority,
            "Links": links,
            "Attachment":  f"{id_}-{notice['Type'].replace(' ', '_')}-{notice['Subject'].replace(' ', '_')}-{notice['Company'].replace(' ', '_')}.pdf"
        }

        try:
            attachment = parseAttachment(session, year, id_)
        except Exception as e:
            logging.error(f" Failed to parse mail attachment ~ {str(e)}")

        if len(attachment) != 0:
            file_name = notification['Attachment']
            if save_file(file_name, attachment): 
                notification['Attachment'] = file_name
            else: 
                break
        else: 
            notification['Attachment'] = None

        notifications.append(notification)
  
    return notifications

def send(notifications, lsnif, notices):
    if notifications:
        print(f"[SENDING NOTIFICATIONS] ~ {NTFY_BASE_URL}/{NTFY_TOPIC}", flush=True)

        for i, notification in enumerate(notifications, 1):
            if has_idx_mutated(lsnif, notices, i): break

            try:
                query_params = f"message={quote(notification['Body'])}"
                request_url = f"{NTFY_BASE_URL}/{NTFY_TOPIC}?{query_params}"

                headers={
                    "Title": notification["Title"],
                    "Tags": notification["Tags"],
                    "Priority": notification["Priority"],
                    "Icon": NTFY_TOPIC_ICON,
                    "Action": notification["Links"],
                    "Markdown": "true"
                }
                if NTFY_USER and NTFY_PASS:
                    headers['Authorization'] = f"Basic {str(base64.b64encode(bytes(NTFY_USER + ':' + NTFY_PASS, 'utf-8')), 'utf-8')}"

                if notification['Attachment']:
                    headers['Filename'] = notification['Attachment']
                    response = requests.put(
                        request_url, 
                        headers=headers,
                        data=open(notification['Attachment'], 'rb')
                    )
                else:
                    response = requests.put(request_url, headers=headers)

            except Exception as e:
                logging.error(f" Failed to request NTFY SERVER: {notification['Title']} ~ {str(e)}")
                break
            finally:
                if notification['Attachment'] and not delete_file(notification['Attachment']): break

            if response.status_code == 200:
                logging.info(f" [NOTIFICATION SENT] ~ {notification['Title']}")
                update_lsni(lsnif, notices, i)
            else: 
                logging.error(f" Failed to send notification: {notification['Title']} ~ {response.text}")
                break

def save_file(file_name: str, attachment):
    try:
        with open(file_name, 'wb') as file:
            file.write(attachment)

        logging.info(f" [PDF SAVED] For notice #{file_name.split('-')[0]} of length ~ {len(attachment)}")
        return True
    except Exception as e:
        logging.error(f" Failed to save attachment for notice #{file_name.split('-')[0]} ~ {str(e)}")
        return False

def delete_file(file_name):
    try:
        os.remove(file_name)
        logging.info(f" [PDF DELETED] ~ {file_name}")
        return True
    except Exception as e:
        logging.error(f" Failed to delete the pdf {file_name} ~ {str(e)}")
        return False

def parseAttachment(session, year, id_):
    stream = session.get(ATTACHMENT_URL.format(year, id_), stream=True)
    attachment = b''
    for chunk in stream.iter_content(4096):
        attachment += chunk
    
    return attachment

def parseBody(notice, session, year, id_):
    content = session.get(NOTICE_CONTENT_URL.format(year, id_))
    content_html = bs(content.text, 'html.parser')
    content_html_div = bs.find_all(content_html, 'div', {'id': 'printableArea'})[0]

    body = ''
    for br in content_html_div.find_all('br'):
        body = body + br.next_sibling.strip() + '\n'

    body = body + notice['Time']

    return body

def parseLinks(data):
    body = data
    links = re.findall(r'(https?://[^\s]+)', data)
    links = list(set(result.lower() for result in links))
    action_template = "view, Link {}, {}"
    actions = ""

    for i, link in enumerate(links, 1):
        if i == 4: break
        elif i > 1: actions = actions + "; "

        body = body.replace(link, f'<LINK {i}>')
        template = action_template
        actions = actions + template.format(i, link)

    return body, actions
