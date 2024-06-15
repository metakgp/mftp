# ERP Credentials (MUST)
ROLL_NUMBER = "XXYYXXXXX" # Institute Roll Number
PASSWORD = "**********" # ERP Password
SECURITY_QUESTIONS_ANSWERS = { # ERP Secret Questions and their Answers
    "Q1" : "A1",
    "Q2" : "A2",
    "Q3" : "A3",
}

# EMAIL (via SMTP)
## Senders' Credentials
FROM_EMAIL = "abc@gmail.com" # Notification Sender Email-id
FROM_EMAIL_PASS = "**********" # App password for the above email-id
## EMAIL - Receiver's Address
BCC_EMAIL_S = ["xyz@googlegroups.com", "abc@googlegroups.com"] # Multiple mails for bcc
# BCC_EMAIL_S = ["xyz@googlegroups.com"] # This is how you can set single mail in a list

# NTFY
NTFY_BASE_URL = "https://ntfy.sh"
NTFY_TOPIC = "mftp"
## Optional: only if you want a custom icon
NTFY_TOPIC_ICON = "https://miro.medium.com/v2/resize:fit:600/1*O94LHxqfD_JGogOKyuBFgA.jpeg"
## Optional: only if the topic is restricted
NTFY_USER = "testuser"
NTFY_PASS = "fakepassword"