#!/bin/bash

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
BLUE=$(tput setaf 4)
WHITE=$(tput setaf 7)

# Copying the service module to /usr/loca/bin
cp mftp-as-a-service.sh ~/.local/bin/mftp &&\
  echo -e "${GREEN}[+] ${BLUE}Installed MFTP as a service script${WHITE}" ||\
  echo -e "${RED}[ERROR] ${BLUE}Failed to install MFTP as a service script${WHITE}"


# Detecting the shell config file
if [[ "$(basename $SHELL)" == "bash" ]]; then
  SHELL_RC=~/.bashrc
elif [[ "$(basename $SHELL)" == "zsh" ]]; then
  SHELL_RC=~/.zshrc
fi

DIRECTORY_CONFIGURED=$(grep -q 'MFTPD' "$SHELL_RC" && echo true || echo false)
if [ "$DIRECTORY_CONFIGURED" == "false" ]; then
  # Storing the location where mftp is installed to be used in service module
  echo -e "${GREEN}[+] ${BLUE}Configuring MFTP Directory location${WHITE}"
  echo "export MFTPD=$(dirname $(pwd))" >> "$SHELL_RC"
else
  echo -e "${YELLOW}[-] ${BLUE}MFTP Directory already configured${WHITE}"
fi
source "$SHELL_RC"

# Only for linux
# Configuring startup service for MFTP
if [ $(grep -q 'USERNAME' systemd/mftp.service && echo true || echo false)  == "true" ] ||
  [ $(grep -q 'USERNAME' systemd/mftp-startup-service.sh && echo true || echo false) == "true" ]; then
  echo -e "${GREEN}[+] ${BLUE}Configuring MFTP startup service${WHITE}"
  sed -i "s#USERNAME#${USER}#g" systemd/mftp.service
  sed -i "s#MFTPD#${MFTPD}#g" systemd/mftp.service
  sed -i "s#MFTPD#${MFTPD}#g" systemd/mftp-startup-service.sh
else
  echo -e "${YELLOW}[-] ${BLUE}MFTP startup service already configured${WHITE}"
fi

if [ ! -f /etc/systemd/system/mftp.service ]; then
  echo -e "${GREEN}[+] ${BLUE}Setting MFTP startup service${WHITE}"
  chmod 644 systemd/mftp.service
  sudo cp systemd/mftp.service /etc/systemd/system/
  sudo chmod 777 /etc/systemd/system/mftp.service
  sudo systemctl daemon-reload
else
  echo -e "${YELLOW}[-] ${BLUE}MFTP startup service already set${WHITE}"
fi

if [ "$(systemctl is-enabled mftp)" == "disabled" ]; then
  echo -e "${GREEN}[+] ${BLUE}Enabling MFTP startup service${WHITE}"
  sudo systemctl enable mftp
else
  echo -e "${YELLOW}[-] ${BLUE}MFTP startup service already enabled${WHITE}"
fi
