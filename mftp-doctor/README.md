<div id="top"></div>

<!-- ABOUT THE PROJECT -->
## MFTP Doctor

[mftp-doctor.py](./mftp-doctor.py) periodically monitors the latest runtime logs of [mftp.py](../mftp/mftp.py). Analyses the logs and looks for errors. On encountering any errors it sends a notification to configured e-mail and ntfy topic, both done utilising [ntfy](https://docs.ntfy.sh/).

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

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="installation-with-docker"></div>

### Installation

1. Get the docker image
   
   You can get the docker image from either docker-hub or by buiilding it locally:
   - Pull from docker-hub
     ```sh
     sudo docker pull metakgporg/mftp-doctor
     ```
   - Build from Dockerfile
       * Clone the repository and cd into it
         ```sh
         git clone https://github.com/metakgp/mftp
         cd mftp/mftp-doctor
         ```
       * Build the image
         ```sh
         sudo docker build -t metakgporg/mftp-doctor .
         ```
2. Create a directory which will contain your env.py, name it as `doctor_config`
3. Follow the steps to [configure env variables](#configuring-environment-variables)

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="usage-with-docker"></div>

### Usage

#### Docker Compose

It is mandatory to provide the following `env variable` before the _docker-compose_ command.

- `DOCTOR_CONFIG`: Absolute path to `doctor_config` directory

```sh
sudo DOCTOR_CONFIG=/path/to/doctor_config docker-compose up -d
```

> [!Note] 
> All the environment variables mentioned above can be placed in a `.env` file and conveniently used via:
> `sudo docker-compose --env-file .env up -d`

<p align="right">(<a href="#top">back to top</a>)</p>

#### Docker Command

This container requires access to hosts' `docker.sock` to check logs of `mftp` container running on host and the **[env.py](#configuring-environment-variables)** file:
  ```sh
  sudo docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /path/to/doctor_config/env.py:/mftp-doctor/env.py \
  --name mftp-doctor \
  metakgporg/mftp-doctor
  ```

<p align="right">(<a href="#top">back to top</a>)</p>

#### As a cronjob

It is also possible to run these docker containers as a cronjob:
- ##### With Docker Compose
    - Provide `--cron` as the `DOCTOR_MODE` env variable. For example:
        ```sh
        sudo DOCTOR_CONFIG=/path/to/doctor_config DOCTOR_MODE=--cron docker-compose up -d
        ```

> [!Note] 
> All the environment variables mentioned above can be placed in a `.env` file and conveniently used via:
> `sudo docker-compose --env-file .env up -d`

- ##### With Docker Command
    - Append `--cron` at the end of [this](#docker-command) commands, as follows:
      ```sh
        sudo docker run -d \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v /path/to/doctor_config/env.py:/mftp-doctor/env.py \
        --name mftp-doctor \
        metakgporg/mftp-doctor --cron
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

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="installation-without-docker"></div>

### Installation

_Now that the environment has been set up and configured to properly compile and run the project, the next step is to download and configure the project locally on your system._
1. Clone the repository
   ```sh
   git clone https://github.com/metakgp/mftp
   cd mftp/mftp-doctor
   ```
2. Install required dependencies
   ```sh
   pip3 install -r requirements.txt
   ```
       
3. #### Configuring environment variables

   - Copy [env.example.py](./env.example.py) as `env.py`.
     > You can read about you can learn about ntfy from their docs: https://docs.ntfy.sh/
   - Update the values inside the `double quotes` ("). **DO NOT CHANGE VAR NAMES.**

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->

<div id="usage-without-docker"></div>

### Usage

It is straight forward to use this script, just run it using [supported version of python interpreter](#prerequisites-without-docker):
```python
python3 mftp-doctor.py
```

It is also possible to bypass the continuous loop - which executes the code after every 2 minutes - using the `--cron` argument:
```python
python3 mftp-doctor.py --cron
```

<p align="right">(<a href="#top">back to top</a>)</p>
