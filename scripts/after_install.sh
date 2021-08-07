#!/bin/bash

cd /home/ec2-user/skule-vote/skule_vote

echo "Installing requirements"
pip3 install -r requirements.txt

echo "Sourcing environment variables"
source /ENV_VARS

echo "Collecting static"
python3 manage.py collectstatic

cd frontend/ui
echo "Yarn install and build"
yarn in && yarn build

cd ../..

echo "Removing existing files"
sudo rm -r /var/www/html/*

echo "Moving frontend files"
sudo mv frontend/ui/build/* /var/www/html/

echo "Moving django files"
sudo mv static/* /var/www/html/static/