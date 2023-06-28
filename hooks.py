from os import environ as env
import requests

from erp import req_args

if 'NOTICES_EMAIL_ADDRESS' not in env:
    env['NOTICES_EMAIL_ADDRESS'] = env['EMAIL_ADDRESS']
METAKGP_BRANDING = "Brought to you by <a href='https://metakgp.github.io'>Metakgp</a>"


def make_text(company):
    text = '%s: %s (%s - %s)' % (company['name'], company['job'],
                                 company['start_date'], company['end_date'])
    return text


def notices_updated(notices):
    for notice in notices:
        message = {
            'to': env['NOTICES_EMAIL_ADDRESS'],
            'from': 'no-reply@mftp.herokuapp.com',
            'fromname': 'MFTP',
            'subject': 'Notice: %s - %s' % (notice['subject'],
                                            notice['company']),
            'html': '<i>(%s)</i>: <p>%s</p><br/><hr/><p style="color:#6c757d;">%s</p>' % (notice['time'], notice['text'], METAKGP_BRANDING),
        }
        files = []
        if 'attachment_url' in notice:
            filename = "attachment.pdf"
            files = [('attachment', (filename, notice['attachment_raw']))]

        r = requests.post(
            'https://api.mailgun.net/v3/%s/messages' % env['MAILGUN_DOMAIN'],
            auth=('api', env['MAILGUN_API_KEY']),
            data={
                'from': 'MFTP <no-reply@%s>' % env['MAILGUN_DOMAIN'],
                'to': [env['NOTICES_EMAIL_ADDRESS']],
                'subject': message['subject'].encode("utf-8"),
                'html': message['html'].encode("utf-8")
            }, files=files, verify=False)

        # r = requests.post('https://api.sendgrid.com/api/mail.send.json',
        # data=message)
        print('Sent notice to', message['to'], ':', message['subject'], r.text)
