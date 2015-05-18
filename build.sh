#!/bin/bash

# Define commonly used JAVA_HOME variable
export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64

rm -rf /var/otp/pdx/*
mkdir -p /var/otp/pdx
#wget -q -O /var/otp/pdx/zurich_switzerland.osm.pbf https://s3.amazonaws.com/metro-extracts.mapzen.com/zurich_switzerland.osm.pbf
#wget -q -O /var/otp/pdx/gtfs_complete.zip http://gtfs.geops.ch/dl/gtfs_complete.zip
#wget -q -O /var/otp/pdx/fix.zip http://www.gtfs-data-exchange.com/agency/flixbus-gmbh/latest.zip
wget -q -O /var/otp/pdx/fix.zip https://www.dropbox.com/s/2rpmww0nrrq00kj/Simplex%202014%20%281%29.zip?dl=0

# Let's build the maps
cd /var/otp
mkdir -p /var/otp/graphs
wget -q -O /var/otp/otp.jar http://dev.opentripplanner.org/jars/otp-latest-master.jar
java -Xmx8G -jar /var/otp/otp.jar --build /var/otp/pdx --noStreets --longDistance

# Moving the generated graph to the right dir
mv /var/otp/pdx/Graph.obj /var/otp/graphs/

java -Xmx6G -Xverify:none -jar /var/otp/otp.jar


