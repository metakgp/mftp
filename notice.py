from endpoints import *
from env import MONGODB_URI as uri
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs
from pymongo import DESCENDING as latest
from pymongo.mongo_client import MongoClient as mc
# Notices Collection
col = mc(uri).mftp.notices
    
def fetch(headers, session, ssoToken):
    r = session.post(TPSTUDENT_URL, data=dict(ssoToken=ssoToken, menu_id=11, module_id=26), headers=headers)
    r = session.get(NOTICEBOARD_URL, headers=headers)
    r = session.get(NOTICES_URL, headers=headers)
    
    soup = bs(r.text, features="xml")
    xml = soup.prettify().encode('utf-8')
    root = ET.fromstring(xml)

    if len(list(col.find())) != 0:
        latest_index = int(col.find().sort('Index', latest)[0]['Index'])
    else:
        latest_index = 0
        
    notices = []
    year = root.findall('row')[0].find('cell[8]').text.split('"')[1].strip()
    for row in root.findall('row'):
        notice = {
            'Index': int(row.find('cell[1]').text.strip()),
            'Type': row.find('cell[2]').text.strip(),
            'Subject': row.find('cell[3]').text.strip(),
            'Company': row.find('cell[4]').text.strip(),
        }
        if bs(row.find('cell[8]').text, 'html.parser').find('a').attrs['title'] == 'Download':
            notice['Attachment'] = 'Yes'
        
        if int(notice['Index']) > latest_index:
            notices.append(notice)
        else:
            break
            
    return notices, session, year


def save(notices):
    for notice in notices:
        if col.find_one({"Index": notice['Index']}) is None:
            col.insert_one(notice)
            
