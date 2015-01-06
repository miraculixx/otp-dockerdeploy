#!/usr/bin/ruby

# Running the puppet module
members = "[" + ARGV.collect { |a| "'#{a}'" }.join(", ") + "]"
system("puppet apply -t -e \"nginxproxy { 'otp': members => #{members} }\"")

# Starting nginx on the foreground
system("/usr/sbin/nginx -g \"daemon off\;\"")
