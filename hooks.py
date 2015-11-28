from os import environ as env
import requests


def make_text(company):
    text = '%s: %s (%s - %s)' % (company['name'], company['job'],
                                 company['start_date'], company['end_date'])
    return text


def companies_updated(companies):
    message = {
        'api_user': env['SENDGRID_USERNAME'],
        'api_key': env['SENDGRID_PASSWORD'],
        'to': env['EMAIL_ADDRESS'],
        'from': 'no-reply@mftp.herokuapp.com',
        'fromname': 'MFTP',
        'subject': 'Companies updated: ' + ', '.join(
            [c['name'] for c in companies]),
        'text': '\n'.join([make_text(c) for c in companies]),
    }
    r = requests.post('https://api.sendgrid.com/api/mail.send.json',
                      data=message)
    print r.text
