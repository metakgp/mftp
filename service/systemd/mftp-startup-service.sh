#!/bin/bash

# Sleeping till the network is not available
while ! ip route | grep -q default; do
  sleep 1
done

# Now starts the script
cd MFTPD || exit 1
export PYTHONPATH=$PYTHONPATH:$(python3 -m site --user-site)
python3 mftp.py --${1:-gmail-api} >>logs.txt 2>&1 &&\
  echo "[+] Successfully started MFTP server!" ||\
  echo "[ERROR] Failed to start MFTP server"
cd - >/dev/null || exit 1
