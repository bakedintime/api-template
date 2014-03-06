#!/bin/sh
cd "$(dirname "$0")"
. ../env/bin/activate;
gunicorn -b ***REMOVED***.200.34:5000 webserver:app;
