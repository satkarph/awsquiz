#!/usr/bin/env bash
apt-get update && apt-get upgrade -y
apt-get install python-pip python-dev nginx git
apt-get install python-virtualenv

/etc/init.d/nginx stop
