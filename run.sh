#!/usr/bin/bash

SCRIPT_DIR=/home/pfournier/.scripts/bandcamp_rss
PYTHON_PATH=$SCRIPT_DIR/.venv/bin/python

cd $SCRIPT_DIR
$PYTHON_PATH main.py -d request_cache.db celestialsynapse
