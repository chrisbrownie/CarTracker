#!/usr/bin/env python

import uuid

tripid_path = "/home/pi/tripid"
# Generate a guid for trip ID
# trip ID is unique every time the car (pi) is started.
trip_id = str(uuid.uuid4())

# Write the trip id to a file
f = open(tripid_path, 'w')
f.write(trip_id)
f.close()
