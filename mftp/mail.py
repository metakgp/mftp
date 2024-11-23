import re
import logging
from email import encoders
from bs4 import BeautifulSoup as bs
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from env import FROM_EMAIL, FROM_EMAIL_PASS, BCC_EMAIL_S
from endpoints import NOTICE_CONTENT_URL, ATTACHMENT_URL


def send(mails, smtp, gmail_api, notice_db):
    print('[SENDING MAILS]', flush=True)

    if gmail_api:
        import base64
        
        try:
            service = generate_send_service()
        except Exception as e:
            logging.error(f" Failed to generate GMAIL API creds ~ {str(e)}")
            return

        for notif in mails:
            mail = notif.get('formatted_notice')
            try:
                response = service.users().messages().send(
                    userId="me", 
                    body={"raw": base64.urlsafe_b64encode(mail.as_bytes()).decode()}
                ).execute()
            except Exception as e:
                logging.error(f"  Failed to send request to GMAIL API : {mail['Subject']} ~ {str(e)}")
                break
            
            if 'id' in response:
                logging.info(f" [MAIL SENT] ~ {mail['Subject']}")
                notice_db.save_notice(notif['original_notice'])
            else:
                logging.error(f" Failed to Send Mail : {mail['Subject']} ~ {response}")
                break
    elif smtp:
        import ssl
        import smtplib
        context = ssl.create_default_context()

        logging.info(" [Connecting to smtp.google.com] ...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            logging.info(" [Connected!]")
            try:
                server.login(FROM_EMAIL, FROM_EMAIL_PASS)
                logging.info(" [Logged In!]")
            except Exception as e:
                logging.error(f" Failed to log in ~ {str(e)}")
                return

            for notif in mails: 
                mail = notif.get('formatted_notice')
                try:
                    server.sendmail(mail["From"], BCC_EMAIL_S, mail.as_string())
                    logging.info(f" [MAIL SENT] ~ {mail['Subject']}")
                    notice_db.save_notice(notif['original_notice'])
                except smtplib.SMTPException as e:
                    logging.error(f" Failed to Send Mail : {mail['Subject']} ~ {str(e)}")
                    break


def format_notice(notices, session):
    print('[FORMATTING MAILS]', flush=True)

    formatted_notifs = []
    for notice in reversed(notices):
        id_, year = notice['UID'].split('_')
        
        message = MIMEMultipart()
        message["Subject"] = f"#{id_} | {notice['Type']} | {notice['Subject']} | {notice['Company']}"
        message["From"] = f'MFTP < {FROM_EMAIL} >'
        message["Bcc"] = ", ".join(BCC_EMAIL_S)
        
        try:
            body = parseBody(session, year, id_)
        except Exception as e:
            logging.error(f" Failed to parse mail body ~ {str(e)}")
            break

        # Hyperlinking any link with <click here> to reduce link clutter
        body = re.sub(r"(https?://[^\s]+)", r'<a href="\1">click here</a>', body)

        # Decent enough layout for the mail
        body = f"""
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; width: 90%; margin: 0 auto; border: 1px solid #333; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);">
                    <div style="margin-bottom: 20px;">
                        {body}
                    </div>
                    <div style="text-align: right; font-style: italic;">
                        ({notice['Time']})
                    </div>
                    <div>
                        <hr>
                        <b>DISCLAIMER</b>: MFTP is unofficial. Not affiliated with CDC, ERP, or Placement Committee. Do not rely solely on MFTP for updates. MFTP-related issues cannot be used as arguments with official authorities.
                    </div>
                </div>
            </body>
        </html>
        """
        
        message.attach(MIMEText(body, "html"))
        
        # Handling attachment
        try:
            attachment = parseAttachment(session, year, id_)
        except Exception as e:
            logging.error(f" Failed to parse mail attachment ~ {str(e)}")
            break

        if len(attachment) != 0:
            file = MIMEBase('application', 'octet-stream')
            file.set_payload(attachment)
            encoders.encode_base64(file)
            file.add_header('Content-Disposition', 'attachment', filename='Attachment.pdf')
            message.attach(file)
            logging.info(f" [PDF ATTACHED] On notice #{id_} of length ~ {len(attachment)}")
            
        formatted_notifs.append({"formatted_notice": message, "original_notice": notice})

    return formatted_notifs


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


def generate_send_service():
    import os
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    creds = None
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    if os.path.exists("mail_send_token.json"):
        creds = Credentials.from_authorized_user_file("mail_send_token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "mail_send_creds.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("mail_send_token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

