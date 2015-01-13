#!/bin/bash


# Defining the env variables
export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-amd64"

mkdir -p /var/otp/pdx && \

for url in $@; do
   wget -q -P /var/otp/pdx/ $url && \
done

# Let's build the maps
cd /var/otp && \
wget -q -O /var/otp/otp.jar http://dev.opentripplanner.org/jars/otp-latest-master.jar && \
java -Xmx8G -jar /var/otp/otp.jar --build /var/otp/pdx

# Moving the generated graph to the shared dir
mkdir -p /var/otp/graphs && \
mv /var/otp/pdx/Graph.obj /var/otp/graphs/
