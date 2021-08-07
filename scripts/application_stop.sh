#!/bin/bash

echo "Stopping previous docker container"
FOLDER=/home/ec2-user/skule-vote
if [ -e "$FOLDER" ]; then
  cd $FOLDER
  docker-compose -f deployment/docker-compose.prod.yml down
else
  echo "$FOLDER does not exist."
fi