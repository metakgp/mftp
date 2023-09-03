#!/bin/bash

rm -f mftp-service-aliases
for script in scripts/*; do 
  echo "alias mftp.${script%.sh}=$(pwd)/${script}" >> mftp-service-aliases
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
  source "$SHELL_RC"
fi
