import base64
import logging
from email.mime.text import MIMEText
from mail import generate_send_service
from env import KEEP_TOKEN_ALIVE_EMAIL, FROM_EMAIL
from email.mime.multipart import MIMEMultipart

def keep_token_alive():
	print('[KEEP TOKEN ALIVE] | [SCHEDULED EVENT]', flush=True)

	mail_content = """
	Hello,<br/><br/>

	This is an automated email to renew the authorization for the Gmail API access used by your running instance of MFTP. Keeping the API access refreshed allows MFTP to continue syncing your Gmail mailbox smoothly.<br/><br/>

	No action is required on your part. This email is just part of regular workflow when using gmail api for uninterrupted service.<br/><br/>

	Regards,<br/>
	Arpit Bhardwaj (<a href="https://linktr.ee/proffapt">proffapt</a>)<br/>
	Developer of MFTP
	"""
	raw_mail_bytes = generate_raw_mail_bytes(mail_content)
	send_keep_token_alive_mail(raw_mail_bytes)


def send_keep_token_alive_mail(raw_mail_bytes):
	try:
		service = generate_send_service()
	except Exception as e:
		logging.error(f" Failed to generate GMAIL API creds ~ {str(e)}")

	try:
		response = service.users().messages().send(
			userId="me", 
			body={"raw": raw_mail_bytes}
		).execute()
	except Exception as e:
		logging.error(f"  Failed to send request to Gmail API ~ {str(e)}")
	
	if 'id' in response:
		logging.info(f" MAIL SENT ~ TO: {KEEP_TOKEN_ALIVE_EMAIL}")
	else:
		logging.error(f" Failed to Send Mail to {KEEP_TOKEN_ALIVE_EMAIL}: ~ {str(e)}")


def generate_raw_mail_bytes(body: str):
	message = MIMEMultipart()
	message["Subject"] = f"[SCHEDULED EVENT] ~ MFTP | Refreshing GMAIL API Token"
	message["From"] = f'MFTP < {FROM_EMAIL} >'
	message["To"] = KEEP_TOKEN_ALIVE_EMAIL

	message.attach(MIMEText(body, "html"))

	return base64.urlsafe_b64encode(message.as_bytes()).decode()
