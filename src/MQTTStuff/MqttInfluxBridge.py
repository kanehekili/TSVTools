#!/usr/bin/env python3
import json
import time
from paho.mqtt import client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration - CHANGE THESE!
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "faketokenfromsomeplace"
INFLUX_ORG = "TSVAccess"
INFLUX_BUCKET = "Humidity"

MQTT_BROKER = "localhost"
MQTT_TOPIC = "moisture/data"

def on_connect(mqtt_client, userdata, flags, rc, properties=None):
    print(f"Connected to MQTT broker with result code {rc}")
    mqtt_client.subscribe(MQTT_TOPIC)

def on_message(mqtt_client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Got {payload}")        
        # Required fields check
        if not all(k in payload for k in ["device", "moisture", "Raw"]):
            print("Missing required fields in payload")
            return
            
        # Create InfluxDB point
        point = Point("device_metrics") \
            .tag("device", payload["device"]) \
            .field("percentage", float(payload["moisture"])) \
            .field("raw_value", float(payload["Raw"]))
            
        # Add timestamp if provided
        if "timestamp" in payload:
            point.time(int(payload["timestamp"]))
        else:
            point.time(time.time_ns())
            
        # Write to InfluxDB
        write_api.write(bucket=INFLUX_BUCKET, record=point)
        print(f"Written data for {payload['device']}")

    except Exception as e:
        print(f"Error processing message: {e}")

# Setup InfluxDB client
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Setup MQTT client
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Prim client", protocol=mqtt.MQTTv5)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_forever()
