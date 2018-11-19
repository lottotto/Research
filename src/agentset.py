import csv
import time
import random
import threading
from agentbase import AgentBase

host= "XXXX"
publish_topic_base =    "XXXX"
subscribe_topic_base =  "XXXX"
port = 1883

class AgentSet():
    def __init__(self):
        self.agents = []
    def define_agent(self, agent_id, agent_state):
        class _Agent(AgentBase):
            def __init__(self, agent_id, agent_state):
                super().__init__(agent_ID=agent_id, agent_STATE=agent_state)
                publish_topic = publish_topic_base + self.agent_state['施設名']
                subscribe_topic = subscribe_topic_base + self.agent_state['施設名']
                super().publish(pub_host=host, pub_topic=publish_topic, message=str(agent_id))
                self.temp_thread = threading.Thread(target=super().subscribe, args=(host, subscribe_topic))
                self.temp_thread.start()

            def step(self, *args, **kwargs):
                print("Step処理実行")
                pass

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
            agent.step()
    def terminate_agent(self):
        for agent in self.agents:
            agent.terminate()
    def run(self,state_csv_path,n):
        self.generate_agent(state_csv_path)
        for i in range(n):
            self.step()
<<<<<<< HEAD
            time.sleep()
=======
            time.sleep(1)
>>>>>>> 3049778ab9ebb65114a1b2d4f0ec7ac6e00762ed
        self.terminate_agent()

def main():
    agent_set = AgentSet()
    agent_set.run('shelter_data.csv', n=10)

if __name__ == '__main__':
    main()
