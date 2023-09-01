#!/bin/bash

tail -n "${1:-25}" "$MFTPD"/logs.txt
