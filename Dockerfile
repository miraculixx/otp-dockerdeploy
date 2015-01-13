#
# OpenTripPlanner Dockerfile
#
# https://github.com/opentripplanner/opentripplanner
#

# Start with a small Ubuntu base image
FROM ubuntu:14.04

MAINTAINER Pablo Fredrikson <pablo.fredrikson@gmail.com>

# Install java
RUN \
  apt-get update && \
  apt-get install -y openjdk-7-jre wget && \
  rm -rf /var/lib/apt/lists/*

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64

# Download zurich pbf and complete gtfs
RUN mkdir -p /var/otp/pdx && \
  wget -q -O /var/otp/pdx/zurich_switzerland.osm.pbf https://s3.amazonaws.com/metro-extracts.mapzen.com/zurich_switzerland.osm.pbf && \
  wget -q -O /var/otp/pdx/gtfs_complete.zip http://gtfs.geops.ch/dl/gtfs_complete.zip

# Let's build the maps
RUN cd /var/otp && \
  mkdir -p /var/otp/graphs && \
  wget -q -O /var/otp/otp.jar http://dev.opentripplanner.org/jars/otp-latest-master.jar && \
  java -Xmx8G -jar /var/otp/otp.jar --build /var/otp/pdx

# Moving the generated graph to the right dir
RUN mv /var/otp/pdx/Graph.obj /var/otp/graphs/

# Expose ports for other containers
EXPOSE 8080
EXPOSE 8081

ENTRYPOINT [ "java", "-Xmx6G", "-Xverify:none", "-jar", "/var/otp/otp.jar" ]

CMD [ "--help" ]
