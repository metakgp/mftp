# ERP Credentials (MUST)
ROLL_NUMBER = "XXYYXXXXX" # Institute Roll Number
PASSWORD = "**********" # ERP Password
SECURITY_QUESTIONS_ANSWERS = { # ERP Secret Questions and their Answers
    "Q1": "A1",
    "Q2": "A2",
    "Q3": "A3",
}

# MONGODB Credentials (MUST)
MONGO_ROOT_USERNAME = "mftp"
MONGO_ROOT_PASSWORD = "ptfm"
MONGO_DATABASE = "mftp"
MONGO_PORT = "27017"
MONGO_URI = f'mongodb://{MONGO_ROOT_USERNAME}:{MONGO_ROOT_PASSWORD}@db:{MONGO_PORT}'
MONGO_COLLECTION = "AY_2024-25"

# HOSTER'S DETAILS - For personalised updates (MUST)
## If hoster wish to share their powers with others as well
## Sort of emergency contact?
## That is why it is a list of emails
HOSTER_EMAIL = ["hoster@kgpian.iitkgp.ac.in", "emergency.hoster@kgpian.iitkgp.ac.in"] 
HOSTER_NAME = "Arpit Bhardwaj"
HOSTER_ROLL = ROLL_NUMBER
HOSTER_INTERESTED_ROLLS = ["XXYYXXXXX", "NNAANNNNN"]

# COMPANY NOTIFIER CONFIG (MUST)
COMPANY_NOTIFIER=True

# SHORTLIST CONFIG (MUST)
## Maps roll number to student names
SHORTLIST_NOTIFIER=True
ROLL_NAME = {
    HOSTER_ROLL: HOSTER_NAME,
    "XXYYXXXXX": "XY Sharma",
    "NNAANNNNN": "AB Gupta",
}
## Maps roll number to their emails
## So, that individuals are notified if they are mentioned somewhere
## It is a list again, which act as emergency contact
ROLL_MAIL = {
    HOSTER_ROLL: HOSTER_EMAIL,
    "XXYYXXXXX": ["xy@kgpian.iitkgp.ac.in", "emergency.xy@kgpian.iitkgp.ac.in"],
    "NNAANNNNN": ["ab@kgpian.iitkgp.ac.in", "emergency.ab@kgpian.iitkgp.ac.in"],
}

# EMAIL
## Senders' Credentials (via SMTP)
FROM_EMAIL = "abc@gmail.com" # Notification Sender Email-id
FROM_EMAIL_PASS = "**********" # App password for the above email-id
## EMAIL - Receiver's Address
BCC_EMAIL_S = ["xyz@googlegroups.com", "abc@googlegroups.com"] # Multiple mails for bcc
# BCC_EMAIL_S = ["xyz@googlegroups.com"] # This is how you can set single mail in a list

# NTFY
NTFY_BASE_URL = "https://ntfy.sh"
## This is a list of ntfy topics, with their respective filters,
## for the logic to determine which message is to be sent on which topic
NTFY_TOPICS = {
    "mftp-test": {},
    "mftp-placement-test": {
        "Type": "PLACEMENT",
    },
    "mftp-internship-test": {
        "Type": "INTERNSHIP",
    },
    "mftp-ppo-test": {
        "Subject": "PPO",
    },
}
## Optional: only if you want a custom icon
NTFY_TOPIC_ICON = "https://miro.medium.com/v2/resize:fit:600/1*O94LHxqfD_JGogOKyuBFgA.jpeg"
## Optional: only if the topic is restricted
NTFY_USER = "testuser"
NTFY_PASS = "fakepassword"
## Optional (specific to metakgp [naarad] architecture): Heimdall security token
HEIMDALL_COOKIE = '17ab96bd8ffbe8ca58a78657a918558'
