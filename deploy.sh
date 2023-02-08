#!/bin/bash

# Change to the project directory
cd /home/no-fuckup-timer-bot/

# Pull the latest changes from Git
git pull

# Restart Docker Compose
docker-compose down
docker-compose up -d
