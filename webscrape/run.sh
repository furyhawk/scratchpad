#!/bin/sh

if command -v caffeinate &> /dev/null
then
    echo "<caffeinate> found"
    caffeinate -i -w $$ &
fi

python companies.py