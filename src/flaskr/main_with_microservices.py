import os
import json
import threading
import paho.mqtt.client as mqtt
from datetime import datetime as dt
from flask import Flask, request, render_template
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from collections import defaultdict

app = Flask(__name__)
bootstrap = Bootstrap(app)
dt_formats = "%Y-%m-%d-%H:%M:%S"
MQTT_BROKER_ADDRESS = "www.ds.se.shibaura-it.ac.jp"


def send_message(user_id, message, db_name, collection_name):
    # topicの例:"/saito/test/201801/shelter/msg/XXXXXX"
    def publish(topic, message):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(host=MQTT_BROKER_ADDRESS)
        mqtt_client.publish(topic, message)
        mqtt_client.disconnect()

    msg_publish_json_data = json.dumps({"user_id":user_id, "msg":message})
    msg_publish_topic = "/saito/{}/{}/shelter/msg/XXXXXX".format(db_name, collection_name)
    publish(msg_publish_topic, msg_publish_json_data)
    print("Pubscribe:{}\tTopic:{}\tpayload:{}".format(dt.now().strftime(dt_formats), msg_publish_topic, msg_publish_json_data))


def make_document_list(db_name, collection_name, search_condition=None):
    mongo_app = PyMongo(app, uri="mongodb://localhost:27017/{}".format(db_name))
    ret_list = [document for document in mongo_app.db[collection_name].find(search_condition)]
    ret_list = sorted(ret_list, key=lambda x:x['code'])
    return ret_list



@app.route('/shelter/<db_name>/<collection_name>/detail.html', methods=['GET','POST'])
def show_detail(db_name='', collection_name=''):
    entries = make_document_list("flask_"+db_name, collection_name)
    # entries = sorted(entries,key=lambda x:x['code'])
    Line_entries = make_document_list('LINE_'+db_name, collection_name)
    if request.method == 'POST':
        send_message(request.form['user_id'],request.form['message'],db_name,collection_name)
    return render_template('detail.html', entries=entries, Line_entries=Line_entries)



@app.route('/shelter/<db_name>/<collection_name>/summary.html', methods=['GET','POST'])
def show_summary(db_name='', collection_name=''):
    temp_entries = make_document_list("flask_"+db_name, collection_name) #コレクション内にある全ての避難所の状態をリストにしたもの
    entries = []
    for entry in temp_entries:
        if entry['problem'] != []:
            entries.append(entry)
    # entries = list(map(calc_remark, temp_list))
    Line_entries = make_document_list('LINE_'+db_name, collection_name)
    if request.method == 'POST':
        send_message(request.form['user_id'],request.form['message'],db_name,collection_name)
    return render_template('summary.html', summary_entries=entries, Line_entries=Line_entries)


@app.route('/', methods=['GET', "POST"])
def top_page():
    return "URLにdb_nameとcollection_nameをつけてね"

def setting_Mongo(topic, mode):
    db_name = mode + topic.split('/')[2] #sub_test, sub_training, sub_default
    collection_name = topic.split('/')[3]  #201801
    mongo_app = PyMongo(app, uri="mongodb://localhost:27017/{}".format(db_name))
    collection = mongo_app.db[collection_name]
    return db_name, collection

def line_subscribe():
    sub_line_topic = "/saito/+/+/shelter/line/#"
    def on_connect(client, userdata, flags, respons_code):
        print("Subscribe Start. Topic:{}".format(sub_line_topic))
        client.subscribe(sub_line_topic)

    def on_message(client, userdata, msg):
        topic = msg.topic
        db_name, collection = setting_Mongo(topic, mode="LINE_")
        collection.insert_one(json.loads(msg.payload.decode()))

    sub_client = mqtt.Client()
    sub_client.on_connect = on_connect
    sub_client.on_message = on_message
    sub_client.connect(host=MQTT_BROKER_ADDRESS)
    sub_client.loop_forever()

def recode_subscribe():
    sub_recode_topic = "/saito/+/+/shelter/recode/#"
    def on_connect(client, userdata, flags, respons_code):
        print("Subscribe Start. Topic:{}".format(sub_recode_topic))
        client.subscribe(sub_recode_topic)

    def on_message(client, userdata, msg):
        print("Subscribe:{}\tTopic:{}\tpayload:{}".format(dt.now().strftime(dt_formats), msg.topic, msg.payload.decode()))
        topic = msg.topic
        code = topic.split('/')[-1]
        json_data = json.loads(msg.payload.decode())
        db_name, collection = setting_Mongo(topic, mode="flask_")
        if collection.find_one({"code":code}) is None:
            collection.insert_one(json_data)
        else:
            document = collection.find_one({"code":code})
            for key, value in json_data.items():
                document[key] = value
            collection.save(document)

    sub_client = mqtt.Client(client_id="recode_sub")
    sub_client.on_connect = on_connect
    sub_client.on_message = on_message
    sub_client.connect(MQTT_BROKER_ADDRESS)
    sub_client.loop_forever()


if __name__ == '__main__':
    recode_thread = threading.Thread(target=recode_subscribe)
    recode_thread.start()
    line_thread = threading.Thread(target=line_subscribe)
    line_thread.start()
    app.run(host='0.0.0.0', port=8080)
