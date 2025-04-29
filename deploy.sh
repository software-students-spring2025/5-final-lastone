#!/bin/bash

set -e  # Fail on any error

# Go to your app folder
cd /root/opt/5-final-lastone

# Make sure Git repo is clean
echo "Fetching latest code..."
git fetch origin main
git reset --hard origin/main

# Rebuild and restart containers
echo "Rebuilding and restarting Docker containers..."
docker-compose down
docker-compose up -d --build

echo "GitHub CD: Deployment successful!"
