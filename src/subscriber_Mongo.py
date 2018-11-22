import sys
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from pymongo import MongoClient

mqtt_host=sys.argv[1]
mqtt_topic = "/saito/#"
mongo_client = MongoClient('localhost', 27017)


def setting_Mongo(topic):
    db_name = topic.split('/')[2] #test, training, defaultなど
    collection_name = topic.split('/')[3]  #201801
    db = mongo_client[db_name]
    collection = db[collection_name]
    return db, collection

def insert_questionnaire_data(message, topic):
    _, collection = setting_Mongo(topic)
    json_data = json.loads(message)
    code = topic.split('/')[-1]
    questionnaire_now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    json_data['code'] = code
    json_data['questionnaire_time'] = questionnaire_now
    if collection.find_one({"code":code}) is None:
        collection.insert(json_data)

    else:
        document = collection.find_one({"code":code})
        for key, value in json_data.items():
            document[key] = value
        collection.save(document)

def insert_sensor_data(message,topic):
    _, collection = setting_Mongo(topic)
    code = topic.split('/')[-1]
    json_data = json.loads(message)
    sensor_now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    if collection.find_one({"code":code}) is None:
        collection.insert({"sensor_time":sensor_now,"code":code,"sensor":json_data})
    else:
        document = collection.find_one({"code":code})
        document['sensor'] = json_data
        document['sensor_time'] = sensor_now
        collection.save(document)

def insert_line_data(message, topic):
    db = mongo_client['LINE']
    collection = db[topic.split('/')[3]]
    json_data = json.loads(message)
    if collection.find_one({"UserID":json_data['UserID']}) is None:
        collection.insert(json_data)
    else:
        document = collection.find_one({"UserID":json_data['UserID']})
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
    code = subscribed_topic.split('/')[-1]
    recieve_data_type = subscribed_topic.split('/')[-2]
    if recieve_data_type == 'app':
        insert_questionnaire_data(message, subscribed_topic)
    elif recieve_data_type == 'sensor':
        insert_sensor_data(message,subscribed_topic)
    elif recieve_data_type == 'line':
        insert_line_data(message,subscribed_topic)


if __name__ == '__main__':
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(host=mqtt_host)
    mqtt_client.loop_forever()
