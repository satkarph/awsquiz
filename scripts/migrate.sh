#!/usr/bin/env bash
cd /home/ubuntu/quiz/
source /home/ubuntu/venv/bin/activate
DJANGO_SETTINGS_MODULE=quiz.settings SECRET_KEY='^00xtu1!)qqj^h$p2(3c&l&7njedyqo!d9z-u@@v694l2darov' ./manage.py makemigrations
DJANGO_SETTINGS_MODULE=quiz.settings SECRET_KEY='^00xtu1!)qqj^h$p2(3c&l&7njedyqo!d9z-u@@v694l2darov' ./manage.py migrate auth
DJANGO_SETTINGS_MODULE=quiz.settings SECRET_KEY='^00xtu1!)qqj^h$p2(3c&l&7njedyqo!d9z-u@@v694l2darov' ./manage.py migrate
