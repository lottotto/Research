import json
import threading
import paho.mqtt.client as mqtt
class AgentBase():
    def __init__(self, agent_ID, agent_STATE):
        self.agent_ID = agent_ID
        self.agent_state = agent_STATE
        self.thread_flag = False


    def publish(self, pub_host, pub_topic, message):
        publish_MQTT_client = mqtt.Client(client_id="publish_"+str(self.agent_ID))
        publish_MQTT_client.connect(host=pub_host, port=1883,keepalive=60)
        publish_MQTT_client.publish(topic=pub_topic, payload=message)
        publish_MQTT_client.disconnect()


    def subscribe(self, sub_host, sub_topic):
        def on_connect(client, userdata, flags, respons_code):
            client.subscribe(sub_topic)

        def on_message(client, userdata, msg):
            new_agent_state = json.loads(msg.payload.decode())
            for key, value in new_agent_state.items():
                self.agent_state[key] = value
            print("エージェントID:{}の状態が変化しました".format(self.agent_ID))


        subscribe_MQTT_client = mqtt.Client(client_id="subscribe_"+str(self.agent_ID))
        subscribe_MQTT_client.on_connect = on_connect
        subscribe_MQTT_client.on_message = on_message

        subscribe_MQTT_client.connect(host=sub_host, port=1883, keepalive=60)
        while not self.thread_flag:
            subscribe_MQTT_client.loop()
