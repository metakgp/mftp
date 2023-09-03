import logging
from endpoints import *
from pymongo import DESCENDING
from env import MONGODB_URI as uri
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient as mc
# Notices Collection
col = mc(uri).mftp.notices
    
def fetch(headers, session, ssoToken):
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

    if len(list(col.find())) != 0:
        try:
            latest_document = col.find_one(sort=[('_id', DESCENDING)])
        except Exception as e:
            logging.error(f" Failed to fetch Latest Saved Notice Index ~ {str(e)}")
        latest_index = int(latest_document['UID'].split('_')[0])
    else:
        latest_index = 0
    logging.info(f" Latest Saved Notice Index ~ {latest_index}")
        
    notices = []
    logging.info(f" Notices uploaded within 2 minutes of current time will be skipped")
    for row in root.findall('row'):
        id_ = row.find('cell[1]').text.strip()
        year = root.findall('row')[0].find('cell[8]').text.split('"')[1].strip()
        has_attachment = True if bs(row.find('cell[8]').text, 'html.parser').find('a').attrs['title'] == 'Download' else False
        notice = {
            'UID': f'{id_}_{year}_{has_attachment}',
            'Time': row.find('cell[7]').text.strip(),
            'Type': row.find('cell[2]').text.strip(),
            'Subject': row.find('cell[3]').text.strip(),
            'Company': row.find('cell[4]').text.strip(),
        }
        
        current_time = datetime.now()
        notice_time = datetime.strptime(notice["Time"], '%d-%m-%Y %H:%M')
        logging.info(f" Notice ID ~ {id_} | Notice Time ~ {notice_time} | Current Time ~ {current_time}")
        
        if int(id_) > latest_index:
            if notice_time + timedelta(minutes=2) < current_time:
                notices.append(notice)
                logging.info(f" [ADDED NOTICE ~ {id_}]: {notice['Subject']} | {notice['Company']} | {notice['Time']} | {has_attachment}")
            else:
                logging.info(f" [SKIPPED NOTICE ~ {id_}]: {notice['Subject']} | {notice['Company']} | {notice['Time']} | {has_attachment}")
        else:
            break
            
    return notices, session


def save(notices):
    try:
        if notices: print('[SAVING NOTICES]', flush=True)
        for notice in reversed(notices):
            col.insert_one(notice)
    except Exception as e:
        logging.error(f" Failed to save notices ~ {str(e)}")
