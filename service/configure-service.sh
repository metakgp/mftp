#!/bin/bash

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
BLUE=$(tput setaf 4)
WHITE=$(tput setaf 7)

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
echo -e "${GREEN}[+] ${BLUE}Configuring MFTP startup service${WHITE}"
if [ $(grep -q 'USERNAME' systemd/mftp.service && echo true || echo false) == "true" ]; then
  sed -i "s#USERNAME#${USER}#g" systemd/mftp.service
fi

if [ $(grep -q 'USERNAME' systemd/mftp.service && echo true || echo false)  == "true" ] ||\
  [ $(grep -q 'MFTPD' systemd/mftp-startup-service.sh && echo true || echo false)  == "true" ]; then
  sed -i "s#MFTPD#${MFTPD}#g" systemd/mftp-startup-service.sh
  sed -i "s#MFTPD#${MFTPD}#g" systemd/mftp.service
fi
  
if [ $(grep -q 'MAILSERVICE' systemd/mftp.service && echo true || echo false)  == "true" ] ||\ 
  [ $(grep -q 'MAILSERVICE' mftp-as-a-service.sh && echo true || echo false)  == "true" ]; then
  read -rp "${YELLOW}How do you want to send mail? ${WHITE}[${GREEN}smtp${WHITE}/${GREEN}gmail-api${WHITE}]${YELLOW}:${WHITE} " MAILSERVICE
  while [[ ! $MAILSERVICE =~ ^(smtp|gmail-api)$ ]]; do
    read -rp "${RED}Invalid option. ${YELLOW}Please enter '${GREEN}smtp${YELLOW}' or '${GREEN}gmail-api${YELLOW}':${WHITE} " MAILSERVICE 
  done
  echo -e "\n${YELLOW}[~] ${WHITE}You can change it later in ${GREEN}systemd/mftp.service${WHITE}\n"
  
  sed -i "s#MAILSERVICE#${MAILSERVICE:=smtp}#g" systemd/mftp.service
  sed -i "s#MAILSERVICE#${MAILSERVICE:=smtp}#g" mftp-as-a-service.sh
fi

echo -e "${GREEN}[+] ${BLUE}Setting MFTP startup service${WHITE}"
chmod 644 systemd/mftp.service
sudo cp systemd/mftp.service /etc/systemd/system/
sudo chmod 777 /etc/systemd/system/mftp.service
sudo systemctl daemon-reload

sudo systemctl enable mftp &&\
  echo -e "${GREEN}[+] ${BLUE}Enabled MFTP startup service${WHITE}" ||\
  echo -e "${RED}[ERROR] ${BLUE}Failed to enable MFTP startup service${WHITE}"

# Copying the service module to /usr/loca/bin
cp mftp-as-a-service.sh ~/.local/bin/mftp &&\
  echo -e "${GREEN}[+] ${BLUE}Installed MFTP as a service script${WHITE}" ||\
  echo -e "${RED}[ERROR] ${BLUE}Failed to install MFTP as a service script${WHITE}"

