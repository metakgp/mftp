# mftp

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

NOTE: The `master` branch is auto-deployed to Heroku.

Get emails when T&P stuff changes on IIT KGP's ERP.

## Setup

Deploy to Heroku and set config variables.

### Required config variables

The following is a list of all the config variables that are required for MFTP
to work:

```sh
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

Set `NOTICES_EMAIL_ADDRESS` variable to the email you want to send notice updates to.

Set `MONGODB_URI` variable to the uri of mongoDB instance you want to use.
We use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas "Atlas") for storage.
You can get your own mongoDB URI [here](https://docs.atlas.mongodb.com/getting-started/).

We suggest using a log manager addon like 
[Papertrail](https://elements.heroku.com/addons/papertrail) 
since the application generates lots of logs.

You need to add the other variables. You can add either by using the command
`heroku config:set KEY=VALUE` from the command line, or you can use the Heroku
web interface, under the **Settings** tab.

### Testing on local system

1. Make a copy of the .env-template file and rename it to .env in the root directory.

`cp ./.env-template ./.env`

2. Add values of all the variables in the newly created .env file accordingly. (Descriptions of all the varibales can be found in app.json).
Note : app.json does not contain `DEBUG` variable as it explicitly configures scripts to run in local environment friendly way.

3. Install all the python modules from the requirements file. **Note : The program runs on Python 3.6.2**

`pip install -r requirements.txt`

4. Run settings.py to load variables from .env file to the local environment.

`python settings.py`

5. Now run the main tornado server.

`python main.py`


## Migration

Database Migration details inside migration directory

## WTF

mftp monitors your ERP account for changes to the notices and the companies list, and sends you an email if there are any new or modified entries. Your credentials are stored as Heroku config variables, and you run your own Heroku instance.

## Errors

The folder `incident-postmortems` contains information about failures and downtimes we have noticed in the past, their cause, and the solutions employed. More information is provided in the `README.md` inside the folder.

## License

GPLv3. Issues and pull requests are welcome.
