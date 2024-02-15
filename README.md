<div id="top"></div>

<!-- PROJECT SHIELDS -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links-->
<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![Wiki][wiki-shield]][wiki-url]

</div>

<br />
<div align="center">
  <!-- PROJECT LOGO -->
  <!-- <a href="https://github.com/metakgp/MFTP">
    <img width="140" alt="image" src="https://user-images.githubusercontent.com/86282911/206632284-cb260f57-c612-4ab5-b92b-2172c341ab23.png">
  </a> -->

  <h3 align="center">MFTP - My Freaking Training & Placements</h3>

  <p align="center">
    <i>CDC Noticeboard on Your Mail: Where Automatic Updates Turn Chaos into Pleasure!</i>
    <br />
    <a href="https://github.com/metakgp/MFTP/issues">Report Bug</a>
    ·
    <a href="https://github.com/metakgp/MFTP/issues">Request Feature</a>
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
<summary>Table of Contents</summary>

- [About The Project](#about-the-project)
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
    - [Supports](#supports)
    - [Prerequisites](#prerequisites-without-docker)
    - [Installation](#installation-without-docker)
    - [Usage](#usage-without-docker)
        - [Using MFTP as a Service](#using-mftp-as-a-service)
- [Maintainer(s)](#maintainers)
- [Contact](#contact)
- [Additional documentation](#additional-documentation)

</details>

<!-- ABOUT THE PROJECT -->
## About The Project

<div align="center">

  <a href="https://github.com/metakgp/MFTP">
	<img width="1200" alt="image" src="https://user-images.githubusercontent.com/86282911/265526168-8edc1b6f-4326-4d90-b2e5-f9742d0bed6e.png">
  </a>
</div>
<br/>

MFTP continuously monitors the CDC Noticeboard and forwards incoming notices to the configured email address, whether it's an individual account or a Google Group. It is also available as a service and as a cronjob on linux systems.

> [!Warning]
> This tool is completely legal, but the way you use it can get you into legal trouble. Some things you **cannot** do are:
> - Use this tool to send CDC notifications to **any non-KGPian**.
> - Use this tool on a wide scale or publicise its running instance without consent from the Placement Committee.
>
> Please use this tool responsibly and within ethical and legal bounds. We do not promote violating company policies or laws. The extent of the punishment may very **from disciplinary action by the institute to blacklisting from CDC process**.

<p align="right">(<a href="#top">back to top</a>)</p>

## Using docker

To set up a local instance of the application using docker, follow the steps below.

<div id="prerequisites-with-docker"></div>

### Prerequisites
The following requirements are to be satisfied for the project to function properly:
* [docker](https://docs.docker.com/get-docker/)
* This project depends on [ERP Login module](https://github.com/proffapt/iitkgp-erp-login-pypi) by [Arpit Bhardwaj](https://github.com/proffapt) for the ERP Login workflow. Read its [documentation](https://github.com/proffapt/iitkgp-erp-login-pypi?tab=readme-ov-file#input) and setup your OTP fetching token mentioned in second point (`OTP_CHECK_INTERVAL`) of optional arguments.

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
3. Follow the steps to [configure mail sending](#sending-emails)
4. Follow the steps to [configure env variables](#configuring-environment-variables)

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="usage-with-docker"></div>

### Usage

#### Docker Compose

It is mandatory to provide both of the following `env variables` before the _docker-compose_ command.
- `MFTP_CONFIG`: Absolute path to `mftp_config` directory
- `MFTP_MODE`: Mode of sending mail - **--smtp** or **--gmail-api**

```sh
sudo CONFIG=/path/to/mftp_config MFTP_MODE=--smtp docker-compose up -d # Using SMTP for sending mails
```

```sh
sudo CONFIG=/path/to/mftp_config MFTP_MODE=--gmail-api docker-compose up -d # Using Gmail API for sending mails
```

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

#### As a cronjob

It is also possible to run these docker containers as a cronjob:
- ##### With Docker Compose
    - Comment out the line `restart: unless-stopped`
    - Append ` --cron` into the `MFTP_MODE` env variable. For example:
        * Using Cronjob to run container and SMTP to send mails
          ```sh
          sudo CONFIG=/path/to/mftp_config MFTP_MODE="--smtp --cron" docker-compose up -d
          ```
        * Using Cronjob to run container and Gmail API to send mails
          ```sh
          sudo CONFIG=/path/to/mftp_config MFTP_MODE="--gmail-api --cron" docker-compose up -d
          ```
- ##### With Docker Command
    - Append `--cron` at the end of any of [these](#docker-command) commands. For example:
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
        proffapt/mftp --gmail-api --cron
        ```
- Add the updated command with desired [cron expression](https://crontab.cronhub.io/) into your cronjob using [crontab -e](https://www.man7.org/linux/man-pages/man5/crontab.5.html)

<p align="right">(<a href="#top">back to top</a>)</p>

## Without using docker

To set up a local instance of the application without using docker, follow the steps below.

<div id="supports"></div>

### Supports:
1. Shells
    * `bash`
    * `zsh`
2. OS(s)
    * any `*nix`[`GNU+Linux` and `Unix`]

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="prerequisites-without-docker"></div>

### Prerequisites
The following requirements are to be satisfied for the project to function properly:
* [python3](https://www.python.org/downloads/) `>=python3.10`
  ```sh
  sudo apt update
  sudo apt install python3
  ```
* This project depends on [ERP Login module](https://github.com/proffapt/iitkgp-erp-login-pypi) by [Arpit Bhardwaj](https://github.com/proffapt) for the ERP Login workflow. Read its [documentation](https://github.com/proffapt/iitkgp-erp-login-pypi/blob/main/README.md) and setup your environment for it.

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
     # ERP Credentials
     ROLL_NUMBER = "XXYYXXXXX" # Institute Roll Number
     PASSWORD = "**********" # ERP Password
     SECURITY_QUESTIONS_ANSWERS = { # ERP Secret Questions and their Answers
         "Q1" : "A1",
         "Q2" : "A2",
         "Q3" : "A3",
     }

     # EMAIL CREDENTIALS
     FROM_EMAIL = "abc@gmail.com" # Notification Sender Email-id
     FROM_EMAIL_PASS = "**********" # App password for the above email-id

     # OTHER PARAMETERS
     BCC_EMAIL_S = ["xyz@googlegroups.com", "abc@googlegroups.com"] # Multiple mails for bcc
     # BCC_EMAIL_S = ["xyz@googlegroups.com"] # This is how you can set single mail in a list
     KEEP_TOKEN_ALIVE_EMAIL = "xyz@gmail.com" # Email-id to send regular emails to keep the token alive
     ```
   - Update the values inside the `double quotes` ("). **DO NOT CHANGE VAR NAMES.**
5. Configure the mftp service
   For linux systems MFTP is available as a service and as a cronjob. To configure it, execute the following commands after navigating into the root directory of the project (inside the mftp folder).
   ```sh
   cd service/
   ./configure-service.sh
   ```

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->

<div id="usage-without-docker"></div>

### Usage

It is mandatory to provide either of the following flags to the execution command.
- `--smtp`: Using SMTP for sending mails
  ```python
  python3 mftp.py --smtp
  ```
  
- `--gmail-api`: Using GMAIL API for sending mails
  ```python
  python3 mftp.py --gmail-api
  ```

#### Using MFTP as a Service

After [configuring MFTP as a service](#setup-mftp-as-a-service), you can use the `mftp` command with several options to interact with the tool as a service.<br/> Following is the help menu for the service.

```graphql
Usage: mftp [OPTIONS]

Options:
  -h, --help               Display this help and exit
  logs [OPTIONS]           Display last 25 lines of log file
    Options:
      clear                 Clear the log file
      NUM                   Display last NUM lines of log file
  disable                  Disable mftp service
  enable                   Enable mftp service
  status                   Check status of mftp service
  restart                  Restart mftp service
  stop                     Stop mftp service
  start                    Start mftp service
  cronjob [OPTIONS]        Use mftp as a cronjob
    Options:
      enable [NUM]             Enable mftp cronjob after every NUM minutes (default is 2 minutes)
      disable                  Disable mftp cronjob
      status                   Check status of mftp cronjob
```

<p align="right">(<a href="#top">back to top</a>)</p>

## Maintainer(s)

- [Arpit Bhardwaj](https://github.com/proffapt)

<p align="right">(<a href="#top">back to top</a>)</p>

## Contact

<p>
📫 Metakgp -
<a href="https://bit.ly/metakgp-slack">
  <img align="center" alt="Metakgp's slack invite" width="22px" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/slack.svg" />
</a>
<a href="mailto:metakgp@gmail.com">
  <img align="center" alt="Metakgp's email " width="22px" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/gmail.svg" />
</a>
<a href="https://www.facebook.com/metakgp">
  <img align="center" alt="metakgp's Facebook" width="22px" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/facebook.svg" />
</a>
<a href="https://www.linkedin.com/company/metakgp-org/">
  <img align="center" alt="metakgp's LinkedIn" width="22px" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linkedin.svg" />
</a>
<a href="https://twitter.com/metakgp">
  <img align="center" alt="metakgp's Twitter " width="22px" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/twitter.svg" />
</a>
<a href="https://www.instagram.com/metakgp_/">
  <img align="center" alt="metakgp's Instagram" width="22px" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/instagram.svg" />
</a>
</p>

<p align="right">(<a href="#top">back to top</a>)</p>

## Additional documentation

  - [License](/LICENSE)
  - [Code of Conduct](/.github/CODE_OF_CONDUCT.md)
  - [Security Policy](/.github/SECURITY.md)
  - [Contribution Guidelines](/.github/CONTRIBUTING.md)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

[contributors-shield]: https://img.shields.io/github/contributors/metakgp/MFTP.svg?style=for-the-badge
[contributors-url]: https://github.com/metakgp/MFTP/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/metakgp/MFTP.svg?style=for-the-badge
[forks-url]: https://github.com/metakgp/MFTP/network/members
[stars-shield]: https://img.shields.io/github/stars/metakgp/MFTP.svg?style=for-the-badge
[stars-url]: https://github.com/metakgp/MFTP/stargazers
[issues-shield]: https://img.shields.io/github/issues/metakgp/MFTP.svg?style=for-the-badge
[issues-url]: https://github.com/metakgp/MFTP/issues
[license-shield]: https://img.shields.io/github/license/metakgp/MFTP.svg?style=for-the-badge
[license-url]: https://github.com/metakgp/MFTP/blob/master/LICENSE
[wiki-shield]: https://custom-icon-badges.demolab.com/badge/metakgp_wiki-grey?logo=metakgp_logo&style=for-the-badge
[wiki-url]: https://wiki.metakgp.org
