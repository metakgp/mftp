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

if [ -n "$mftpID" ]; then
	echo -e "${YELLOW}[-] ${BLUE}MFTP is already running on PID : ${RED}${mftpID}${WHITE}"
	exit
fi

cd "$MFTPD" || exit 1
setsid python3 mftp.py --${1:-gmail-api} >>logs.txt 2>&1 &
echo -e "${GREEN}[+] ${BLUE}Successfully started MFTP server!${WHITE}"
cd - >/dev/null || exit 1
