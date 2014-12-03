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

def unit_test(ipaddr, target_port):
    LOGGER.info(u'Begin test to ' + ipaddr + u':' + target_port + u'.')
    fromPlace = u'47.37731,8.51612'
    toPlace = u'47.35371, 8.55835'
    mode = u'TRANSIT,WALK'
    date = u'11-29-2014'
    r = requests.get(u'http://' + ipaddr + u':' + target_port + u'/otp/routers/default/plan?fromPlace=' + fromPlace + '&toPlace=' + toPlace + '&mode=' + mode + '&date=' + date)
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

def create_container(tag, port8080, port8081, bind_address, must_map):
    LOGGER.info(u'Creating container.')
    port_bindings = {}
    if port8080 is not None:
        port_bindings[8080] = (bind_address, port8080)
    if port8081 is not None:
        port_bindings[8081] = (bind_address, port8081)
    try:
       container = CLI.create_container(image=tag, command=u'/bin/bash -s -v', stdin_open=True, tty=True, name='otp-test', ports=[8080, 8081])
    except docker.errors.APIError as e:
        LOGGER.warning(u'Container exists but is inactive. Trying to start it.')
        if e.response.status_code == 409:
            container = get_container(tag, all=True)
    LOGGER.info(u'Starting container.')
    CLI.start(container=container.get('Id'), port_bindings=port_bindings)
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
 

def cleanup(image, container, keep_image=True):
    image_action = u'keeping' if keep_image is True else u'removing'
    LOGGER.info(u'Cleaning up (stopping/removing container and ' + image_action + ' image)')
    CLI.stop(container.get('Id'))
    CLI.remove_container(container.get('Id'))
    if keep_image is False:
        CLI.remove_image(image.get('Id'))

def check_current_mappings(container, port8080, port8081, bind_address):
    to_map = []
    if port8080 is not None:
        to_map.append(bind_address + u':' + unicode(port8080))
    if port8081 is not None:
        to_map.append(bind_address + u':' + unicode(port8081))
    mapped = []
    for addrport in container['Ports']:
        if 'IP' in addrport.keys() and 'PublicPort' in addrport.keys():
            mapped.append(addrport['IP'] + u':' + unicode(addrport['PublicPort']))
    new_add = []
    old_remove = []
    for map in to_map:
        if map not in mapped:
            new_add.append(map)
    for map in mapped:
        if map not in to_map:
            old_remove.append(map)
    for map in new_add:
        LOGGER.warning(u'Mapping ' + unicode(map) + u' not mapped but desired.')
    for map in old_remove:
        LOGGER.warning(u'Mapping ' + unicode(map) + u' not desired but mapped.')
    if len(new_add) > 0 or len(old_remove) > 0:
        LOGGER.warning(u'If you wish to refresh port mappings, use --force-new-container.')
    if bind_address not in [map.split(':')[0] for map in mapped] or unicode(port8080) not in [map.split(':')[1] for map in mapped]:
        LOGGER.error(u'Falling back to internal container address and port since no usable mappings are available.')
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Docker unit test for OTP.')
    parser.add_argument('tag', type=str, help='Image name/tag to test. Mandatory')
    parser.add_argument('--dockerfilepath', type=str, help='Path to Dockerfile, or directory containing Dockerfile. Needed if image does not exist.')
    parser.add_argument('-O', '--output', type=str, help='Filename to write build output.')
    parser.add_argument('-P', '--port8080', type=int, help='Local port to forward to port 8080 on the container. Leave blank if you don\'t want forwarding.')
    parser.add_argument('-p', '--port8081', type=int, help='Local port to forward to port 8081 on the container. Leave blank if you don\'t want forwarding')
    parser.add_argument('-B', '--bind-address', type=str, help='Local IP address to bind the ports. Leave blank or set to 0.0.0.0 to bind to all available IP addresses.')
    parser.add_argument('--nokeep', action='store_true', help='Delete the container/image after testing.')
    parser.add_argument('--force-new-container', action='store_true', help='Force container recreation if it is running. Use this to refresh port mappings if necessary.')

    args = parser.parse_args()
    dockerfile = args.dockerfilepath
    tag = args.tag
    output = args.output
    
    port8080 = args.port8080
    port8081 = args.port8081
    bind_address = args.bind_address
    must_map = True
    if bind_address is not None:
        if len(bind_address.split(' ')) > 1 or len(bind_address.split(',')) > 1:
            LOGGER.error(u'Only one address mapping can be performed.')
            sys.exit(4)

    if bind_address is not None and port8080 is None and port8081 is None:
        LOGGER.error(u'If using bind-address, local ports must be specified. Ignoring desired mappings.')
        must_map = False
    elif bind_address is None and (port8080 is not None or port8081 is not None):
        LOGGER.warning(u'Mapping local ports to all addresses. Set -B/--bind-address to avoid this.')
        bind_address = u'0.0.0.0'

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
        container = create_container(tag, port8080, port8081, bind_address, must_map)

    maps_healthy = True
    if new_container is False:
        if args.force_new_container is False and must_map is True:
            maps_healthy = check_current_mappings(container, port8080, port8081, bind_address)
        else:
            LOGGER.warning(u'Refreshing container to clean old port mappings.')
            cleanup(image, container)
            new_container = True
            container = create_container(tag, port8080, port8081, bind_address, must_map)
    
    if new_container is True:
        LOGGER.info(u'Sleeping for 5 seconds to allow the container to spawn')
        time.sleep(5)
    
    #Getting the container's IP address in case we are not mapping anything and we need it to perform the test.
    ipaddr = CLI.inspect_container(container.get(u'Id'))[u'NetworkSettings'][u'IPAddress']
    ready = False

    if maps_healthy is False or port8080 is None:
        target_ip = ipaddr
        target_port = u'8080'
    elif bind_address == '0.0.0.0' and port8080 is not None:
        target_ip = u'127.0.0.1'
        target_port = unicode(port8080)
    elif bind_address != '0.0.0.0':
        target_ip = bind_address
        target_port = unicode(port8080)
 
    addr = target_ip if target_ip != '127.0.0.1' else ipaddr
    port = target_port if addr != ipaddr else '8080'

    LOGGER.info(u'Checking connectivity to the container, this may take some time. Using ' + addr  + u':' + port)
    retry = 1
    while ready is False and ready <= 50:
        try:
            tnet = Telnet(addr, port)
            ready = True
        except socket.error as e:
            if retry >= 30:
                LOGGER.info(u'Retry ' + unicode(retry) + u'/50. Still trying.')
            time.sleep(5)
            retry += 1
    LOGGER.info(u'Connection ready.')

    unit_test(target_ip, target_port)

    if args.nokeep is True:
        cleanup(image, container, keep_image=False)

    LOGGER.info(u'Everything looks OK. Exiting')
    sys.exit(0)
