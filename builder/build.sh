#!/bin/bash

# Getting the urls and environment variables for otp
while getopts ":u:e:" opt
   do
      case $opt in
         u ) urls=$OPTARG;;
         e ) envs=$OPTARG;;
      esac
done

for url in $urls; do
   wget -q -P /var/otp/pdx/ $url
done

# Defining the env variables
export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-amd64"
mkdir -p /var/otp/pdx && \
  
# Let's build the maps
cd /var/otp && \
wget -q -O /var/otp/otp.jar http://dev.opentripplanner.org/jars/otp-latest-master.jar && \
java -Xmx8G -jar /var/otp/otp.jar --build /var/otp/pdx $envs

# Moving the generated graph to the shared dir
mkdir -p /var/otp/graphs && \
mv /var/otp/pdx/Graph.obj /var/otp/graphs/
