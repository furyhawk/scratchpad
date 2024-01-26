#!/bin/bash

if [ -n "$SUDO_USER" ] || [ -n "$SUDO_UID" ]; then
    echo "This script was executed with sudo."
    echo "Use './autorun.sh' instead of 'sudo ./autorun.sh'"
    echo "Exiting..."
    exit 1
fi

# # Define the cron job and its schedule
cron_job="@reboot ~/pt_rpi/ugv-env/bin/python ~/pt_rpi/app.py >> ~/ugv.log 2>&1"

# Check if the cron job already exists in the user's crontab
if crontab -l | grep -q "$cron_job"; then
    echo "Cron job is already set, no changes made."
else
    # Add the cron job for the user
    (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
    echo "Cron job added successfully."
fi

echo "Now you can use the command below to reboot."

echo "sudo reboot"