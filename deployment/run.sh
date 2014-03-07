#!/bin/sh
cd "$(dirname "$0")"
. ../env/bin/activate;
ip="$(ifconfig | grep -A 1 'eth0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1)"
gunicorn -b $ip:5000 webserver:app;
