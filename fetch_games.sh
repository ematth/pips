#!/bin/bash

# --- Configuration ---
# Set the start and end dates for the range you want to fetch.
# Format: YYYY-MM-DD
start_date="2025-09-01"
end_date="2025-09-15"
# ---------------------

echo "Starting to fetch Pips games from $start_date to $end_date..."

# Convert the end date to seconds since the epoch for comparison
end_date_sec=$(date -d "$end_date" +%s)
current_date_sec=$(date -d "$start_date" +%s)

# Loop from the start date until the current date passes the end date
while [ "$current_date_sec" -le "$end_date_sec" ]; do
    # Format the current date as YYYY-MM-DD
    current_date_fmt=$(date -d "@$current_date_sec" +%Y-%m-%d)
    
    echo "Fetching game for: $current_date_fmt"
    
    # Run your Python script with the current date as an argument
    python3 nytgames.py "$current_date_fmt"
    
    # Be polite to the server: wait for 1 second between requests
    sleep 0.5
    
    # Increment the current date by one day
    current_date_sec=$(date -d "$current_date_fmt + 1 day" +%s)
done

echo "All done!"
