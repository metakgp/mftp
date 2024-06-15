<div id="top"></div>

<!-- ABOUT THE PROJECT -->
## MFTP Scripts

[mftp.py](./mftp.py) continuously monitors the CDC Noticeboard and forwards incoming notices to the configured email address, whether it's an individual account or a Google Group.

<!-- TABLE OF CONTENTS -->
<details>
<summary>Table of Contents</summary>

- [Using docker](#using-docker)
    - [Prerequisites](#prerequisites-with-docker)
    - [Installation](#installation-with-docker)
    - [Usage](#usage-with-docker)
        - [Docker Compose](#docker-compose)
        - [Docker Command](#docker-command)
        - [As a cronjob](#as-a-cronjob)
            - [With Docker Compose](#with-docker-compose)
            - [With Docker Command](#with-docker-command)
- [Without using docker](#without-using-docker)
    - [Prerequisites](#prerequisites-without-docker)
    - [Installation](#installation-without-docker)
    - [Usage](#usage-without-docker)

</details>

## Using docker

To set up a local instance of the application using docker, follow the steps below.

<div id="prerequisites-with-docker"></div>

### Prerequisites
The following requirements are to be satisfied for the project to function properly:
* [docker](https://docs.docker.com/get-docker/)
* This project depends on [ERP Login module](https://github.com/proffapt/iitkgp-erp-login-pypi) by [Arpit Bhardwaj](https://github.com/proffapt) for the ERP Login workflow. Read its [documentation](https://github.com/proffapt/iitkgp-erp-login-pypi?tab=readme-ov-file#input) and setup your OTP fetching token mentioned in second point (`OTP_CHECK_INTERVAL`) of optional arguments.

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="installation-with-docker"></div>

### Installation

1. Get the docker image
   
   You can get the docker image from either docker-hub or by buiilding it locally:
   - Pull from docker-hub
     ```sh
     sudo docker pull proffapt/mftp
     ```
   - Build from Dockerfile
       * Clone the repository and cd into it
         ```sh
         git clone https://github.com/metakgp/mftp
         cd mftp/mftp
         ```
       * Build the image
         ```sh
         sudo docker build -t proffapt/mftp .
         ```
2. Create a directory which will contain your tokens and env.py, name it as `mftp_config`
3. Follow the steps to [configure mail sending](#sending-emails). **Skip this step if you wish to use method not involving mails, for example, ntfy**
4. Follow the steps to [configure env variables](#configuring-environment-variables)

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="usage-with-docker"></div>

### Usage

#### Docker Compose

It is mandatory to provide both of the following `env variables` before the _docker-compose_ command.
- `MFTP_CONFIG`: Absolute path to `mftp_config` directory
- `MFTP_MODE`: Mode of sending mail - **--smtp**, **--gmail-api** and **--ntfy**

```sh
sudo MFTP_CONFIG=/path/to/mftp_config MFTP_MODE=--smtp docker-compose up -d # Using SMTP for sending mails
```

```sh
sudo MFTP_CONFIG=/path/to/mftp_config MFTP_MODE=--gmail-api docker-compose up -d # Using Gmail API for sending mails
```

```sh
sudo MFTP_CONFIG=/path/to/mftp_config MFTP_MODE=--ntfy docker-compose up -d # Using Gmail API for sending mails
```

<p align="right">(<a href="#top">back to top</a>)</p>

#### Docker Command

It is mandatory to provide either of the following flags to the execution command.
- `--smtp`: Using SMTP for sending mails
  ```sh
  sudo docker run -d \
  -v /path/to/mftp_config/env.py:/mftp/env.py \
  -v /path/to/mftp_config/token.json:/mftp/token.json \
  -v /path/to/mftp_config/credentials.json:/mftp/credentials.json \
  -v /path/to/mftp_config/mail_send_token.json:/mftp/mail_send_token.json \
  -v /path/to/mftp_config/mail_send_creds.json:/mftp/mail_send_creds.json \
  -v /path/to/mftp_config/.lsnif:/mftp/.lsnif \
  -v /path/to/mftp_config/.session:/mftp/.session \
  --restart=unless-stopped \
  --name mftp \
  proffapt/mftp --smtp
  ```
  
- `--gmail-api`: Using Gmail API for sending mails
    ```sh
  sudo docker run -d \
  -v /path/to/mftp_config/env.py:/mftp/env.py \
  -v /path/to/mftp_config/token.json:/mftp/token.json \
  -v /path/to/mftp_config/credentials.json:/mftp/credentials.json \
  -v /path/to/mftp_config/mail_send_token.json:/mftp/mail_send_token.json \
  -v /path/to/mftp_config/mail_send_creds.json:/mftp/mail_send_creds.json \
  -v /path/to/mftp_config/.lsnif:/mftp/.lsnif \
  -v /path/to/mftp_config/.session:/mftp/.session \
  --restart=unless-stopped \
  --name mftp \
  proffapt/mftp --gmail-api
  ```

- `--ntfy`: Using NTFY to serve notification
    ```sh
  sudo docker run -d \
  -v /path/to/mftp_config/env.py:/mftp/env.py \
  -v /path/to/mftp_config/token.json:/mftp/token.json \
  -v /path/to/mftp_config/credentials.json:/mftp/credentials.json \
  -v /path/to/mftp_config/mail_send_token.json:/mftp/mail_send_token.json \
  -v /path/to/mftp_config/mail_send_creds.json:/mftp/mail_send_creds.json \
  -v /path/to/mftp_config/.lsnif:/mftp/.lsnif \
  -v /path/to/mftp_config/.session:/mftp/.session \
  --restart=unless-stopped \
  --name mftp \
  proffapt/mftp --ntfy
  ```

<p align="right">(<a href="#top">back to top</a>)</p>

#### As a cronjob

It is also possible to run these docker containers as a cronjob:
- ##### With Docker Compose
    - Comment out the line `restart: unless-stopped`
    - Append ` --cron` into the `MFTP_MODE` env variable. For example:
        * Using Cronjob to run container and SMTP to send mails
          ```sh
          sudo MFTP_CONFIG=/path/to/mftp_config MFTP_MODE="--smtp --cron" docker-compose up -d
          ```
        * Using Cronjob to run container and Gmail API to send mails
          ```sh
          sudo MFTP_CONFIG=/path/to/mftp_config MFTP_MODE="--gmail-api --cron" docker-compose up -d
          ```
        * Using Cronjob to run container and ntfy to send mails
          ```sh
          sudo MFTP_CONFIG=/path/to/mftp_config MFTP_MODE="--ntfy --cron" docker-compose up -d
          ```
- ##### With Docker Command
    - Remove `--restart=unless-stopped` flag & append `--cron` at the end of any of [these](#docker-command) commands. For example:
      ```sh
        sudo docker run -d \
        -v /path/to/mftp_config/env.py:/mftp/env.py \
        -v /path/to/mftp_config/token.json:/mftp/token.json \
        -v /path/to/mftp_config/credentials.json:/mftp/credentials.json \
        -v /path/to/mftp_config/mail_send_token.json:/mftp/mail_send_token.json \
        -v /path/to/mftp_config/mail_send_creds.json:/mftp/mail_send_creds.json \
        -v /path/to/mftp_config/.lsnif:/mftp/.lsnif \
        -v /path/to/mftp_config/.session:/mftp/.session \
        --name mftp \
        proffapt/mftp --gmail-api --cron
        ```
- Add the updated command with desired [cron expression](https://crontab.cronhub.io/) into your cronjob using [crontab -e](https://www.man7.org/linux/man-pages/man5/crontab.5.html)

<p align="right">(<a href="#top">back to top</a>)</p>

## Without using docker

To set up a local instance of the application without using docker, follow the steps below.

<div id="prerequisites-without-docker"></div>

### Prerequisites
The following requirements are to be satisfied for the project to function properly:
* [python3](https://www.python.org/downloads/) `>=python3.10`
  ```sh
  sudo apt update
  sudo apt install python3
  ```
* This project depends on [ERP Login module](https://github.com/proffapt/iitkgp-erp-login-pypi) by [Arpit Bhardwaj](https://github.com/proffapt) for the ERP Login workflow. Read its [documentation](https://github.com/proffapt/iitkgp-erp-login-pypi?tab=readme-ov-file#input) and setup your OTP fetching token mentioned in second point (`OTP_CHECK_INTERVAL`) of optional arguments.

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="installation-without-docker"></div>

### Installation

_Now that the environment has been set up and configured to properly compile and run the project, the next step is to download and configure the project locally on your system._
1. Clone the repository
   ```sh
   git clone https://github.com/metakgp/mftp
   cd mftp/mftp
   ```
2. Install required dependencies
   ```sh
   pip3 install -r requirements.txt
   ```
3. #### Sending Emails

> [!Note]
> Since, port `465` (SMTP with SSL) on campus LAN is blocked and if you want to host mftp on an internal server on the campus LAN, it will need another method then SMTP. <br/>
> However, it is preferred to use SMTP when hosting on external server as SMTP is the convenient of the two.
   
   The tool provides two methods of sending emails.

   - ##### Using SMTP
     > `--smtp`
     - [Create an app password](https://support.google.com/accounts/answer/185833?hl=en) for the senders' email.
     - After creating app password use it as your `FROM_EMAIL_PASS` value in  next step.
   - ##### Using GMAIL API
     > `--gmail-api`
     - Follow this [quick start guide](https://developers.google.com/gmail/api/quickstart/python) to configure _gmail api_ on the senders' mail.
     - After successfull configuration of gmail api, you can leave the value of `FROM_EMAIL_PASS` as it is in the next step.
     - Save the generated token as `mail_send_token.json`
       
4. #### Configuring environment variables

   - Copy `env.example.py` as `env.py`. It looks like this:
     ```python
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
     ```
   - Update the values inside the `double quotes` ("). **DO NOT CHANGE VAR NAMES.**

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->

<div id="usage-without-docker"></div>

### Usage

It is mandatory to provide either of the following flags to the execution command:
- `--smtp`: Using SMTP for sending mails
  ```python
  python3 mftp.py --smtp
  ```
  
- `--gmail-api`: Using GMAIL API for sending mails
  ```python
  python3 mftp.py --gmail-api
  ```

- `--ntfy`: Using NTFY for serving notifications
  ```python
  python3 mftp.py --ntfy
  ```

It is also possible to bypass the continuous loop - which executes the code after every 2 minutes - using the `--cron` argument:
```python
python3 mftp.py --smtp --cron
python3 mftp.py --gmail-api --cron
python3 mftp.py --ntfy --cron
```

<p align="right">(<a href="#top">back to top</a>)</p>
