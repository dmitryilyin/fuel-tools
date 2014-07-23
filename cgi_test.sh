#!/bin/sh
QUERY_STRING="hostname=${1}&resource=${2}&xml=1" python cib_check_cgi.py
