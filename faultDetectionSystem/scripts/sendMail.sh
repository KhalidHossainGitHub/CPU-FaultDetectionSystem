#!/bin/bash

# Ensure correct number of arguments
if [ $# -ne 2 ]; then
  echo "Error: You must provide exactly two arguments (CPU usage and process name)"
  exit 1
fi

TIMESTAMP=$1
CPU_USAGE=$2
EMAIL_RECIPIENT="jay.savaliya@ontariotechu.net"  # Replace with the recipient's email

# Check if msmtp is available
if ! command -v msmtp &>/dev/null; then
  echo "Error: msmtp is not installed. Please install msmtp to send emails."
  exit 1
fi

# Prepare the email content
EMAIL_SUBJECT="CPU FAULT ON LINUX SYSTEM"
EMAIL_BODY="FAULT DETECTED at $TIMESTAMP - CPU Usage $CPU_USAGE%.\n\nPlease check if you would like to kill a process that uses high amount of cpu resouces by going into Linux in the terminal, naviagting to faultDetectionSystem/scripts directory and type \"./highCPUProcessKiller\"."

# Send the email using msmtp
echo -e "Subject: $EMAIL_SUBJECT\n\n$EMAIL_BODY" | msmtp "$EMAIL_RECIPIENT"

# Check if msmtp was successful
if [ $? -eq 0 ]; then
  echo "Email sent successfully."
else
  echo "Error: Failed to send email."
  exit 1
fi

