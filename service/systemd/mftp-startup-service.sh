#!/bin/bash

# Sleeping till the network is not available
while ! /usr/bin/curl -Is https://google.com > /dev/null; do
  sleep 1
done

# Now starts the script
cd MFTPD/mftp || exit 1
export PYTHONPATH=$PYTHONPATH:$(python3 -m site --user-site)
python3 mftp.py "--${1}" >>logs.txt 2>&1 &&\
  echo "[+] Successfully started MFTP server!" ||\
  echo "[ERROR] Failed to start MFTP server"
cd - >/dev/null || exit 1
