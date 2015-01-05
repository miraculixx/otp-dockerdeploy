#
# OpenTripPlanner Dockerfile
#
# https://github.com/opentripplanner/opentripplanner
#

# Start with a small Ubuntu base image
FROM ubuntu:14.04

MAINTAINER Pablo Fredrikson <pablo.fredrikson@gmail.com>

# Setting variables and copying the manifest
WORKDIR /root

# Install the puppet agent
RUN \
  apt-get install -y wget && \
  wget http://apt.puppetlabs.com/puppetlabs-release-trusty.deb && \
  dpkg -i puppetlabs-release-trusty.deb && \
  apt-get update && \
  apt-get install -y puppet && \
  rm -rf puppetlabs-release-trusty.deb

# Install the required puppet modules
RUN \
  puppet module install jfryman/nginx && \
  mkdir -p /etc/puppet/modules/nginxproxy/manifests

ADD init.pp /etc/puppet/modules/nginxproxy/manifests/init.pp
ADD build.rb /root/build.rb
RUN chmod +x /root/build.rb

# Expose ports to other containers
EXPOSE 80

# Finishing
ENTRYPOINT [ "/root/build.rb" ]
