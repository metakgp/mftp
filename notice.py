from endpoints import *
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs

def fetch(headers, session, ssoToken):
    r = session.post(TPSTUDENT_URL, data=dict(ssoToken=ssoToken, menu_id=11, module_id=26), headers=headers)
    r = session.get(NOTICEBOARD_URL, headers=headers)
    r = session.get(NOTICES_URL, headers=headers)
    
    soup = bs(r.text, features="xml")
    xml = soup.prettify().encode('utf-8')
    root = ET.fromstring(xml)
    
    notices = []
    for row in root.findall('row'):
        year = row.find('cell[8]').text.split('"')[1].strip()
        id_ = row.find('cell[8]').text.split('"')[3].strip()
        notice = {
            'Index': row.find('cell[1]').text.strip(),
            'Type': row.find('cell[2]').text.strip(),
            'Subject': row.find('cell[3]').text.strip(),
            'Company': row.find('cell[4]').text.strip(),
            'Body': parseBody(session, year, id_),
            'Attachment': parseAttachment(session, year, id_),
            'Time': row.find('cell[7]').text.strip(),
        }
        if notice not in notices:
            notices.append(notice)
        if int(notice['Index']) > 98: # TODO: Replace with latest index in mongo db
            break
            
    return notices

def parseBody(session, year, id_):
    content = session.get(NOTICE_CONTENT_URL.format(year, id_))
    content_html = bs(content.text, 'html.parser')
    content_html_div = bs.find_all(content_html, 'div', {'id': 'printableArea'})[0]
    body = content_html_div.decode_contents(formatter='html')
    
    return body

def parseAttachment(session, year, id_):
    stream = session.get(ATTACHMENT_URL.format(year, id_), stream=True)
    attachment = b''
    for chunk in stream.iter_content(4096):
        attachment += chunk
    
    return attachment
