#!/bin/bash

# Copying the service module to /usr/loca/bin
cp mftp-as-a-service.sh /usr/local/bin/mftp

# Detecting the shell config file
if [[ "$(basename $SHELL)" == "bash" ]]; then
  SHELL_RC=~/.bashrc
elif [[ "$(basename $SHELL)" == "zsh" ]]; then
  SHELL_RC=~/.zshrc
fi

DIRECTORY_CONFIGURED=$(grep -q 'MFTPD' "$SHELL_RC" && echo true || echo false)
if [ "$DIRECTORY_CONFIGURED" == "false" ]; then
  # Storing the location where mftp is installed to be used in service module
  echo "export MFTPD=$(dirname $(pwd))" >> "$SHELL_RC"
fi
source "$SHELL_RC"

# Only for linux
# Configuring startup service for MFTP
sed -i "s#MFTPD#${MFTPD}#g" systemd/mftp.service
sed -i "s#USERNAME#${USER}#g" systemd/mftp.service
sed -i "s#MFTPD#${MFTPD}#g" systemd/mftp-startup-service.sh

if [ ! -f /etc/systemd/system/mftp.service ]; then
  echo -e "${GREEN}[+] ${BLUE}Creating MFTP startup service${WHITE}"
  chmod 644 systemd/mftp.service
  sudo cp systemd/mftp.service /etc/systemd/system/
  sudo chmod 777 /etc/systemd/system/mftp.service
  sudo systemctl daemon-reload
else
  echo -e "${YELLOW}[-] ${BLUE}MFTP startup service already created${WHITE}"
fi

if [ "$(systemctl is-enabled mftp)" == "disabled" ]; then
  echo -e "${GREEN}[+] ${BLUE}Enabling MFTP startup service${WHITE}"
  sudo systemctl enable mftp
else
  echo -e "${YELLOW}[-] ${BLUE}MFTP startup service already enabled${WHITE}"
fi
