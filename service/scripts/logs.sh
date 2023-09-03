#!/bin/bash

if [[ "$1" == "clear" ]]; then
  rm -f "$MFTPD"/logs.txt
  exit 0
fi

tail -n "${1:-25}" "$MFTPD"/logs.txt

