import smtplib, ssl
from email import encoders
from bs4 import BeautifulSoup as bs
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from env import FROM_EMAIL, FROM_EMAIL_PASS, TO_EMAIL
from endpoints import NOTICE_CONTENT_URL, ATTACHMENT_URL

def format(notices, session, year): 
    mails = []
    for notice in notices:
        message = MIMEMultipart()
        message["Subject"] = f"{notice['Subject']} - {notice['Company']}"
        message["From"] = FROM_EMAIL
        message["To"] = TO_EMAIL

        body = parseBody(session, year, notice['Index'])
        message.attach(MIMEText(body, "html"))
        
        if notice['Attachment']:
            file = MIMEBase('application', 'octet-stream')
            attachment = parseAttachment(session, year, notice['Index'])
            file.set_payload(attachment)
            encoders.encode_base64(file)
            file.add_header('Content-Disposition', 'attachment', filename='Attachment.pdf')
            message.attach(file)
            
        mails.append(message)

    return mails
        

def send(mails):
    context = ssl.create_default_context()
    # with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    #     server.login(FROM_EMAIL, FROM_EMAIL_PASS.encode("utf-8"))
    with smtplib.SMTP("localhost", 1025) as server:
        for mail in mails: 
            server.sendmail(mail["From"], mail["To"], mail.as_string())
            
            
def parseBody(session, year, id_):
    content = session.get(NOTICE_CONTENT_URL.format(year, id_))
    content_html = bs(content.text, 'html.parser')
    content_html_div = bs.find_all(content_html, 'div', {'id': 'printableArea'})[0]
    body = content_html_div.decode_contents(formatter='html')
    
    return str(body)


def parseAttachment(session, year, id_):
    stream = session.get(ATTACHMENT_URL.format(year, id_), stream=True)
    attachment = b''
    for chunk in stream.iter_content(4096):
        attachment += chunk
    
    return attachment

