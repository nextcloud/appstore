#!/bin/bash

if [ ! -f package.json ]; then
    echo "Cannot find package.json in the current location."
    echo "Are you running the version update script from the root folder of your app?"
    echo
    echo "Exiting..."
    exit 1
fi

sed "s/\"version\": \"[^\"]*\"/\"version\": \"$1\"/" -i package.json
