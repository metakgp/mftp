#!/bin/bash

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
WHITE=$(tput setaf 7)

usage() {
  cat <<-EOF 
Usage: ${0##*/} [OPTIONS]

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
      
EOF
}

enable_cronjob() {
  period="$1"
  crontab -l > mftp-cron.tmp
  cron_expression="*/${period} * * * *"
  echo "$cron_expression cd ${MFTPD}; $(which python3) mftp-cron.py --MAILSERVICE >>logs.txt 2>&1" >> mftp-cron.tmp
  crontab mftp-cron.tmp
  rm mftp-cron.tmp
  echo "===================== <<: ENABLED CRONJOB :>> ======================" >> "$MFTPD"/logs.txt
}

disable_cronjob() {
  crontab -l | grep -v "mftp-cron.py" | crontab -
  echo "==================== <<: DISABLED CRONJOB :>> ======================" >> "$MFTPD"/logs.txt
}

case "$1" in
"-h" | "--help")
  usage
  exit 0
  ;;
"logs")
  logfile="${MFTPD}/logs.txt"
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
  echo "======================== <<: RESTARTED :>> =========================" >> "$MFTPD"/logs.txt
  sudo systemctl restart mftp
  ;;
"stop")
  sudo systemctl stop mftp &&\
  echo "========================= <<: STOPPED :>> ==========================" >> "$MFTPD"/logs.txt
  ;;
"start")
  sudo systemctl start mftp
  ;;
"cronjob")
  # Getting the status of configuration of mftp cronjob
  if ! crontab -l | grep -q "mftp-cron.py"; then
    cron_enabled="False"
  else
    cron_enabled="True"
  fi
  
  case "$2" in
  "enable")
    if [[ "$3" =~ ^[0-9]+$ ]] || [[ -z "$3" ]]; then
      if [[ "$cron_enabled" == "False" ]]; then
        enable_cronjob "${3:-2}"
        echo -e "${GREEN}[+] ${WHITE}Cronjob configured!"
      else
        echo -e "${YELLOW}[~] ${WHITE}Cronjob already configured"
      fi
    else
      echo -e "${RED}[ERROR] ${WHITE} Invalid argument for \`${YELLOW}mftp cronjob enable${WHITE}\`"
    fi
    ;;
  "disable")
    disable_cronjob
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
