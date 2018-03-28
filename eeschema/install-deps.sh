#!/bin/bash

apt-get update
apt-get install -y python python-pip xvfb recordmydesktop xdotool
pip install -r `dirname $0`/requirements.txt
