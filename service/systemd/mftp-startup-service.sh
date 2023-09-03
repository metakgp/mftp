#!/bin/bash

cd MFTPD || exit 1
setsid python3 mftp.py --${1:-gmail-api} >>logs.txt 2>&1 &
echo "[+] Successfully started MFTP server!"
cd - >/dev/null || exit 1
