#!/bin/bash

# Script that tries to automate the graph building process

if [ -z $2 ]
  then
    echo "Usage: "
    echo "  $0 <GTFS_URL> <PDX_URL>"
    exit 1
fi 

# Defining the env variables
export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-amd64"

mkdir -p /var/otp/pdx && \
wget -q -P /var/otp/pdx/ $1 && \ 
wget -q -P /var/otp/pdx/ $2 && \

# Let's build the maps
cd /var/otp && \
mkdir -p /var/otp/graphs && \
wget -q -O /var/otp/otp.jar http://dev.opentripplanner.org/jars/otp-latest-master.jar && \
java -Xmx8G -jar /var/otp/otp.jar --build /var/otp/pdx

# Moving the generated graph to the right dir
mv /var/otp/pdx/Graph.obj /var/otp/graphs/
