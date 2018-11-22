import sys
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from pymongo import MongoClient

mqtt_host=sys.argv[1]
mqtt_topic = "/saito/#"
mongo_client = MongoClient('localhost', 27017)
format_datetime_string = "%Y-%m-%d-%H:%M:%S"


def setting_Mongo(topic):
    db_name = topic.split('/')[2] #test, training, default
    collection_name = topic.split('/')[3]  #201801
    db = mongo_client[db_name]
    collection = db[collection_name]
    return db, collection

def insert_questionnaire_data(json_data, topic):
    _, collection = setting_Mongo(topic)
    code = topic.split('/')[-1]
    questionnaire_now = datetime.now().strftime(format_datetime_string)
    json_data['code'] = code
    json_data['questionnaire_time'] = questionnaire_now
    if collection.find_one({"code":code}) is None:
        collection.insert(json_data)

    else:
        document = collection.find_one({"code":code})
        for key, value in json_data.items():
            document[key] = value
        collection.save(document)

def insert_sensor_data(json_data,topic):
    _, collection = setting_Mongo(topic)
    code = topic.split('/')[-1]
    sensor_now = datetime.now().strftime(format_datetime_string)

    if collection.find_one({"code":code}) is None:
        collection.insert({"sensor_time":sensor_now,"code":code,"sensor":json_data})
    else:
        document = collection.find_one({"code":code})
        document['sensor'] = json_data
        document['sensor_time'] = sensor_now
        collection.save(document)

def insert_line_data(json_data, topic):
    db = mongo_client['LINE']
    collection = db[topic.split('/')[3]]
    if collection.find_one(json_data) is None:
        collection.insert(json_data)
    else:
        document = collection.find_one(json_data)
        document['user_name'] = json_data['user_name']
        document['user_id']   = json_data['user_id']
        collection.save(document)



def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    print('Connect')
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    now = datetime.now().strftime(format_datetime_string)
    receive_json_data = json.loads(msg.payload.decode())
    print("{}\t{}\t{}".format(now, msg.topic, msg.payload))

    recieve_data_type = msg.topic.split('/')[-2]
    if recieve_data_type == 'app':
        insert_questionnaire_data(receive_json_data, msg.topic)
    elif recieve_data_type == 'sensor':
        insert_sensor_data(receive_json_data, msg.topic)
    elif recieve_data_type == 'line':
        insert_line_data(receive_json_data, msg.topic)


if __name__ == '__main__':
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(host=mqtt_host)
    mqtt_client.loop_forever()
