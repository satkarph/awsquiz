#!/usr/bin/env bash

sudo cp /home/ubuntu/quiz/gunicorn/default.service /etc/systemd/system/gunicorn.service

sudo systemctl start gunicorn
sudo systemctl enable gunicorn
