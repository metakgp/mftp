import os
import re
import base64
import logging
import requests
from urllib.parse import quote
from env import NTFY_BASE_URL, NTFY_TOPICS, NTFY_TOPIC_ICON, NTFY_USER, NTFY_PASS, HEIMDALL_COOKIE


def ntfy_priority(subject):
    match subject:
        case 'Urgent':
            priority = "5"
        case _:
            priority = "3"
    return priority


def ntfy_emoji(subject):
    match subject:
        case 'Urgent':
            emoji = "exclamation"
        case 'CV Submission':
            emoji = "rotating_light"
        case 'Result':
            emoji = "newspaper"
        case 'Shortlist':
            emoji = "postbox"
        case 'Date extension':
            emoji = "date"
        case 'PPT/Workshop/Seminars etc':
            emoji = "briefcase"
        case 'Schedule':
            emoji = "calendar"
        case 'Re-schedule':
            emoji = "spiral_calendar"
        case _:
            emoji = ""
    return emoji


def format_notices(notices):
    print('[FORMATTING NOTIFICATIONS]', flush=True)

    formatted_notifs = []
    for notice in reversed(notices):
        id_ = notice['UID'].split('_')[0]

        try:
            data = parse_body(notice['BodyData'], notice['Time'])
            notice['Body'] = data
            notice.pop('BodyData', None)
            body, links = parse_links(data)
            body = body[:5000] + '...\n\n[NOTICE SIZE EXCEEDED, PLEASE CHECK NOTICEBOARD]\n' if len(body) > 5000 else body
            body += '''
--------------

⚠️ DISCLAIMER ⚠️

MFTP is unofficial. Not affiliated with CDC, ERP, or Placement Committee. Do not rely solely on MFTP for updates. MFTP-related issues cannot be used as arguments with official authorities.

--------------
            '''
        except Exception as e:
            logging.error(f" Failed to parse notification body ~ {str(e)}", exc_info=True)
            break

        # NTFY specific features
        priority = ntfy_priority(subject=notice['Subject'])
        emoji = ntfy_emoji(subject=notice['Subject'])

        notification = {
            "Title":  f"#{id_} | {notice['Type']} | {notice['Subject']} | {notice['Company']}".encode('latin-1', 'ignore').decode('latin-1'),
            "Body": body,
            "Tags": f"{emoji}, {notice['Type']}, {notice['Subject']}, {notice['Company']}".encode('latin-1', 'ignore').decode('latin-1'),
            "Priority": priority,
            "Links": links.encode('latin-1', 'ignore').decode('latin-1'),
            "Attachment":  f"{id_}-{notice['Type']}-{notice['Subject']}-{notice['Company']}.pdf".replace(' ', '_').replace('/', '_')
        }

        # NTFY TOPICS LIST: Based on filters
        notification["NTFY_TOPICS"] = filter_subscribers(notice, NTFY_TOPICS)

        if 'Attachment' in notice:
            file_name = notification['Attachment']
            if save_file(file_name, notice['Attachment']):
                notification['Attachment'] = file_name
            else:
                break
        else:
            notification['Attachment'] = None
        formatted_notifs.append({'formatted_notice': notification, 'original_notice': notice})
    return formatted_notifs


def send_notices(notifications, notice_db):
    print('[SENDING NOTIFICATIONS]', flush=True)

    for notif in notifications:
        notification = notif.get('formatted_notice')
        original_notice = notif['original_notice']

        notification_sent_to_all_subscribers = True

        ntfy_topics = notification['NTFY_TOPICS']
        latest_successful_subscribers = notice_db.get_successful_ntfy_subscribers(original_notice['UID'])
        if len(latest_successful_subscribers) != 0:
            ntfy_topics = [subscirber for subscirber in ntfy_topics if subscirber not in latest_successful_subscribers]

        for ntfy_topic in ntfy_topics:
            try:
                query_params = f"message={quote(notification['Body'])}"
                request_url = f"{NTFY_BASE_URL}/{ntfy_topic}?{query_params}"

                headers = {
                    "Title": notification["Title"],
                    "Tags": notification["Tags"],
                    "Priority": notification["Priority"],
                    "Icon": NTFY_TOPIC_ICON,
                    "Action": notification["Links"],
                    "Markdown": "false"
                }
                if NTFY_USER and NTFY_PASS:
                    headers['Authorization'] = f"Basic {str(base64.b64encode(bytes(NTFY_USER + ':' + NTFY_PASS, 'utf-8')), 'utf-8')}"

                cookies = {}
                if HEIMDALL_COOKIE:
                    cookies = {'heimdall': HEIMDALL_COOKIE}

                if notification['Attachment']:
                    headers['Filename'] = notification['Attachment']
                    response = requests.put(
                        request_url,
                        headers=headers,
                        data=open(notification['Attachment'], 'rb'),
                        cookies=cookies
                    )
                else:
                    response = requests.put(request_url, headers=headers, cookies=cookies)
            except Exception as e:
                logging.error(f" Failed to request NTFY SERVER: {notification['Title']} ~ {str(e)}")
                notification_sent_to_all_subscribers = False
                break

            if response.status_code == 200:
                logging.info(f" [NOTIFICATION SENT] ~ `{notification['Title'].split(' | ')[0]} -> {ntfy_topic}`")
                notice_db.add_successful_ntfy_subscriber(original_notice['UID'], ntfy_topic)
            else: 
                logging.error(f" Failed to send notification: `{notification['Title'].split(' | ')[0]} -> {ntfy_topic}` ~ {response.text}")
                notification_sent_to_all_subscribers = False
                break
        # Delete attachment files
        if notification['Attachment']:
            delete_file(notification['Attachment'])

        if notification_sent_to_all_subscribers:
            notice_db.delete_successful_ntfy_subscribers(original_notice['UID'])
            notice_db.save_notice(original_notice)
        else:
            break


# This feature doesn't make sense to implement for mails
# As 'Label' in e-mail can achieve the same thing without any efforts
# Thus this feature is specific to ntfy and resides here
def filter_subscribers(notice, subscribers):
    filtered_subscribers = []

    for subscriber in subscribers:
        filters = subscribers[subscriber]

        if len(filters) == 0:
            filtered_subscribers.append(subscriber)

        for filter in filters:
            filter_value = filters[filter]

            if notice[filter] == filter_value:
                filtered_subscribers.append(subscriber)

    return filtered_subscribers


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


def parse_body(body_data, time):
    body = ''
    for br in body_data.find_all('br'):
        body = body + str(br.next_sibling).strip() + '\n'

    body = body + time

    return body


def parse_links(data):
    body = data
    links = re.findall(r'(https?://[^\s]+)', data)
    action_template = "view, Link {}, {}"
    actions = ""

    for i, link in enumerate(links, 1):
        if i == 4:
            break
        elif i > 1:
            actions = actions + "; "

        body = body.replace(link, f'<LINK {i}>')
        template = action_template
        actions = actions + template.format(i, link)

    return body, actions
