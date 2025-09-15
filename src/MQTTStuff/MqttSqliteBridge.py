#!/usr/bin/env python3
'''
Created on Jun 24, 2025

@author: matze
'''

#!/usr/bin/env python3
import sqlite3
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# Database setup
DB_PATH = "/var/lib/grafana/data/sensors.db"
MQTT_BROKER = "localhost"
MQTT_TOPIC = "moisture/data"
MQTT_PORT=1883

def init_db():
    print("Init database:",DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            device TEXT NOT NULL,
            percentage REAL,
            raw_value REAL
        )
    """)
    conn.commit()
    conn.close()

def on_connect(mqtt_client, userdata, flags, rc, properties=None):
    print(f"Connected to MQTT broker with result code {rc}")
    mqtt_client.subscribe(MQTT_TOPIC)
    
def on_message(client, userdata, msg):
    try:
        mystr = msg.payload.decode("utf-8")
        data = json.loads(msg.payload)
        print("data:",mystr)
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO measurements (device, percentage, raw_value)
            VALUES (?, ?, ?)
        """, (data["device"], data["moisture"], data["Raw"]))
        conn.commit()
        print(f"Inserted: {data}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "MQTT Bridge Sqlite", protocol=mqtt.MQTTv5)
    client.on_message = on_message
    client.on_connect = on_connect    
    client.connect(MQTT_BROKER,MQTT_PORT,60)
    client.loop_forever()
