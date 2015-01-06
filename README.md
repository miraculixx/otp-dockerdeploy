otp-dockerdeploy
================

#### Table of contents

1. [Overview] (#overview)
2. [Running the containers] (#running-the-containers)
   * [Starting the server] (#starting-the-server)
   * [Building the graph] (#building-the-graph)
   * [Starting nginx] (#starting-nginx)
3. [Unit testing] (#unit-testing)

## Overview

This project has a Dockerfile to deploy an opentripplanner instance, with the GTFS for Switzerland built in. There is also a unittest script to run the instance and check if everything is working.

## Running the containers

First pull the Docker container from the repo (the repo might change):

`docker pull pablokbs/opentripplanner` 

The server and the builder are now separated, but they share the /var/otp directory. The builder will build (doh!) the graphs and place it on the shared directory.

### Starting the server

You can run the server by running the following line, please note the "--name server" that is necessary for the builder container. Note also the **-s** switch, to run the server:

`docker run -p 80:8080 -d --name server pablokbs/opentripplanner:server -s`

That will run a simple ubuntu instance, will download the dependencies and run the server, it might take a few minutes to start. After starting, you can browse the ip of the server, that will be redirected to the 8080 port on the container. The `-d`switch puts the container on daemon mode.

To see the running docker instances, just type:

`docker ps`

Some useful commands:

```
## Stop the container
# docker stop <container>

## Start the container
# docker start <container>

## Restart the container
# docker restart <container>

## SIGKILL a container
# docker kill <container>

## Remove a container
# docker stop <container> # Container must be stopped to remove it
# docker rm <container>
```

### Building the graph

Now it's possible to build a new graph for the server. It's easy to use:

`docker run --volumes-from server pablokbs/opentripplanner:builder <GTFS_URL> <PDX_URL>`

That will download the GTFS and the PDX from the specified urls, it will build the graph and also will place the generated graph into the right dir.

After building the graph you should reload the server container:

`docker restart server`

IMPORTANT: The **server** container must be running before running the builds. Because the shared volume is created by the server container.. 

## Starting nginx

It's also possible to start a nginx proxy server to balance the load and run multiple "server" containers. The command line is the following:

`docker run -p 80:80 -d --name nginx pablokbs/opentripplanner:nginx <SERVER1_IP:PORT> <SERVER2_IP:PORT> ... <SERVERN_IP:PORT>`

That will create a ubuntu container, download puppet, get the nginx module and configure nginx to forward the traffic to the IPs configured as arguments, you can use as many arguments as you want.

## Unit testing

We've implemented a script that has the ability to both run and test if the container is working as expected. In order to run it, we will need some dependencies on the server:

`apt-get install python-pip && pip -q install docker-py`

That's it! That's all we need to run the test. Remember that Docker version > 1.3 is required.

To run the test:

`./unittest.py pablokbs/opentripplanner:latest`

This is an example output:

```
2014-12-02 10:54:52,157 - unittest.py - INFO - Creating container.
2014-12-02 10:54:52,301 - unittest.py - INFO - Starting container.
2014-12-02 10:54:52,444 - unittest.py - INFO - Sleeping for 5 seconds to allow the container to start up
2014-12-02 11:01:17,805 - unittest.py - INFO - Begin test.
2014-12-02 11:01:17,930 - urllib3.connectionpool - INFO - Starting new HTTP connection (1): 172.17.0.2
2014-12-02 11:01:30,375 - unittest.py - INFO - Asserting origin data (47.37731,8.51612).
2014-12-02 11:01:30,377 - unittest.py - INFO - Origin data is OK.
2014-12-02 11:01:30,378 - unittest.py - INFO - Asserting destination data (47.35371, 8.55835).
2014-12-02 11:01:30,379 - unittest.py - INFO - Destination data is OK.
2014-12-02 11:01:30,379 - unittest.py - INFO - All assertions passed!
2014-12-02 11:01:30,380 - unittest.py - INFO - Everything looks OK. Exiting
```

As you can see, it creates the container, starts it, and tests a little search.
