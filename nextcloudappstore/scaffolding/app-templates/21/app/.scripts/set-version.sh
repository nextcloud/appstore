#!/bin/bash -e

if [ -z "$1" ]; then
    echo "You did not provide a version string as the first parameter. It is required. Aborting."
    exit 1
fi

find "`dirname "$0"`/set-version.d" -type f | sort -f | while read part
do

    if [ ! -x "$part" ]; then
        echo "Cannot execute file $part. Aborting processing."
        exit 1
    fi

    echo "Executing $part"
    "$part" "$1"
done
