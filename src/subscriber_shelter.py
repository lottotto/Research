
# coding: utf-8

import re
import sys
import json
import datetime
import paho.mqtt.client as mqtt
from datetime import datetime as dt
from pymongo import MongoClient
from calc_remarkable import CalcRemarkProblem
from collections import defaultdict
mqtt_host = sys.argv[1]
mqtt_topic = "/saito/#"
mongo_client = MongoClient('localhost', 27017)
format_datetime_string = "%Y-%m-%d-%H:%M:%S"


# In[3]:

def setting_Mongo(topic):
    db_name = "sub_" + topic.split('/')[2] #sub_test, sub_training, sub_default
    collection_name = topic.split('/')[3]  #201801
    db = mongo_client[db_name]
    collection = db[collection_name]
    return db, collection


# In[5]:


def analysis_problems(document):
    # print("ana_pro", document)
    # problems = analysis(document)
    problems = CalcRemarkProblem(document).run() #発生してると考えられる問題をリストで返す。
    # print("analysis:", problems)
    return problems


# In[8]:


def insert_questionnaire_data(json_data, topic):
    _, collection = setting_Mongo(topic)
    code = topic.split('/')[-1]
    json_data['code'] = code
    if collection.find_one({"code":code}) is None:  #初期登録
        collection.insert(json_data)
    else:
        document = collection.find_one({"code":code})
        for key, value in json_data.items():
            document[key] = value
        collection.save(document)


# In[9]:


def insert_sensor_data(json_data,topic):
    _, collection = setting_Mongo(topic)
    code = topic.split('/')[-1]

    if collection.find_one({"code":code}) is None:
        document = {"code":code,"sensor":json_data}
        collection.insert(document)
    else:
        document = collection.find_one({"code":code})
        document['sensor'] = json_data
        collection.save(document)


# In[10]:


def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    print('Connect')
    client.subscribe(mqtt_topic)


# In[20]:


def publish(host, topic, message):
    pub_client = mqtt.Client()
    pub_client.connect(host=host)
    pub_client.publish(topic=topic, payload=message)
    pub_client.disconnect()

def publish_recode(topic):
    _, collection = setting_Mongo(topic)
    code = topic.split('/')[-1]
    document = collection.find_one({"code":code})
    del document['_id']
    print(document)
    document['problem'] = analysis_problems(document)
    pub_message = json.dumps(document, ensure_ascii=False)
    pub_topic = re.sub("sensor|app", "recode", topic)
    publish(host=mqtt_host, topic=pub_topic, message=pub_message)


# In[21]:


def on_message(client, userdata, msg):
    now = dt.now().strftime(format_datetime_string)
    receive_json_data = json.loads(msg.payload.decode())
    print("{}\t{}\t{}".format(now, msg.topic, msg.payload.decode()))

    recieve_data_type = msg.topic.split('/')[-2]
    if recieve_data_type == 'app':
        insert_questionnaire_data(receive_json_data, msg.topic)
    elif recieve_data_type == 'sensor':
        insert_sensor_data(receive_json_data, msg.topic)

    if recieve_data_type in ['app', 'sensor']:
        publish_recode(msg.topic)


# In[22]:


if __name__ == '__main__':
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(host=mqtt_host)
    mqtt_client.loop_forever()
