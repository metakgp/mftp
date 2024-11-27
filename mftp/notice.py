import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs
from endpoints import TPSTUDENT_URL, NOTICEBOARD_URL, NOTICES_URL, ATTACHMENT_URL, NOTICE_CONTENT_URL


LAST_NOTICES_CHECK_COUNT = 30

    
def fetch(headers, session, ssoToken, notice_db):
    print('[FETCHING NOTICES]', flush=True)
    try:
        r = session.post(TPSTUDENT_URL, data=dict(ssoToken=ssoToken, menu_id=11, module_id=26), headers=headers)
        r = session.get(NOTICEBOARD_URL, headers=headers)
        r = session.get(NOTICES_URL, headers=headers)
    except Exception as e:
        logging.error(f" Failed to navigate to Noticeboard ~ {str(e)}")
        return []

    try:
        soup = bs(r.text, features="xml")
        xml = soup.prettify().encode('utf-8')
        root = ET.fromstring(xml)
    except Exception as e:
        logging.error(f" Failed to extract data from Noticeboard ~ {str(e)}")
        return []

    latest_notices = []
    for i, row in enumerate(root.findall('row')):
        if i >= LAST_NOTICES_CHECK_COUNT:
            break

        id_ = row.find('cell[1]').text.strip()
        year = root.findall('row')[0].find('cell[8]').text.split('"')[1].strip()
        notice = {
            'UID': f'{id_}_{year}',
            'Time': row.find('cell[7]').text.strip(),
            'Type': row.find('cell[2]').text.strip(),
            'Subject': row.find('cell[3]').text.strip(),
            'Company': row.find('cell[4]').text.strip(),
        }

        # Handling Body
        try:
            body_data = parse_body_data(session, year, id_)
            notice['BodyData'] = body_data
        except Exception as e:
            logging.error(f" Failed to parse mail body ~ {str(e)}")
            break

        # Handling attachment
        try:
            attachment = parse_attachment(session, year, id_)
            if attachment:
                notice['Attachment'] = attachment
        except Exception as e:
            logging.error(f" Failed to parse mail attachment ~ {str(e)}")
            break

        latest_notices.append(notice)
    
    # This is done to reduce DB queries
    # Get all first X notices from ERP in latest_notices
    # Check if these notices exist in the DB using their UIDs in a single query
    # Get new notice uids, filter out new notices from latest_notices based on uids
    new_notice_uids = notice_db.find_new_notices([notice['UID'] for notice in latest_notices])
    new_notices = [notice for notice in latest_notices if notice['UID'] in new_notice_uids]
    for notice in new_notices:
        logging.info(f" [NEW NOTICE]: #{notice['UID'].split('_')[0]} | {notice['Type']} | {notice['Subject']} | {notice['Company']} | {notice['Time']}")

    return new_notices


def parse_body_data(session, year, id_):
    content = session.get(NOTICE_CONTENT_URL.format(year, id_))
    content_html = bs(content.text, 'html.parser')
    body_data = bs.find_all(content_html, 'div', {'id': 'printableArea'})[0]

    return body_data


def parse_attachment(session, year, id_):
    stream = session.get(ATTACHMENT_URL.format(year, id_), stream=True)
    attachment = b''
    for chunk in stream.iter_content(4096):
        attachment += chunk
    
    return attachment

