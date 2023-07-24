import smtplib, ssl
from email import encoders
from env import FROM_EMAIL, FROM_EMAIL_PASS, TO_EMAIL
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

def format(notices): 
    mails = []
    for notice in notices:
        message = MIMEMultipart()
        message["Subject"] = f"{notice['Subject']} - {notice['Company']}"
        message["From"] = FROM_EMAIL
        message["To"] = TO_EMAIL

        message.attach(MIMEText(notice['Body'], "html"))
        if notice['Attachment'] != b'':
            file = MIMEBase('application', 'octet-stream')
            file.set_payload(notice['Attachment'])
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
