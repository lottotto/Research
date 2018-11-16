import json
import time
import datetime
import threading
import paho.mqtt.client as mqtt

host= "www.ds.se.shibaura-it.ac.jp"
publish_topic_base =    "/saito/training/201802/shelter/app/"
subscribe_topic_base =  "/saito/training/201802/shelter/support/"
port = 1883


def start_subscribe(agent):

    def on_connect(client, userdata, flags, respons_code):
        client.subscribe(subscribe_topic_base+agent.sheler_state['code'])

    def on_message(client, userdata, msg):
        new_shelter_state = json.loads(msg.payload.decode())
        for key, value in new_shelter_state.items():
            agent.shelter_state[key] = value
        print("{}の状態が変化しました".format(agent.shelter_state['code']))

    subscribe_MQTT_client = mqtt.Client(client_id="subscribe_"+agent.name)
    sub
