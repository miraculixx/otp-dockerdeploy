#!/bin/bash
java -Xmx6G -Xverify:none -jar /var/otp/otp.jar --noStreets --longDistance --graphs /var/otp/graphs -s -p 80 --analyst --insecure

