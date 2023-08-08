#!/bin/bash

COMMAND="kill -9 $(ps aux | grep '[i]nterstitial_API:app' | awk '{print $2}')"

eval $COMMAND