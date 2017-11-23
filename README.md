# mftp

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Get emails when T&P stuff changes on IIT KGP's ERP.

## Setup

Deploy to Heroku and set config variables.

### Required config variables

The following is a list of all the config variables that are required for MFTP
to work:

```sh
EMAIL_ADDRESS
ERP_A1
ERP_A2
ERP_A3
ERP_PASSWORD
ERP_Q1
ERP_Q2
ERP_Q3
ERP_USERNAME
MAILGUN_API_KEY
MAILGUN_DOMAIN
MAILGUN_PUBLIC_KEY
MAILGUN_SMTP_LOGIN
MAILGUN_SMTP_PASSWORD
MAILGUN_SMTP_PORT
MAILGUN_SMTP_SERVER
MONGODB_URI
NOTICES_EMAIL_ADDRESS
```

Among these, the variables prefixed by `MAILGUN` will be added by Heroku when
you run the command `heroku addons:create mailgun:starter`.

The `MONGODB_URI` env variable will be set by `heroku addons:create
mongolab:sandbox`.

You need to add the other variables. You can add either by using the command
`heroku config:set KEY=VALUE` from the command line, or you can use the Heroku
web interface, under the **Settings** tab.

## WTF

mftp monitors your ERP account for changes to the notices and the companies list, and sends you an email if there are any new or modified entries. Your credentials are stored as Heroku config variables, and you run your own Heroku instance.

## License

GPLv3. Issues and pull requests are welcome.
