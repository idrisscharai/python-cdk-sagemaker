#!/bin/bash
if [ "$1" = "serve" ]; then
    exec python /serve.py
else
    exec "$@"
fi