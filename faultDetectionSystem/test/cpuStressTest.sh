#!/bin/bash

# A simple test case to generate high CPU usage for 10 minutes
# This will run an infinite loop and use 100% CPU

echo "Starting high CPU usage test... Press Ctrl+C to stop."
start_time=$(date)

# Run an infinite loop that will consume CPU
while :
do
	# Output the CPU usage every 5 seconds to show it's running
	echo "High CPU usage test running at $(date)"
	sleep 5
done

echo "High CPU usage test started at $start_time"

