import sys
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from pymongo import MongoClient

mqtt_host=sys.argv[1]
mqtt_topic = "/saito/#"
mongo_client = MongoClient('localhost', 27017)
db = mongo_client.shelter
collection = db.shelter


def insert_document(message,topic):
    json_data = json.loads(message)
    shelter_code = topic.split('/')[-1]
    if len(shelter_code) != 10: #避難所コードは必ず10文字
        return 0
    now = datetime.now()
    print(collection.find_one({"code":shelter_code}))

    if collection.find_one({"code":shelter_code}) is None:
        collection.insert({"datetime":now,"code":shelter_code,"sensor":json_data})
        
    else:
        document = collection.find_one({"code":shelter_code})
        document['sensor'] = json_data
        collection.save(document)


def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    print('Connect')
    client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    subscribed_topic = msg.topic
    message = msg.payload.decode()
    print("{}\t{}\t{}".format(now, subscribed_topic, message))
    insert_document(message,subscribed_topic)


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
