#!/bin/bash

# Install java

apt-get update
apt-get install -y openjdk-7-jre wget
rm -rf /var/lib/apt/lists/*

./build.sh
