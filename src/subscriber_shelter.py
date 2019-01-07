
# coding: utf-8

import re
import sys
import json
import datetime
import paho.mqtt.client as mqtt
from datetime import datetime as dt
from pymongo import MongoClient
# from calc_remarkable import CalcRemarkProblem
from collections import defaultdict
mqtt_host = sys.argv[1]
mqtt_topic = "/saito/#"
mongo_client = MongoClient('localhost', 27017)
format_datetime_string = "%Y-%m-%d-%H:%M:%S"


# In[3]:

def analysis(document):
    def calc_WBGT(tmp, hum):
        print(tmp, hum)
        WBGT = (0.735*tmp) + (0.0374*hum) + (0.00292*tmp*hum)
        # if WBGT >= 31:
        #     return "暑さ警戒度:{}".format("危険")
        # elif WBGT >=28:
        #     return "暑さ警戒度:{}".format("厳重警戒")
        # elif WBGT >= 25:
        #     return "暑さ警戒度:{}".format("警戒")
        print(WBGT)
        if WBGT >= 21:
            return "暑さ警戒"
        else:
            return "特になし"

    ret_list = []
    WBGT = calc_WBGT(document['sensor']['tmp'], document['sensor']['hum'])
    ret_list.append(WBGT)
    print(ret_list)
    return ret_list


class CalcRemarkProblem():
    def __init__(self, mongo_document):

        #値抜けの可能性あるので、dict.get(key)で値を抽出
        self.document = mongo_document
        self.sensor = mongo_document.get('sensor') #Noneメソッドは.getを持たないので、一度これを挟む
        if self.sensor is not None:
            self.tmp = self.sensor['tmp']
            self.hum = self.sensor['hum']
            self.lux = self.sensor['lux']
            self.co2 = self.sensor['co2']
        else:
            self.tmp = None
            self.hum = None
            self.lux = None
            self.co2 = None

    #熱中症リスクの計算

    def C_or_D(param):
        if param == 'C' or param == 'D' or param == "0":
            return True
        else:
            return False

    def is_None(self, *args):
        if None in args:
            return True
        else:
            False

    def WBGT(self):
        if self.is_None(self.tmp, self.hum) == True:
            return "特になし"
        WBGT = 0.735*self.tmp+0.0374*self.hum+0.00292*self.tmp*self.hum
        if WBGT >= 31:
            return "暑さ警戒度:{}".format("危険")
        elif WBGT >=28:
            return "暑さ警戒度:{}".format("厳重警戒")
        elif WBGT >= 25:
            return "暑さ警戒度:{}".format("警戒")
        elif WBGT >= 21:
            return "暑さ警戒度:{}".format("注意")
        else:
            return "特になし"
    #Cf 環境省熱中症予防情報サイト, http://www.wbgt.env.go.jp/wbgt_detail.php 11月26日閲覧


    #水不足リスクの計算
    def lack_of_water_risk(self):
        drink_water=self.document.get('il01')
        if self.is_None(self.tmp, self.hum, drink_water) == True:
            return "特になし"
        if self.tmp >= 30 and self.hum <=40 and self.C_or_D(drink_water):
            return "水消費量増大リスク"
        else:
            return "特になし"

    #感染症リスクの計算
    def infection_risk(self):
        if self.is_None(self.tmp, self.hum, self.co2) == True:
            return "特になし"
        None_filter = lambda x:x is not None
        temp_list = [self.document.get('sp0'+str(x+1)) for x in range(4)] + [self.document.get('vi0'+str(x+1)) for x in range(3)]
        #temp_list = list(map(int, temp_list))
        temp_list = list(filter(None_filter, temp_list))
        infect_number = sum(list(map(int, temp_list)))

        if self.tmp <= 20 and self.hum <= 40 and infect_number:
            return "感染症蔓延リスクあり"
        else:
            return "特になし"
    # Cf 室温・湿度管理でインフル予防　20度以上、50～60％が理想｜ヘルスＵＰ｜NIKKEI STYLE
    # https://style.nikkei.com/article/DGXKZO93955790T11C15A1W13001 11月26日閲覧


    #睡眠不足リスクの計算
    def lack_of_sleep_risk(self):
        sleep_items = self.document.get('en02')
        if self.is_None(self.tmp, self.lux, sleep_items) == True:
            return "特になし"
        elif self.tmp <= 15 and self.lux > 400 and self.C_or_D(sleep_items):
            return "睡眠不足リスクあり"
        else:
            return "特になし"
    #路上寝泊まりの実体験から。府中市10月28日、寒くてほぼ寝れず。当時気温は15度ほど


    #トイレのリスク
    def toilet_risk(self):
        domestic_water = self.document.get('il06')
        cleaning_toilet= self.document.get('il03')
        sewage         = self.document.get('en07')
        if self.is_None(domestic_water, cleaning_toilet, sewage) == True:
            return "特になし"
        if self.self.C_or_D(domestic_water) and self.C_or_D(cleaning_toilet) and self.C_or_D(sewage):
            return "トイレのリスクあり"
        else:
            return "特になし"


    #調査できているかのリスク
    def research_info_risk(self):
        questionnaire_strtime = self.document.get('questionnaire_time')
        if questionnaire_strtime is None:
            return "情報収拾不安定リスクあり"
        questionnaire_dt = datetime.datetime.strptime(questionnaire_strtime, "%Y-%m-%d-%H:%M:%S")
        if datetime.datetime.now() - questionnaire_dt > datetime.timedelta(days=2):
            return "情報収拾不安定リスクあり"
        else:
            return "特になし"

    def run(self):
        ret_list = []
        ret_list.append(self.WBGT())
        ret_list.append(self.lack_of_water_risk())
        ret_list.append(self.infection_risk())
        ret_list.append(self.lack_of_sleep_risk())
        ret_list.append(self.toilet_risk())
        ret_list.append(self.research_info_risk())
        ret_list = list(set(ret_list))#特になしの重複を削除し、残った特になしを削除
        ret_list.remove('特になし')
        return ret_list


def setting_Mongo(topic):
    db_name = "sub_" + topic.split('/')[2] #sub_test, sub_training, sub_default
    collection_name = topic.split('/')[3]  #201801
    db = mongo_client[db_name]
    collection = db[collection_name]
    return db, collection


# In[5]:


def analysis_problems(document):
    print("ana_pro", document)
    problems = analysis(document)
    # problems = CalcRemarkProblem(document).run() #発生してると考えられる問題をリストで返す。
    print("analysis:", problems)
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
    pub_message = json.dumps(document)
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
