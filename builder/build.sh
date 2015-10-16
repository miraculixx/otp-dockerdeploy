#!/bin/bash


# Getting the urls and environment variables for otp
while getopts ":u:e:U:H" opt
   do
      case $opt in
        u ) urls=$OPTARG;;
        e ) envs=$OPTARG;;
        U ) useragent="-U $OPTARG";;
        H ) headers="$headers --header $OPTARG";;
        r ) router=$OPTARG;;
      esac
done

OTP_BASE=/var/otp
OTP_GRAPHS=$OTP_BASE/graphs
OTP_ROUTER=${router:-default}

mkdir -p $OTP_GRAPHS/$OTP_ROUTER

for url in $urls; do
echo "downloading $url"
wget_opts="-S -nv $headers $useragent -P $OTP_GRAPHS/$OTP_ROUTER $url"
echo "wget $wget_opts" 
wget $wget_opts || echo "-- error" 
done

# Defining the env variables
export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-amd64"
#mkdir -p /var/otp/pdx && \
  
# Let's build the maps
echo "generating graph"  
java -Xmx16G -jar /var/otp/otp.jar --build $OTP_GRAPHS/$OTP_ROUTER $envs

# Moving the generated graph to the shared dir
echo "finalizing"
find $OTP_GRAPHS
