#!/bin/bash
exec_path='/home/pi/cartracker/'

# Ensure we've got the latest version of the code

cd $exec_path

echo "Updating git repo ..."

git pull || echo "Failed to update git repo!"

