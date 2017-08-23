#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Processes trips and turns them into kml files
"""

from __future__ import print_function
import sys
import boto3
import uuid
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

__version__ = "0.1"
__author__ = "Chris Brown"

# The name of the AWS profile to use
AWS_PROFILE = 'carlog-read'
# The AWS region to work in
AWS_REGION = 'ap-southeast-2'
# The name of the dynamodb table
TABLE_NAME = 'carlog'
# The name of the index by tripid sorting by time
INDEX_NAME = 'tripid-index'
# The name of the S3 bucket
S3_BUCKET = 'carlog'

KML_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Placemark>
    <name>{tripname}</name>
    <description>{tripdescription}</description>
    <LineString>
      <extrude>1</extrude>
      <tessellate>1</tessellate>
      <altitudeMode>absolute</altitudeMode>
      <coordinates>
"""

KML_FOOTER = """
      </coordinates>
    </LineString>
  </Placemark>
</kml>

"""

KML_LINETEMPLATE = '        {lon}, {lat}, {alt} <!-- {time},{odo} -->'

boto3.setup_default_session(
    profile_name=AWS_PROFILE,
    region_name=AWS_REGION)


def getDbRecords():

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    results = table.scan(
        # This works, updating to allow 'exported'.notexists()
        # FilterExpression=Attr('time').exists(),
        ExpressionAttributeNames={
            "#time": "time",
            "#exported": "exported"
        },
        FilterExpression='attribute_exists(#time) AND attribute_not_exists(#exported)'
    )

    # the query method

    items = results['Items']
    return items


def markTripExported(tripid):
    print('Marking trip exported ' + tripid)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    results = table.query(
        TableName=TABLE_NAME,
        IndexName=INDEX_NAME,
        KeyConditionExpression='tripid = :tripid',
        ExpressionAttributeValues={
            ":tripid": tripid
        }
    )

    items = results['Items']
    for item in items:
        table.update_item(
            Key={
                'time': item['time']
            },
            UpdateExpression="set exported = :exported",
            ExpressionAttributeValues={
                ':exported': 'true'
            },
            ReturnValues="UPDATED_NEW"
        )

def generateKml(items):
    kml = KML_HEADER
    try:
        tripid = items[0]['tripid']
    except:
        tripid = "00000"

    times = []

    # Sort the times
    for item in items:
        times.append(item["time"])

    times.sort()

    starttime = 'not-set'
    endtime = 'not-set'

    # for each time in order, return the item
    for time in times:
        item = next(x for x in items if x['time'] == time)
        # if this is our first run, set starttime
        if starttime == 'not-set':
            starttime = item['time']
        # Always set endtime so that it's got the last time entry
        endtime = item['time']

        coords = {
            'lon': item['lon'],
            'lat': item['lat'],
            'alt': item['alt'],
            'time': item['time'],
            'tripid': tripid,
            'odo': item['odo']
        }
        kmlline = KML_LINETEMPLATE.format(**coords)
        kml = kml + kmlline + "\n"

    # attach the footer
    kml = kml + KML_FOOTER
    kmlinfo = {
        'tripname': ('Trip ' + starttime + ' to ' + endtime),
        'tripdescription': ''
    }
    kml = kml.format(**kmlinfo)
    return tripid, kml


def writeFileToS3(filename, content):
    client = boto3.client('s3')
    filepath = "/tmp/" + filename + '.kml'
    f = open(filepath, 'w')
    f.write(content)
    f.close()

    with open(filepath, 'rb') as g:
        client.upload_fileobj(g, S3_BUCKET, 'kml/' + filename + '.kml')

    return 0


def main(prog_args):

    items = getDbRecords()
    trips = []
    for item in items:
        if 'tripid' in item:
            if item["tripid"] not in trips:
                trips.append(item["tripid"])

    for trip in trips:
        # This will be set to false if anything fails.
        # Used to determine if we should re-export or not
        exportsuccess = True

        # build a new list with the items where the tripid = this trip
        tripitems = []

        try:
            for item in items:
                if "tripid" in item:
                    if item["tripid"] == trip:
                        tripitems.append(item)

            # create the kml
            tripid, kml = generateKml(tripitems)

            # Write the KML to S3
            writeFileToS3(
                filename=tripid,
                content=kml
            )
            print("Processed" + tripid)
        except:
            exportsuccess = False
            print('Could not export trip: ' + trip)

        if exportsuccess == True:
            # Succeeded to export
            markTripExported(tripid)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
