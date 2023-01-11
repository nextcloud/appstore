#!/bin/bash

if [ ! -f appinfo/info.xml ]; then
    echo "Cannot find appinfo/info.xml in the current location."
    echo "Are you running the version update script from the root folder of your app?"
    echo
    echo "Exiting..."
    exit 1
fi

sed "s/<version>[^<]*<\\/version>/<version>$1<\\/version>/" -i appinfo/info.xml
