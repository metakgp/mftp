from os import environ as env
import requests

if 'NOTICES_EMAIL_ADDRESS' not in env:
    env['NOTICES_EMAIL_ADDRESS'] = env['EMAIL_ADDRESS']


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
    r = requests.post(
        'https://api.mailgun.net/v3/%s/messages' % env['MAILGUN_DOMAIN'],
        auth=('api', env['MAILGUN_API_KEY']),
        data={
            'from': 'MFTP <no-reply@%s>' % env['MAILGUN_DOMAIN'],
            'to': [env['EMAIL_ADDRESS']],
            'subject': message['subject'],
            'html': message['html']
        })

    # r = requests.post('https://api.sendgrid.com/api/mail.send.json',
    #                  data=message)
    print r.text


def notices_updated(notices):
    for notice in notices:
        message = {
            'api_user': env['SENDGRID_USERNAME'],
            'api_key': env['SENDGRID_PASSWORD'],
            'to': env['NOTICES_EMAIL_ADDRESS'],
            'from': 'no-reply@mftp.herokuapp.com',
            'fromname': 'MFTP',
            'subject': 'Notice: %s - %s' % (notice['subject'],
                                            notice['company']),
            'html': '<i>(%s)</i>: <p>%s<p>' % (notice['time'], notice['text']),
        }
        if 'attachment' in notice:
            message['html'] += '<p>Attachment: <a href="%s">Download</a></p>' \
                               % notice['attachment']
        r = requests.post(
            'https://api.mailgun.net/v3/%s/messages' % env['MAILGUN_DOMAIN'],
            auth=('api', env['MAILGUN_API_KEY']),
            data={
                'from': 'MFTP <no-reply@%s>' % env['MAILGUN_DOMAIN'],
                'to': [env['NOTICES_EMAIL_ADDRESS']],
                'subject': message['subject'],
                'html': message['html']
            }, verify=False)

        # r = requests.post('https://api.sendgrid.com/api/mail.send.json',
        # data=message)
        print 'Sent notice to', message['to'], ':', message['subject'], r.text
