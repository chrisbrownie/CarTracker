#!/usr/bin/env python

from gps3 import gps3
import json
import time
import obd
import subprocess
import shlex
import os.path
import requests
import uuid

# Get some variables together
obd_mac = "00:1D:A5:68:98:8A"
obd_port = "1"
rfcomm_port = "0"
odo_offset = 132435
post_url = "https://zb8lln5c7b.execute-api.ap-southeast-2.amazonaws.com/prod/log"

# Generate a guid for trip ID
# trip ID is unique every time the car (pi) is started.
trip_id = str(uuid.uuid4())

gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()


def mount_obd(mac, port, rfcomm_port):

    RFCOMM_OPERATION_NOT_PERMITTED_ERROR = "Can't create device: Operation not permitted"
    RFCOMM_ADDRESS_ALREADY_IN_USE_ERROR = "Can't create device: Address already in use"

    # attempt to bind the OBD to a port
    obd_bindcommand = 'rfcomm bind {} {} {}'.format(rfcomm_port, mac, port)
    obd_args = shlex.split(obd_bindcommand)
    obd_bindresults = subprocess.Popen(obd_args, stderr=subprocess.PIPE)

    # Get the results from rfcomm. RFCOMM includes spaces and newlines and stuff so strip those out
    obd_err = obd_bindresults.stderr.read().strip(' \t\n\r')

    # rfcomm doesn't return non-zero even if it fails, so we need to catch common errors:
    if obd_err == RFCOMM_OPERATION_NOT_PERMITTED_ERROR:
        print("access denied")
    elif obd_err == RFCOMM_ADDRESS_ALREADY_IN_USE_ERROR:
        print("address already in use")
    else:
        pass
        #print("successfully bound {}({}) to rfcomm{}".format(mac,port,rfcomm_port))


if (os.path.exists('/dev/rfcomm{}'.format(rfcomm_port))):
        #print('Using existing device at /dev/rfcomm{}'.format(rfcomm_port))
    pass
else:
    mount_obd(obd_mac, obd_port, rfcomm_port)

obd_connection = obd.OBD('/dev/rfcomm{}'.format(rfcomm_port))
obd_command = obd.commands['DISTANCE_SINCE_DTC_CLEAR']


data = {}

for new_data in gps_socket:
    if new_data:
        data_stream.unpack(new_data)
        if data_stream.TPV['lat'] == "n/a":
            # valid data not yet received
            pass
        else:
            # schema: http://www.catb.org/gpsd/gpsd_json.html
            data['tripid'] = trip_id
            data['time'] = str(data_stream.TPV['time'])
            data['lat'] = str(data_stream.TPV['lat'])
            data['lon'] = str(data_stream.TPV['lon'])
            data['alt'] = str(data_stream.TPV['alt'])
            data['speed'] = str(data_stream.TPV['speed'])
            data['track'] = str(data_stream.TPV['track'])
            data['climb'] = str(data_stream.TPV['climb'])
            try:
                data['odo'] = str(obd_connection.query(obd_command).value)
            except:
                data['odo'] = ''

            json_data = json.dumps(data)
            print 'JSON:', json_data
            req = requests.post(post_url, json=data)
            print(req.status_code, req.reason)
            quit()
