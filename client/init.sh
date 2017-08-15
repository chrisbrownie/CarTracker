#!/bin/bash
exec_path='/home/pi/cartracker/'

# Ensure we've got the latest version of the code
echo 'getting latest copy of repository'
cd $exec_path
git pull
echo 'got latest copy of repository'
