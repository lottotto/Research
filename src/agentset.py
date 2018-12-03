import csv
import time
import random
import threading
import json
from agentbase import AgentBase
import pandas as pd

host= "XXXX"
publish_topic_base =    "/saito/test/201803/shelter/app/"
subscribe_topic_base =  "/saito/test/201803/shelter/support/"
port = 1883

class AgentSet():
    def __init__(self):
        self.agents = []
    def define_agent(self, agent_id, agent_state):
        class _Agent(AgentBase):
            def __init__(self, agent_id, agent_state):
                super().__init__(agent_ID=agent_id, agent_STATE=agent_state)
                self.publish_topic = publish_topic_base + self.agent_state['code']
                self.subscribe_topic = subscribe_topic_base + self.agent_state['code']
                super().publish(host, self.publish_topic, message=json.dumps(self.agent_state, ensure_ascii=False))
                self.temp_thread = threading.Thread(target=super().subscribe, args=(host, self.subscribe_topic))
                self.temp_thread.start()

            def step(self, *args, **kwargs):
                """
                エージェントのステップ処理記述
                """
                tmp_data_path = 'data_temperuter.csv'
                hum_data_path = 'data_humidity.csv'
                sensor_publish_topic = self.publish_topic.replace('app', 'sensor')
                with open(tmp_data_path, 'r') as f_tmp, open(hum_data_path, 'r') as f_hum:
                    next(f_tmp)
                    next(f_hum)
                    tmp_data = [row for row in csv.reader(f_tmp)]
                    hum_data = [row for row in csv.reader(f_hum)]

                for tmp_row, hum_row in zip(tmp_data, hum_data):
                    tmp = round(float(tmp_row[0]) + random.gauss(float(tmp_row[1]), 1), 2)
                    hum = round(float(hum_row[0]) + random.gauss(float(hum_row[1]), 1), 2)
                    lux = int(random.gauss(500, 100))
                    co2 = int(random.gauss(400, 10))
                    message = {"tmp":tmp,"hum":hum,"lux":lux, "co2":co2}
                    self.publish(host, sensor_publish_topic, message=json.dumps(message))
                    time.sleep(10)
                self.publish(host, self.publish_topic, message=json.dumps(self.agent_state, ensure_ascii=False))

            def terminate(self):
                self.thread_flag = True
                # print("終了処理, agent_id:{} is_alival:{}".format(agent_id, self.temp_thread.isAlive()))

        return _Agent(agent_id, agent_state)
    def generate_agent(self, state_csv_path):
        def make_agent_state(header, row):
            ret_dict = {}
            for column, value in zip(header, row):
                ret_dict[column] = value
            return ret_dict

        with open(state_csv_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for i, row in enumerate(reader):
                temp_state_dict = make_agent_state(header, row)
                temp_agent = self.define_agent(i, temp_state_dict)
                self.agents.append(temp_agent)
    def step(self):
        for agent in self.agents:
            agent.step(tmp_data_path='data_temperuter.csv', hum_data_path='data_humidity.csv')
    def terminate_agent(self):
        for agent in self.agents:
            agent.terminate()
    def run(self,state_csv_path,n):
        self.generate_agent(state_csv_path)
        for i in range(n):
            print(i)
            self.step()
        self.terminate_agent()

def main():
    agent_set = AgentSet()
    agent_set.run('data_shelter3.csv', n=10)

if __name__ == '__main__':
    main()
