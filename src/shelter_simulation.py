import json
import time
import datetime
import threading
import paho.mqtt.client as mqtt

host= "www.ds.se.shibaura-it.ac.jp"
publish_topic_base =    "/saito/training/201802/shelter/app/"
subscribe_topic_base =  "/saito/training/201802/shelter/support/"
port = 1883
threads = {}

class AgentBase():
    def __init__(self, agent_ID, agent_STATE):
        self.agent_ID = agent_ID
        self.agent_state = agent_STATE
        self.thread_flags = False
    def publish(self, pub_host, pub_topic):
        publish_MQTT_client = mqtt.Client(client_id="publish_"+str(self.agent_ID))
        publish_MQTT_client.connect(host=pub_host, port=1883,keepalive=60)
        message = json.dumps(self.agent_state)
        publish_MQTT_client.publish(topic=pub_topic, payload=message)
        publish_MQTT_client.disconnect()
    def subscribe(self, sub_host, sub_topic):

        def on_connect(client, userdata, flags, respons_code):
            client.subscribe(sub_topic)
            if self.thread_flags:
                client.disconnect()

        def on_message(client, userdata, msg):
            new_agent_state = json.loads(msg.payload.decode())
            for key, value in new_agent_state.items():
                self.agent_state[key] = value
            print("エージェントID:{}の状態が変化しました".format(self.agent_ID))

        def on_subscribe(client, userdata, mid, granted_qos):
            if self.thread_flags:
                client.disconnect()

        subscribe_MQTT_client = mqtt.Client(client_id="subscribe_"+str(self.agent_ID))
        subscribe_MQTT_client.on_connect = on_connect
        subscribe_MQTT_client.on_message = on_message
        subscribe_MQTT_client.on_subscribe = on_subscribe

        subscribe_MQTT_client.connect(host=sub_host, port=1883, keepalive=60)
        while not self.thread_flags:
            subscribe_MQTT_client.loop()

class Agent(AgentBase):
    def __init__(self, agent_id, agent_state):
        super().__init__(agent_ID=agent_id, agent_STATE=agent_state)
        publish_topic = publish_topic_base + self.agent_state['code']
        subscribe_topic = subscribe_topic_base + self.agent_state['code']
        super().publish(pub_host=host, pub_topic=publish_topic)
        self.temp_thread = threading.Thread(target=super().subscribe, args=(host, subscribe_topic))
        self.temp_thread.start()

    def step(self, *args, **kwargs):
        print("Step処理実行中")
        pass

    def terminate(self):
        print("終了処理")
        self.thread_flag = True

class AgentSet():
    def __init__(self):
        self.agents = []
    def define_agent(self, agent_id, agent_state):
        class _Agent(AgentBase):
            def __init__(self, agent_id, agent_state):
                super().__init__(agent_ID=agent_id, agent_STATE=agent_state)
                publish_topic = publish_topic_base + self.agent_state['code']
                subscribe_topic = subscribe_topic_base + self.agent_state['code']
                super().publish(pub_host=host, pub_topic=publish_topic)
                self.temp_thread = threading.Thread(target=super().subscribe, args=(host, subscribe_topic))
                self.temp_thread.start()

            def step(self, *args, **kwargs):
                print("Step処理実行")
                pass

            def terminate(self):
                print("終了処理")
                self.thread_flag = True

        return _Agent(agent_id, agent_state)

    def generate_agent(self, n):
        for i in range(n):
            temp_agent = self.define_agent(i, {'code':'sh'+str(10000000+i)})
            self.agents.append(temp_agent)

    def step(self):
        for agent in self.agents:
            agent.step()

    def terminate_agent(self):
        for agent in self.agents:
            agent.terminate()
if __name__ == '__main__':
    main()
