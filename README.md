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
        - [As a cronjob](#as-a-cronjob)
- [Without using docker](#without-using-docker)
    - [Supports](#supports)
    - [Prerequisites](#prerequisites-without-docker)
    - [Installation](#installation-without-docker)
    - [Usage](#usage-without-docker)
- [Maintainer(s)](#maintainers)
- [Contact](#contact)
- [Additional documentation](#additional-documentation)

</details>

<!-- ABOUT THE PROJECT -->
## About The Project

MFTP continuously monitors the CDC Noticeboard and forwards incoming notices to the configured email address, whether it's an individual account or a Google Group. It is also available as a service and as a cronjob on linux systems along with a [heath checkup utility](./mftp-doctor) to monitor and notify for any errors.

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
* [For mftp](https://github.com/metakgp/mftp/blob/main/mftp/README.md#prerequisites)
* [For mftp doctor](https://github.com/metakgp/mftp/blob/main/mftp-doctor/README.md#prerequisites)

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="installation-with-docker"></div>

### Installation

1. Clone the repository and cd into it
   ```sh
   git clone https://github.com/metakgp/mftp
   cd mftp
   ```
2. Follow the [installation steps for mftp with docker](https://github.com/metakgp/mftp/blob/main/mftp/README.md#installation)
3. Follow the [installation steps for mftp doctor with docker](https://github.com/metakgp/mftp/blob/main/mftp-doctor/README.md#installation)

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="usage-with-docker"></div>

### Usage

<img width="1200" alt="image" src="https://github.com/metakgp/mftp/assets/86282911/f06c46b6-0471-49c2-bd6b-b7bdf765a277">

It is mandatory to provide all of the following `env variables` before the _docker-compose_ command.
- `MFTP_CONFIG`: Absolute path to `mftp_config` directory
- `DOCTOR_CONFIG`: Absolute path to `doctor_config` directory
- `MFTP_MODE`: Mode of sending mail - **--smtp**, **--gmail-api** or **--ntfy**

```sh
sudo MFTP_CONFIG=/path/to/mftp_config DOCTOR_CONFIG=/path/to/doctor_config MFTP_MODE="--smtp" docker-compose up -d # Using SMTP for sending mails
```

```sh
sudo MFTP_CONFIG=/path/to/mftp_config DOCTOR_CONFIG=/path/to/doctor_config MFTP_MODE="--gmail-api" docker-compose up -d # Using Gmail API for sending mails
```

```sh
sudo MFTP_CONFIG=/path/to/mftp_config DOCTOR_CONFIG=/path/to/doctor_config MFTP_MODE="--ntfy" docker-compose up -d # Using NTFY for serving notifications
```

> [!NOTE]
> There also is `DOCTOR_MODE` as one of the environment variables, which is optional and considers one value only `--cron`. We will use it in the sub-section just next.

#### As a cronjob

It is also possible to run these docker containers as a cronjob:

- Comment out the line `restart: unless-stopped` in [docker-compose.yml](./docker-compose.yml)
- Append ` --cron` into the `MFTP_MODE` env variable and set `DOCTOR_MODE` to `--cron` as well. As follows:
    * Using Cronjob to run containers and SMTP to send mails
      ```sh
      sudo MFTP_CONFIG=/path/to/mftp_config DOCTOR_CONFIG=/path/to/doctor_config MFTP_MODE="--smtp --cron" DOCTOR_MODE="--cron" docker-compose up -d
      ```
    * Using Cronjob to run containers and Gmail API to send mails
      ```sh
      sudo MFTP_CONFIG=/path/to/mftp_config DOCTOR_CONFIG=/path/to/doctor_config MFTP_MODE="--gmail-api --cron" DOCTOR_MODE="--cron" docker-compose up -d
      ```
    * Using Cronjob to run containers and NTFY to serve notifications
      ```sh
      sudo MFTP_CONFIG=/path/to/mftp_config DOCTOR_CONFIG=/path/to/doctor_config MFTP_MODE="--ntfy --cron" DOCTOR_MODE="--cron" docker-compose up -d
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

* [For mftp](https://github.com/metakgp/mftp/blob/main/mftp/README.md#prerequisites-1)
* [For mftp doctor](https://github.com/metakgp/mftp/blob/main/mftp-doctor/README.md#prerequisites-1)

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="installation-without-docker"></div>

### Installation

_Now that the environment has been set up and configured to properly compile and run the project, the next step is to download and configure the project locally on your system._
1. Clone the repository
   ```sh
   git clone https://github.com/metakgp/mftp
   cd mftp
   ```
2. Install required dependencies
   ```sh
   pip3 install -r requirements.txt
   ```
3. Follow the [installation steps for mftp](https://github.com/metakgp/mftp/blob/main/mftp/README.md#installation-1)
4. Follow the [installation steps for mftp doctor](https://github.com/metakgp/mftp/blob/main/mftp-doctor/README.md#installation-1)
5. ##### Configure the mftp service
   For linux systems, MFTP & MFTP Doctor are available as a service and as cronjob. To configure them, execute the following commands after navigating into the root directory of the project (inside the mftp folder).
   ```sh
   cd service/
   ./configure-service.sh
   ```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

<div id="usage-without-docker"></div>

### Usage

<img width="1200" alt="image" src="https://user-images.githubusercontent.com/86282911/265526168-8edc1b6f-4326-4d90-b2e5-f9742d0bed6e.png">

After [configuring MFTP as a service](#configure-the-mftp-service), you can use the `mftp` command with several options to interact with the tool as a service.<br/> Following is the help menu for the service.

```graphql
Usage: mftp [COMMAND] [OPTIONS]

Command:
  -h, --help                   Display this help and exit
  logs [OPTIONS]               Display last 25 lines of mftp log file
    Options:
      clear                    Clear the mftp log file
      NUM                      Display last NUM lines of mftp log file
  disable                      Disable mftp service
  enable                       Enable mftp service
  status                       Check status of mftp service
  restart                      Restart mftp service
  stop                         Stop mftp service
  start                        Start mftp service

  cronjob [OPTIONS]            Use mftp as a cronjob
    Options:
      enable [NUM]             Enable mftp cronjob after every NUM minutes (default is 2 minutes)
      disable                  Disable mftp cronjob
      status                   Check status of mftp cronjob

  doctor [OPTIONS]             Use mftp doctor as a cronjob
    Options:
      enable [NUM]             Enable doctor cronjob after every NUM minutes (default is 2 minutes)
      disable                  Disable doctor cronjob
      status                   Check status of doctor cronjob
      logs [OPTIONS]           Display last 25 lines of doctor log file
        Options:
          clear                Clear the doctor log file
          NUM                  Display last NUM lines of doctor log file
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
