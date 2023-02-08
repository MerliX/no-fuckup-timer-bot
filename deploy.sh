#!/bin/bash

# Change to the project directory
cd /home/no-fuckup-timer-bot/

# Pull the latest changes from Git
git fetch --all
git pull

export COMPOSE_API_VERSION=1.18
docker-compose build

# Restart Docker Compose
docker-compose down
docker-compose up -d
