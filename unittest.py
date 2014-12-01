#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import docker
import pprint
import requests
import json
import sys
import argparse
import time
import socket
import logging
from io import BytesIO
from telnetlib import Telnet

CLI = docker.Client()
logformat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=u'INFO', format=logformat)
LOGGER = logging.getLogger(u'unittest.py')

def unit_test(ipaddr):
    LOGGER.info(u'Begin test.')
    fromPlace = u'47.37731,8.51612'
    toPlace = u'47.35371, 8.55835'
    mode = u'TRANSIT,WALK'
    date = u'11-29-2014'
    r = requests.get('http://' + ipaddr + ':8080/otp/routers/default/plan?fromPlace=' + fromPlace + '&toPlace=' + toPlace + '&mode=' + mode + '&date=' + date)
    response = json.loads(r.text)

    LOGGER.info(u'Asserting origin data (' + fromPlace + ').')
    assert response['plan']['from']['name'] == u'Sihlfeldstrasse'
    assert response['plan']['from']['lat'] == 47.37732962161289
    assert response['plan']['from']['lon'] == 8.516347042621483
    LOGGER.info(u'Origin data is OK.')
    LOGGER.info(u'Asserting destination data (' + toPlace + ').')
    assert response['plan']['to']['lat'] == 47.35370859536038
    assert response['plan']['to']['lon'] == 8.55834686524565
    assert response['plan']['to']['name'] == u'Seefeldstrasse'
    LOGGER.info(u'Destination data is OK.')

    LOGGER.info(u'All assertions passed!')


def build_dockerfile(dockerfile, is_path, tag, output):
    LOGGER.info(u'Building image. This may take a while.')
    LOGGER.info(u'To see the progress, wait for the container(s) to show up and use docker logs -f. Or, just wait :)')
    kwargs = {'rm': True, 'tag': tag}
    if is_path is True:
        kwargs['path'] = dockerfile
    else:
        f_ = open(dockerfile)
        filedocker = f_.read()
        f_.close()
        f = BytesIO(filedocker.encode('utf-8'))
        kwargs['fileobj'] = f
    try:
        response = [line for line in CLI.build(**kwargs)]
    except Exception as e:
        logger.error(u'Something went wrong when building! Exception is ' + unicode(e))
        sys.exit(3)
    if output is not None:
        LOGGER.info(u'Writing build output file.')
        file_ = open(output, 'w')
        pprint.pprint(response, file_)
        file_.close()

def create_container(tag):
    LOGGER.info(u'Creating container.')
    try:
       container = CLI.create_container(image=tag, command=u'/bin/bash -s -v', stdin_open=True, tty=True, name='otp-test')
    except docker.errors.APIError as e:
        LOGGER.warning(u'Container exists but is inactive. Trying to start it.')
        if e.response.status_code == 409:
            container = get_container(tag, all=True)
    LOGGER.info(u'Starting container.')
    CLI.start(container=container.get('Id'))
    return container

def get_image(tag):
    image = None
    for i in CLI.images():
        if tag in i['RepoTags']:
            image = i
    return image

def get_container(tag, all=False):
    container = None
    for c in CLI.containers(all=all):
        if tag in c['Image']:
            container = c
    return container

def validate_dockerfile(dockerfile):
    if os.path.isdir(dockerfile) is True:
        LOGGER.info(u'Assuming --dockerfilepath is a path.')
        return True
    else:
        LOGGER.info(u'Assuming --dockerfilepath is a file.')
        return False
 

def cleanup(image, container):
    LOGGER.info(u'Cleaning up (stopping container and removing entities)')
    CLI.stop(container.get('Id'))
    CLI.remove_container(container.get('Id'))
    CLI.remove_image(image.get('Id'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Docker unit test for OTP.')
    parser.add_argument('tag', type=str, help='Image name/tag to test. Mandatory')
    parser.add_argument('--dockerfilepath', type=str, help='Path to Dockerfile, or directory containing Dockerfile. Needed if image does not exist.')
    parser.add_argument('-O', '--output', type=str, help='Filename to write build output.')
    parser.add_argument('--nokeep', action='store_true', help='Delete the container/image after testing.')

    args = parser.parse_args()
    dockerfile = args.dockerfilepath
    tag = args.tag
    output = args.output

    new_container = False

    container = get_container(tag)
    image = get_image(tag)
    if container is None:
        if image is None:
            if dockerfile is None:
                LOGGER.error(u'No suitable image found. Need dockerfile/path to continue.')
                sys.exit(2)
            is_path = validate_dockerfile(dockerfile)
            build_dockerfile(dockerfile, is_path, tag, output)
            image = get_image(tag)
        new_container = True
        container = create_container(tag)

    if new_container == True:
        LOGGER.info(u'Sleeping for 5 seconds to allow the container to start up')
        time.sleep(5)
    
    ipaddr = CLI.inspect_container(container.get(u'Id'))[u'NetworkSettings'][u'IPAddress']
    ready = False
    while ready is False:
        try:
            Telnet(ipaddr, '8080')
            ready = True
        except socket.error:
            time.sleep(5)

    unit_test(ipaddr)

    if args.nokeep is True:
        cleanup(image, container)

    LOGGER.info(u'Everything looks OK. Exiting')
    sys.exit(0)
