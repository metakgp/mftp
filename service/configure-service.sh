#!/bin/bash

rm -f mftp-service-aliases
for script in scripts/*; do 
  echo "alias mftp.$(basename ${script%.sh})=$(pwd)/${script}" >> mftp-service-aliases
done
echo "export MFTPD=$(dirname $(pwd))" >> mftp-service-aliases

cat mftp-service-aliases

if [[ "$(basename $SHELL)" == "bash" ]]; then
  ALIAS_CONFIGURED=$(grep -q 'mftp-service-aliases' ~/.bashrc && echo true || echo false)
  SHELL_RC=~/.bashrc
elif [[ "$(basename $SHELL)" == "zsh" ]]; then
  ALIAS_CONFIGURED=$(grep -q 'mftp-service-aliases' ~/.zshrc && echo true || echo false)
  SHELL_RC=~/.zshrc
fi

if [ "$ALIAS_CONFIGURED" == "false" ]; then
  echo "source $(pwd)/mftp-service-aliases" >> "$SHELL_RC"
fi
source "$SHELL_RC"

KERNEL=$(uname -s)
if [[ "$KERNEL" == "Linux" ]]; then
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
fi

