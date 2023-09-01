#!/bin/bash

rm -f mftp-service-aliases
for script in *; do 
  if [[ "$script" != "setup-service.sh" ]]; then
    echo "alias mftp.${script%.sh}=$(pwd)/${script}" >> mftp-service-aliases
  fi
done
echo "export MFTPD=$(dirname $(pwd))" >> mftp-service-aliases

cat mftp-service-aliases

ALIAS_CONFIGURED=$(grep -q 'mftp-service-aliases' ~/.bashrc && echo true || echo false)
if [ "$ALIAS_CONFIGURED" == "false" ]; then
	echo "source $(pwd)/mftp-service-aliases" >> ~/.bashrc
	source ~/.bashrc
fi
