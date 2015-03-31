#!/bin/bash
# run this to install required software on the server
#
# sudo ./install.ch
#
apt-get install python-pip && pip -q install docker-py
apt-get install docker
pip install -r requirements.txt