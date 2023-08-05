import re 
companies = [] # List containing all the shortlisted companies

def check(mails):
    for mail in mails:
        check_mail(mail)
        
        # if len(mail.get_payload()) > 1:
        #     check_attachment(mail)

    return companies


def check_mail(mail):
    body = str(mail.get_payload()[0]._payload)
    # if mail_body.find(ROLL_NUMBER) != -1:
    if body.find("20CS30071") != -1:
        match = re.search(r'shortlist for (\w+(?: \w+)*)', body)
        company = match.group(1)
        companies.append(company)

