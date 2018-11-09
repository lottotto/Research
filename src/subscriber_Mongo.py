import sys
import paho.mqtt.client as mqtt
from datetime import datetime
from pymongo import MongoClient

mqtt_host=sys.argv[1]
mongo_client = MongoClient('localhost', 27017)
db = client.shelter
collection = db.shelter

def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    print('Connect')
    client.subscribe(topic)


def on_message(client, userdata, msg):
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    subscribed_topic = msg.topic
    message = msg.payload()
    print("{}\t{}\t{}".format(now, subscribed_topic, message))


def setting_mongoDB():
    client = MongoClient('localhost', 27017)
    db = client.shelter
    collection = db.shelter


if __name__ == '__main__':



    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(host=mqtt_host)
    mqtt_client.loop_forever()
