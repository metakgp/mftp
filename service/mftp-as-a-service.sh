#!/bin/bash

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
WHITE=$(tput setaf 7)

usage() {
  cat <<-EOF 
Usage: ${0##*/} [COMMAND] [OPTIONS]

Command:
  -h, --help                   Display this help and exit
  logs [OPTIONS]               Display last 25 lines of log file
    Options:
      clear                    Clear the log file
      NUM                      Display last NUM lines of log file
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

EOF
}

enable_cronjob() {
  period="$1"
  crontab -l > "${2}-cron.tmp"
  cron_expression="*/${period} * * * *"
  echo "$cron_expression cd ${MFTPD}/${2}; $(which python3) ${2}.py --cron --MAILSERVICE >>logs.txt 2>&1" >> "${2}-cron.tmp"
  crontab "${2}-cron.tmp"
  rm "${2}-cron.tmp"
  echo "===================== <<: ENABLED CRONJOB :>> ======================" >> "${MFTPD}/${2}"/logs.txt
}

disable_cronjob() {
  crontab -l | grep -v "${1}.py" | crontab -
  echo "==================== <<: DISABLED CRONJOB :>> ======================" >> "${MFTPD}/${1}"/logs.txt
}

case "$1" in
"-h" | "--help")
  usage
  exit 0
  ;;
"logs")
  logfile="${MFTPD}/mftp/logs.txt"
  if [[ "$2" == "clear" ]]; then
    echo "" > "$logfile"
    exit 0
  elif [[ "$2" =~ ^[0-9]+$ ]] || [[ -z "$2" ]]; then
    if [ -f "$logfile" ]; then
      tail -f -n "${2:-25}" "$logfile"
    else
      echo -e "${RED}[ERROR] ${WHITE}Log file does not exist"
    fi
  else 
    echo -e "${RED}[ERROR] ${WHITE} Invalid argument for \`${YELLOW}mftp logs${WHITE}\`"
  fi
  ;;
"disable")
  sudo systemctl disable mftp
  ;;
"enable")
  sudo systemctl enable mftp
  ;;
"status")
  sudo systemctl status mftp
  ;;
"restart")
  echo "======================== <<: RESTARTED :>> =========================" >> "$MFTPD"/mftp/logs.txt
  sudo systemctl restart mftp
  ;;
"stop")
  sudo systemctl stop mftp &&\
  echo "========================= <<: STOPPED :>> ==========================" >> "$MFTPD"/mftp/logs.txt
  ;;
"start")
  sudo systemctl start mftp
  ;;
"doctor")
  # Getting the status of configuration of mftp-doctor cronjob
  if ! crontab -l | grep -q "mftp-doctor.py"; then
    doctor_cron_enabled="False"
  else
    doctor_cron_enabled="True"
  fi

  case "$2" in
  "enable")
    if [[ "$3" =~ ^[0-9]+$ ]] || [[ -z "$3" ]]; then
      if [[ "$doctor_cron_enabled" == "False" ]]; then
        enable_cronjob "${3:-2}" "mftp-doctor"
        echo -e "${GREEN}[+] ${WHITE}Doctor Cron configured!"
      else
        echo -e "${YELLOW}[~] ${WHITE}Doctor Cron already configured"
      fi
    else
      echo -e "${RED}[ERROR] ${WHITE} Invalid argument for \`${YELLOW}mftp cronjob enable${WHITE}\`"
    fi
    ;;
  "disable")
    if [[ "$doctor_cron_enabled" == "True" ]]; then
      disable_cronjob "mftp-doctor"
      echo -e "${GREEN}[+] ${WHITE}Doctor Cron disabled!"
    else
      echo -e "${YELLOW}[~] ${WHITE}Doctor Cron already disabled"
    fi
    ;;
  "status")
    if [[ "$doctor_cron_enabled" == "True" ]]; then
      echo -e "${GREEN}[+]${WHITE} Doctor Cron is configured!"
    else
      echo -e "${RED}[-]${WHITE} Doctor Cron is not configured"
    fi 
    ;;
  esac
  ;;
"cronjob")
  # Getting the status of configuration of mftp cronjob
  if ! crontab -l | grep -q "mftp.py"; then
    cron_enabled="False"
  else
    cron_enabled="True"
  fi
  
  case "$2" in
  "enable")
    if [[ "$3" =~ ^[0-9]+$ ]] || [[ -z "$3" ]]; then
      if [[ "$cron_enabled" == "False" ]]; then
        enable_cronjob "${3:-2}" "mftp"
        echo -e "${GREEN}[+] ${WHITE}Cronjob configured!"
      else
        echo -e "${YELLOW}[~] ${WHITE}Cronjob already configured"
      fi
    else
      echo -e "${RED}[ERROR] ${WHITE} Invalid argument for \`${YELLOW}mftp cronjob enable${WHITE}\`"
    fi
    ;;
  "disable")
    if [[ "$cron_enabled" == "True" ]]; then
      disable_cronjob "mftp"
      echo -e "${GREEN}[+] ${WHITE}Doctor Cron disabled!"
    else
      echo -e "${YELLOW}[~] ${WHITE}Doctor Cron already disabled"
    fi
    ;;
  "status")
    if [[ "$cron_enabled" == "True" ]]; then
      echo -e "${GREEN}[+] ${WHITE}Cronjob is configured!"
    else
      echo -e "${RED}[-] ${WHITE} Cronjob is not configured"
    fi 
    ;;
  "*")
    echo -e "${RED}[ERROR] ${WHITE} Invalid argument for \`${YELLOW}mftp cronjob${WHITE}\`"
  esac
  ;;
"*")
  echo -e "${RED}[ERROR] ${WHITE} Invalid argument for \`${YELLOW}mftp${WHITE}\`"
esac
