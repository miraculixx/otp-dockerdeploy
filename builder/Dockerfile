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
  rm -rf /var/lib/apt/lists/* && \
  mkdir -p /var/otp/pdx && \
  echo "downloading otp" && \ 
  cd /var/otp && \ 
  wget -S -nv -O /var/otp/otp.jar http://dev.opentripplanner.org/jars/otp-0.14.0.jar
  
ADD build.sh /root/
RUN chmod +x /root/build.sh

ENTRYPOINT [ "/root/build.sh" ]

CMD [ "--help" ]
