# CarTracker

This system grew out of my need to keep a car logbook for tax purposes. I need to record every car journey's distance and purpose.

## Components

* Raspberry Pi
* USB LTE Modem
* gpsd compatible GPS Data Logger (e.g. Holux M-1000C)
* OBD II bluetooth module

## Client

The client is quite simple. A cron job runs every minute to grab the GPS lat/long (from `gpspipe`) which is then curl'd against an API URL.

## Server

An Amazon API Gateway API is configured to Put content into a DynamoDB database whenever the API is hit. The client POSTs a bunch of JSON (including `time`, `lat`, and `lon`) to the API which is then dumped into the DB.

## Is it legal?

I'm not sure, time will tell. I think so, as per ATO finding [2002/095](http://law.ato.gov.au/atolaw/view.htm?docid=AID/AID2002925/00001).

## Resources

* [picard: A Raspberry Pi based OBD-II data logging system](https://souvik.me/blog/picard-a-raspberry-pi-based-obd-ii-data-logging-system)
