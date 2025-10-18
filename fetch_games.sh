#!/bin/bash

# --- Configuration ---
# Set the start and end dates for the range you want to fetch.
# Format: YYYY-MM-DD
start_date="2025-08-18"
end_date="2025-10-18"
# ---------------------

echo "Starting to fetch Pips games from $start_date to $end_date..."

# Create boards_json directory if it doesn't exist
mkdir -p boards_json

# Convert the end date to seconds since the epoch for comparison
end_date_sec=$(date -d "$end_date" +%s)
current_date_sec=$(date -d "$start_date" +%s)

# Loop from the start date until the current date passes the end date
while [ "$current_date_sec" -le "$end_date_sec" ]; do
    # Format the current date as YYYY-MM-DD
    current_date_fmt=$(date -d "@$current_date_sec" +%Y-%m-%d)
    
    # Check if JSON file for this date already exists
    json_file="boards_json/${current_date_fmt}.json"
    if [ -e "$json_file" ]; then
        echo "JSON for $current_date_fmt already exists. Skipping."
    else
        echo "Fetching JSON for: $current_date_fmt"
        url="https://www.nytimes.com/svc/pips/v1/${current_date_fmt}.json"
        
        # Fetch JSON using curl
        curl -s "$url" -o "$json_file"
        
        # Check if the download was successful
        if [ $? -eq 0 ] && [ -s "$json_file" ]; then
            echo "Successfully saved $json_file"
        else
            echo "Failed to fetch $current_date_fmt"
            rm -f "$json_file"
        fi
        
        sleep 0.5
    fi
    
    # Increment the current date by one day
    current_date_sec=$(date -d "$current_date_fmt + 1 day" +%s)
done

echo "All done!"
