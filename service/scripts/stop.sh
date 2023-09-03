#!/bin/bash

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
BLUE=$(tput setaf 4)
WHITE=$(tput setaf 7)

KERNEL=$(uname -s)
if [[ "$KERNEL" == "Darwin" ]]; then
  mftpID=$(ps -a | grep -i "mftp.py" | grep -v "grep" | head -n 1 | awk '{print $1}')
else
  mftpID=$(ps -aux | grep -i "mftp.py" | grep -v "grep" | head -n 1 | awk '{print $2}')
fi

if [ -z "$mftpID" ]; then
	echo -e "${YELLOW}[-] ${BLUE}MFTP is not running currently${WHITE}"
	exit
fi

sudo kill -SIGTERM "$mftpID"
echo "======================== <<: STOPPED :>> =========================" >> "$MFTPD"/logs.txt
echo -e "${GREEN}[+] ${BLUE}Successfully stopped MFTP server at PID${WHITE}[${RED}${mftpID}${WHITE}]${BLUE}!${WHITE}"
