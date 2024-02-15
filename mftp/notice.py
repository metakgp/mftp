import os
import logging
from endpoints import *
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs
    
def fetch(headers, session, ssoToken, lsnif):
    print('[FETCHING NOTICES]', flush=True)
    try:
        r = session.post(TPSTUDENT_URL, data=dict(ssoToken=ssoToken, menu_id=11, module_id=26), headers=headers)
        r = session.get(NOTICEBOARD_URL, headers=headers)
        r = session.get(NOTICES_URL, headers=headers)
    except Exception as e:
        logging.error(f" Failed to navigate to Noticeboard ~ {str(e)}")

    try:
        soup = bs(r.text, features="xml")
        xml = soup.prettify().encode('utf-8')
        root = ET.fromstring(xml)
    except Exception as e:
        logging.error(f" Failed to extract data from Noticeboard ~ {str(e)}")

    latest_index = get_latest_index(lsnif)
    logging.info(f" Latest Saved Notice Index ~ {latest_index}")
        
    notices = []
    for row in root.findall('row'):
        id_ = row.find('cell[1]').text.strip()
        year = root.findall('row')[0].find('cell[8]').text.split('"')[1].strip()
        notice = {
            'UID': f'{id_}_{year}',
            'Time': row.find('cell[7]').text.strip(),
            'Type': row.find('cell[2]').text.strip(),
            'Subject': row.find('cell[3]').text.strip(),
            'Company': row.find('cell[4]').text.strip(),
        }
        
        if int(id_) > latest_index:
            notices.append(notice)
            logging.info(f" [NEW NOTICE]: #{id_} | {notice['Type']} | {notice['Subject']} | {notice['Company']} | {notice['Time']}")
        else:
            break
            
    return notices


def get_latest_index(lsnif):
    try:
        with open(lsnif, 'r') as file:
            file_content = file.read().strip()
            latest_index = int(file_content)
    except FileNotFoundError:
        latest_index = 0
    
    return latest_index


def update_lsni(lsnif, notices, i):
    lsni = notices[-i]['UID'].split('_')[0] # Latest Sent Notice Index

    # Create file if it doesn't exist
    if not os.path.exists(lsnif):
        open(lsnif, 'w').close()

    # Save the value of Latest Sent Notice Index
    try:
        with open(lsnif, 'w') as file:
            file.write(lsni)
    except Exception as e:
        logging.error(f" Failed to Save Notice ~ #{lsni}")
