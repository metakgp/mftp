#!/bin/bash

RED=$(tput setaf 1)
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
      enable NUM             Enable mftp cronjob after every NUM minutes (default is 2 minutes)
      disable                Disable mftp cronjob
      
EOF
}

enable_cronjob() {
  period="$1"
  crontab -l > mftp-cron.tmp
  cron_expression="*/$period * * * *"
  echo "$cron_expression "$MFTPD/mftp-cron.py"" >> mftp-cron.tmp
  crontab mftp-cron.tmp
  rm mftp-cron.tmp

  echo "======================== <<: ENABLED CRONJOB :>> =========================" >> "$MFTPD"/logs.txt
}

disable_crontab() {
  crontab -l | grep -v "$MFTPD/mftp-cron.py" > mftp-cron.tmp
  crontab mftp-cron.tmp
  rm mftp-cron.tmp
}

case $1 in
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
  if [[ "$2" == "enable" ]]; then
    if [[ "$3" =~ ^[0-9]+$ ]]; then
      enable_cronjob $3
    elif [[ -z "$3" ]]; then
      enable_cronjob 2
    else
      echo -e "${RED}[ERROR] ${WHITE} Invalid argument for \`${YELLOW}mftp cronjob enable${WHITE}\`"
    fi
  elif [[ "$2" == "disable" ]]; then
    disable_crontab
  else 
    echo -e "${RED}[ERROR] ${WHITE} Invalid argument for \`${YELLOW}mftp cronjob${WHITE}\`"
  fi
  ;;
"*")
  echo -e "${RED}[ERROR] ${WHITE} Invalid argument for \`${YELLOW}mftp${WHITE}\`"
esac
