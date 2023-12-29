#!/bin/bash

# Set the URL
url="https://api.publibike.ch/v1/public/partner/stations"

# Get the current date and time
current_datetime=$(date +"%Y%m%d_%H%M%S")

# Set the filename with a timestamp
filename="output_$current_datetime.json"

# Use curl to fetch JSON data and create a new file
curl_result=$(curl -s "$url")

# Check if the curl command was successful
if [ $? -eq 0 ]; then
    # Create a new file with the data
    echo "{ \"date\": \"$current_datetime\", \"data\": $curl_result }" > "$filename"
    echo "Data saved to $filename"
else
    echo "Error: Unable to fetch data from $url"
fi
