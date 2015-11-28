from mandrill import Mandrill
from os import environ as env

mailer = Mandrill(env['MANDRILL_APIKEY'])


def make_text(company):
    text = '%s: %s (%s - %s)' % (company['name'], company['job'],
                                 company['start_date'], company['end_date'])
    return text


def companies_updated(companies):
    message = {
        'from_name': 'MFTP',
        'from_email': 'no-reply@mftp.herokuapp.com',
        'to': [{'email': env['EMAIL_ADDRESS']}],
        'track_clicks': None,
        'track_opens': None,
        'subject': 'Companies updated: ' + ', '.join(
            [c['name'] for c in companies]),
        'text': '\n'.join([make_text(c) for c in companies]),
    }
    result = mailer.messages.send(message=message, async=False, ip_pool='Main Pool')
    print result
