#!/bin/bash

baseUrl='https://mydomain.com/log.php'
# Get 5 lines from gpspipe (best chance of speed+accuracy tradeoff)
# if we get more than one location line (class=TPV), get the last one
gpsData=`gpspipe -w -n 5 | grep '"class":"TPV"' | tail -n1`

cmd="curl -k $baseUrl --data-urlencode 'gpsData=$gpsData'"

curlLog=`eval $cmd`

echo $curlLog
