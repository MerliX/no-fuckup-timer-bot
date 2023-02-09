#!/bin/bash

# Change to the project directory
cd /home/no-fuckup-timer-bot/
docker-compose down

# Pull the latest changes from Git
git fetch --all
git pull

docker-compose build

# Restart Docker Compose

docker-compose up -d
