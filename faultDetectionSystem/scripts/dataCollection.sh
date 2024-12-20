#!/bin/bash

# Function to display error messages in tmux using less
display_error_tmux() {
    # Ensure the error log file exists
    if [ ! -e "$TEMP_ERROR_LOG" ]; then
        echo "$(get_timestamp) Error: $TEMP_ERROR_LOG does not exist. Creating it now." >> "$ERROR_LOG"
        touch "$TEMP_ERROR_LOG" || {
            echo "$(get_timestamp) Error: Cannot create $TEMP_ERROR_LOG. Exiting." >> "$ERROR_LOG"
            exit 1
        }
    fi

    # Create a tmux session to display the errors
    tmux new-session -d -s "error_session" "less $TEMP_ERROR_LOG"

    # Attach to the tmux session
    tmux attach -t "error_session"

    # Kill the tmux session after the user exits
    tmux kill-session -t "error_session" 2>/dev/null
}

# Get current timestamp
get_timestamp() {
    echo "$(date '+%Y-%m-%d %I:%M:%S %p')"
}

# Constants
THRESHOLD=5
SYSTEM_LOG="../logs/system.log"
ERROR_LOG="../logs/error.log"
TEMP_ERROR_LOG=$(mktemp)
RAW_DATA_FILE="../data/rawData.txt"

# Ensure necessary directories exist
if [ ! -d "$(dirname "$RAW_DATA_FILE")" ]; then
    echo "$(get_timestamp) Error: Data directory $(dirname "$RAW_DATA_FILE") does not exist. Exiting." | tee -a "$ERROR_LOG"
    exit 1
fi
if [ ! -d "$(dirname "$SYSTEM_LOG")" ]; then
    echo "$(get_timestamp) Error: Log directory $(dirname "$SYSTEM_LOG") does not exist. Exiting." | tee -a "$ERROR_LOG"
    exit 1
fi

# Validate number of arguments
if [ $# -ne 1 ]; then
    echo "$(get_timestamp) Error: Incorrect number of arguments. Usage: $0 <duration_in_minutes>" >> "$TEMP_ERROR_LOG"
    display_error_tmux
    exit 1
fi

# Validate and parse duration argument (in minutes)
if [[ ! "$1" =~ ^[0-9]+$ ]]; then
    echo "$(get_timestamp) Error: Invalid number of minutes provided. File: ${BASH_SOURCE[0]}" >> "$TEMP_ERROR_LOG"
    display_error_tmux
    exit 1
fi
DURATION=$1

# Log start of data collection
START_TIME=$(get_timestamp)
echo "$START_TIME Data collection started at $START_TIME for $DURATION minute(s)." >> "$SYSTEM_LOG"

# Create or clear the raw data file
> "$RAW_DATA_FILE" || {
    echo "$(get_timestamp) Error: Cannot write to $RAW_DATA_FILE. File: ${BASH_SOURCE[0]}" >> "$TEMP_ERROR_LOG"
    display_error_tmux
    exit 1
}

# Collect data for the specified duration
for (( i=0; i<DURATION; i++ )); do
    # Get CPU usage percentage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    
    # Check if CPU usage is valid
    if [ -z "$CPU_USAGE" ] || ! [[ "$CPU_USAGE" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
        TIMESTAMP=$(get_timestamp)
        echo "$TIMESTAMP Error: Failed to retrieve CPU usage at $TIMESTAMP. File: ${BASH_SOURCE[0]}" >> "$TEMP_ERROR_LOG"
        display_error_tmux
        exit 1
    fi
    
    TIMESTAMP=$(get_timestamp)
    FAULT=0
    if (( $(echo "$CPU_USAGE >= $THRESHOLD" | bc -l) )); then
        FAULT=1
    fi

    # Append data to the raw data file
    echo "$TIMESTAMP, $CPU_USAGE, $FAULT" >> "$RAW_DATA_FILE" || {
        TIMESTAMP=$(get_timestamp)
        echo "$TIMESTAMP Error: Failed to write to $RAW_DATA_FILE. File: ${BASH_SOURCE[0]}" >> "$TEMP_ERROR_LOG"
        display_error_tmux
        exit 1
    }

    sleep 60
done

# Log end of data collection
END_TIME=$(get_timestamp)
echo "$END_TIME Data collection ended at $END_TIME" >> "$SYSTEM_LOG"

# Run processData.pl if no errors occurred
if [ ! -s "$TEMP_ERROR_LOG" ]; then
    echo "$END_TIME No errors detected. Running processData.pl." >> "$SYSTEM_LOG"
    perl processData.pl
    if [ $? -ne 0 ]; then
        echo "$(get_timestamp) Error: processData.pl failed to execute. File: ${BASH_SOURCE[0]}" >> "$TEMP_ERROR_LOG"
        display_error_tmux
        exit 1
    fi
else
    echo "$(get_timestamp) Errors detected during execution. Exiting." >> "$SYSTEM_LOG"
    display_error_tmux
    exit 1
fi

# Clean up temporary error log
rm -f "$TEMP_ERROR_LOG"

exit 0
