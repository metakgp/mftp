import re
import logging
from email import encoders
from endpoints import TPSTUDENT_URL
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from env import FROM_EMAIL, SMTP_HOST, FROM_EMAIL_USER, FROM_EMAIL_PASS, BCC_EMAIL_S, HOSTER_EMAIL, HOSTER_INTERESTED_ROLLS, HOSTER_NAME, ROLL_MAIL, ROLL_NAME


def send_shortlists(mails, gmail_api, smtp):
    print('[SENDING SHORTLIST UPDATES]', flush=True)
    if gmail_api:
        import base64
        try:
            service = generate_send_service()
        except Exception as e:
            logging.error(f" Failed to generate GMAIL API creds ~ {str(e)}")
            return

        for mail in mails:
            try:
                response = service.users().messages().send(
                    userId="me",
                    body={"raw": base64.urlsafe_b64encode(mail.as_bytes()).decode()}
                ).execute()
            except Exception as e:
                logging.error(f"  Failed to send request to GMAIL API : {mail['Subject']} -x-> ({mail['Bcc']}) ~ {str(e)}")
                break
            if 'id' in response:
                logging.info(f" [MAIL SENT] ~ {mail['Subject']} -> ({mail['Bcc']})")
            else:
                logging.error(f" Failed to Send Mail : {mail['Subject']} -x-> ({mail['Bcc']}) ~ {response}")
                break
    elif smtp:
        import ssl
        import smtplib
        context = ssl.create_default_context()

        logging.info(f" [Connecting to {SMTP_HOST}] ...")
        with smtplib.SMTP_SSL(SMTP_HOST, 465, context=context) as server:
            logging.info(" [Connected!]")
            try:
                server.login(FROM_EMAIL_USER, FROM_EMAIL_PASS)
                logging.info(" [Logged In!]")
            except Exception as e:
                logging.error(f" Failed to log in ~ {str(e)}")
                return

            for mail in mails: 
                try:
                    server.sendmail(mail["From"], mail["Bcc"].split(', '), mail.as_string())
                    logging.info(f" [MAIL SENT] ~ {mail['Subject']} -> ({mail['Bcc']})")
                except smtplib.SMTPException as e:
                    logging.error(f" Failed to Send Mail : {mail['Subject']} -x-> ({mail['Bcc']}) ~ {str(e)}")
                    break


def format_shortlists(shortlists):
    print('[FORMATTING SHORTLIST UPDATES]', flush=True)
    table_body = """
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; width: 90%; margin: 0 auto; border: 1px solid #333; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);">
                <div align="center">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f2f2f2;">
                                {columns}
                            </tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
    </html>
    """

    host_interested_message = MIMEMultipart()
    host_interested_message["Subject"] = "People you are interested in are shortlisted!"
    host_interested_message["From"] = f'MFTP < {FROM_EMAIL} >'
    host_interested_message["Bcc"] = ", ".join(HOSTER_EMAIL)

    host_interested_cols = """
    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Name (count)</th>
    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Company (notice_id)</th>
    """

    def generate_row(company_shortlist):
        return f"""
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px;">{company_shortlist['company']} (#{company_shortlist['id']})</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{company_shortlist['count']}</td>
        </tr>
        """

    def generate_host_interested_row(name, company_shortlist):
        return f"""
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px;">{name} ({company_shortlist['count']})</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{company_shortlist['company']} (#{company_shortlist['id']})</td>
        </tr>
        """

    host_interested_rows_list = []

    mails = []
    for roll, shortlist in shortlists.items():
        if roll in HOSTER_INTERESTED_ROLLS:
            name = ROLL_NAME.get(roll)
            host_interested_rows_list += [generate_host_interested_row(name, company_shortlist) for company_shortlist in shortlist]

        student_mails = ROLL_MAIL.get(roll)
        if student_mails is None:
            continue

        message = MIMEMultipart()
        message["Subject"] = "You have been shortlisted!"
        message["From"] = f'MFTP < {FROM_EMAIL} >'
        message["Bcc"] = ", ".join(student_mails)

        rows = ''.join(generate_row(company_shortlist) for company_shortlist in shortlist)
        columns = """
        <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Company (notice_id)</th>
        <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Count</th>
        """

        shortlist_table = table_body.format(columns=columns, rows=rows)
        message.attach(MIMEText(shortlist_table, "html"))

        mails.append(message)

    host_interested_rows = ''.join(host_interested_rows_list)
    host_interested_shortlist_table = table_body.format(columns=host_interested_cols, rows=host_interested_rows)
    host_interested_message.attach(MIMEText(host_interested_shortlist_table, "html"))
    mails.append(host_interested_message)

    return mails


def send_companies(mail, gmail_api, smtp):
    print('[SENDING COMPANY UPDATES]', flush=True)

    if gmail_api:
        import base64
        
        try:
            service = generate_send_service()
        except Exception as e:
            logging.error(f" Failed to generate GMAIL API creds ~ {str(e)}")
            return

        try:
            response = service.users().messages().send(
                userId="me", 
                body={"raw": base64.urlsafe_b64encode(mail.as_bytes()).decode()}
            ).execute()
        except Exception as e:
            logging.error(f"  Failed to send request to GMAIL API : {mail['Subject']} ~ {str(e)}")
            return
        
        if 'id' in response:
            logging.info(f" [MAIL SENT] ~ {mail['Subject']}")
        else:
            logging.error(f" Failed to Send Mail : {mail['Subject']} ~ {response}")
            return
    elif smtp:
        import ssl
        import smtplib
        context = ssl.create_default_context()

        logging.info(f" [Connecting to {SMTP_HOST}] ...")
        with smtplib.SMTP_SSL(SMTP_HOST, 465, context=context) as server:
            logging.info(" [Connected!]")
            try:
                server.login(FROM_EMAIL_USER, FROM_EMAIL_PASS)
                logging.info(" [Logged In!]")
            except Exception as e:
                logging.error(f" Failed to log in ~ {str(e)}")
                return

            try:
                server.sendmail(mail["From"], mail["Bcc"].split(', '), mail.as_string())
                logging.info(f" [MAIL SENT] ~ {mail['Subject']}")
            except smtplib.SMTPException as e:
                logging.error(f" Failed to Send Mail : {mail['Subject']} ~ {str(e)}")


def format_companies(ssoToken, companies):
    print('[FORMATTING COMPANY UPDATES]', flush=True)

    message = MIMEMultipart()
    message["Subject"] = f"{HOSTER_NAME} Apply Now! New companies opened"
    message["From"] = f'MFTP < {FROM_EMAIL} >'
    message["Bcc"] = ", ".join(HOSTER_EMAIL)

    def generate_row(company):
        return f"""
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px;">
                <a href="{company['Company_Additional_Details']}&ssoToken={ssoToken}" target="_blank">{company['Name']}</a>
            </td>
            <td style="border: 1px solid #ddd; padding: 8px;">
                {company['Role']} 
                (<a href="{company['Apply_Link_CV']}1&ssoToken={ssoToken}" target="_blank">CV1</a>,
                 <a href="{company['Apply_Link_CV']}2&ssoToken={ssoToken}" target="_blank">CV2</a>,
                 <a href="{company['Apply_Link_CV']}3&ssoToken={ssoToken}" target="_blank">CV3</a>)
            </td>
            <td style="border: 1px solid #ddd; padding: 8px;">
                <a href="{company['Additional_Job_Description']}&ssoToken={ssoToken}" target="_blank">{company.get('CTC', 'N/A')}</a>
            </td>
            <td style="border: 1px solid #ddd; padding: 8px;">{company['End_Date']}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{company['Interview_Date']}</td>
        </tr>
        """
    company_rows = ''.join(generate_row(company) for company in companies)
    
    html_content = """
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; width: 90%; margin: 0 auto; border: 1px solid #333; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);">
                <div align="center">
                    !! Click <a href="{companies_url}" target="_blank">here</a>, in order to enable the links below !!
                </div>
                <br>
                <div align="center">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f2f2f2;">
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Company</th>
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Role (Apply)</th>
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">CTC</th>
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">End Date</th>
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Interview Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {company_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
    </html>
    """
    companies_table = html_content.format(companies_url=f"{TPSTUDENT_URL}?ssoToken={ssoToken}", company_rows=company_rows)
    message.attach(MIMEText(companies_table, "html"))

    return message


def send_notices(mails, smtp, gmail_api, notice_db):
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

        logging.info(f" [Connecting to {SMTP_HOST}] ...")
        with smtplib.SMTP_SSL(SMTP_HOST, 465, context=context) as server:
            logging.info(" [Connected!]")
            try:
                server.login(FROM_EMAIL_USER, FROM_EMAIL_PASS)
                logging.info(" [Logged In!]")
            except Exception as e:
                logging.error(f" Failed to log in ~ {str(e)}")
                return

            for notif in mails: 
                mail = notif.get('formatted_notice')
                try:
                    server.sendmail(mail["From"], mail["Bcc"].split(', '), mail.as_string())
                    logging.info(f" [MAIL SENT] ~ {mail['Subject']}")
                    notice_db.save_notice(notif['original_notice'])
                except smtplib.SMTPException as e:
                    logging.error(f" Failed to Send Mail : {mail['Subject']} ~ {str(e)}")
                    break


def parse_notice_body(body_data):
    body = body_data.decode_contents(formatter='html')
    return str(body)


def format_notices(notices):
    print('[FORMATTING MAILS]', flush=True)

    formatted_notifs = []
    for notice in reversed(notices):
        id_ = notice['UID'].split('_')[0]
        message = MIMEMultipart()
        message["Subject"] = f"#{id_} | {notice['Type']} | {notice['Subject']} | {notice['Company']}"
        message["From"] = f'MFTP < {FROM_EMAIL} >'
        message["Bcc"] = ", ".join(BCC_EMAIL_S)
        try:
            body = parse_notice_body(notice['BodyData'])
            notice['Body'] = body
            notice.pop('BodyData', None)
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
        
        if 'Attachment' in notice:
            file = MIMEBase('application', 'octet-stream')
            file.set_payload(notice['Attachment'])
            encoders.encode_base64(file)
            file.add_header('Content-Disposition', 'attachment', filename='Attachment.pdf')
            message.attach(file)
            logging.info(f" [PDF ATTACHED] On notice #{id_} of length ~ {len(notice['Attachment'])}")
            
        formatted_notifs.append({"formatted_notice": message, "original_notice": notice})

    return formatted_notifs


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
