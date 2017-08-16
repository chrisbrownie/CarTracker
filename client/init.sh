#!/bin/bash
exec_path='/home/pi/cartracker'

# Ensure we've got the latest version of the code

cd $exec_path

echo "Updating git repo ..."

git pull || echo "Failed to update git repo!"

python $exec_path/client/starttrip.py || echo "Failed to run starttrip.py"

