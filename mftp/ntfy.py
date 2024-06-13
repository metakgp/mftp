import re
import logging
import requests
from bs4 import BeautifulSoup as bs
from endpoints import NOTICE_CONTENT_URL
from notice import update_lsni, has_idx_mutated
from env import NTFY_BASE_URL, NTFY_TOPIC, NTFY_TOPIC_ICON

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
            body, links = parseLinks(data, id_)
        except Exception as e:
            logging.error(f" Failed to parse notification body ~ {str(e)}")

        # NTFY specific features
        priority = ntfy_priority(subject=notice['Subject'])
        emoji = ntfy_emoji(subject=notifications['Subject'])

        # TODO: Handling attachment
        try:
            attachment = parseAttachment(session, year, id_)
        except Exception as e:
            logging.error(f" Failed to parse mail attachment ~ {str(e)}")

        if len(attachment) != 0:
            # Logic to add attachment stuff
            pass

        notifications.append({
            "Title":  f"#{id_} | {notice['Type']} | {notice['Subject']} | {notice['Company']}",
            "Body": body,
            "Tags": f"{emoji}, {notice['Type']}, {notice['Subject']}, {notice['Company']}",
            "Priority": priority,
            "Links": links
        })
  
    return notifications

def send(notifications, lsnif, notices):
    if notifications:
        print(f"[SENDING NOTIFICATIONS]", flush=True)

        for i, notification in enumerate(notifications, 1):
            if has_idx_mutated(lsnif, notices, i): break

            try:
                requests.post(f"{NTFY_BASE_URL}/${NTFY_TOPIC}",
                    data=notification["Body"],
                    headers={
                                "Title": notification["Title"],
                                "Tags": notification["Tags"],
                                "Priority": notification["Priority"],
                                "Icon": NTFY_TOPIC_ICON,
                                "Action": notification["Links"]
                    }
                )
                # TODO: Handle repsone
                update_lsni(lsnif, notices, i)
                logging.info(f" [NOTIFICATION SENT] ~ {notification['Title']}")
            except Exception as e:
                logging.error(f" Failed to send notification: {notification['Title']} ~ {str(e)}")

def parseBody(notice, session, year, id_):
    content = session.get(NOTICE_CONTENT_URL.format(year, id_))
    content_html = bs(content.text, 'html.parser')
    content_html_div = bs.find_all(content_html, 'div', {'id': 'printableArea'})[0]

    body = ''
    for br in content_html_div.find_all('br'):
        body = body + br.next_sibling.strip() + '\n'

    body = body + notice['Time']

    return body

def parseLinks(data, id_):
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
