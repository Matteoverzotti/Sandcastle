#!/bin/bash

while true; do
    curl -s http://192.168.100.1 > /dev/null
    echo "Request sent to 192.168.100.1"
    sleep 2
done
