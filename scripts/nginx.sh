#!/usr/bin/env bash

mkdir -p /etc/nginx/sites-enabled
mkdir -p /etc/nginx/sites-available

sudo mkdir -p /etc/nginx/log/

sudo cp /home/ubuntu/quiz/nginx/default.conf /etc/nginx/quiz.phuyal.co.uk.conf

sudo ln -s /etc/nginx/sites-available/quiz.phuyal.co.uk.conf /etc/nginx/sites-enabled/quiz.phuyal.co.uk.conf

sudo /etc/init.d/nginx reload
sudo /etc/init.d/nginx start
