#!/usr/bin/env bash

cd /home/ubuntu/quiz/
source /home/ubuntu/venv/bin/activate
echo yes | DJANGO_SETTINGS_MODULE=quiz.settings SECRET_KEY='^00xtu1!)qqj^h$p2(3c&l&7njedyqo!d9z-u@@v694l2darov' /home/ubuntu/quiz/manage.py collectstatic

sudo service gunicorn stop
sudo service gunicron start
sudo service nginx restart
