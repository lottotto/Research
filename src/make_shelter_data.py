
# coding: utf-8

# In[190]:


from sklearn.linear_model import LinearRegression
import pickle as pkl
import random
import numpy as np
from time import sleep
import datetime
import paho.mqtt.client as mqtt
import json
import threading
import sys
import imp

format_sensor_datetime = "%Y-%m-%d-%H:%M:%S"
format_app_datetime = "%Y-%m-%d-%H:%M"
host = 'www.ds.se.shibaura-it.ac.jp'
topic_base = '/saito/test/201901/shelter/'


# In[ ]:


def make_keys(char, num):
    ret_list = [char+str(i+1).zfill(2)for i in range(num)]
    return ret_list


# In[181]:


def set_random_2_digit_number(key_list):
    ret_dict = {}
    for key in key_list:
        ret_dict[key] = str(random.randint(0,50))
    return ret_dict
def set_random_1_digit_number(key_list):
    ret_dict = {}
    for key in key_list:
        ret_dict[key] = str(random.randint(0,5))
    return ret_dict

def make_random_alphabet(key_list):
    choices = ["A","B","C","D"]
    ret_dict = {}
    for key in key_list:
        ret_dict[key] = random.choice(choices)
    return ret_dict

def make_random_checkbox(key_list):
    ret_dict = {}
    for key in key_list:
        ret_dict[key] = str(random.randint(0,1))
    return ret_dict


# In[178]:


def set_number_value():
    in01 = random.randint(2,50) * 10
    in02 = random.randint(1, in01/10) * 10
    in03 = in01-in02
    nm01 = in01
    nm02 = nm01+random.randint(-nm01/2, nm01/2)
    nm03 = random.randint(0, nm01/10)
    nm04 = random.randint(0, nm01/10)
    return {'in01':str(in01),
            'in02':str(in02),
            'in03':str(in03),
            'nm01':str(nm01),
            'nm02':str(nm02),
            'nm03':str(nm03),
            'nm04':str(nm04)}


# In[182]:


def set_dict_data(shelter_name, shelter_code):
    send_dict_data = {"name":shelter_name, "code":shelter_code}
    send_dict_data.update(set_number_value())
    send_dict_data.update(make_random_alphabet(make_keys("il",10)[:6]))
    send_dict_data.update(make_random_checkbox(make_keys("il",10)[6:]))
    send_dict_data.update(make_random_alphabet(make_keys("en",10)[:4]))
    send_dict_data.update(make_random_checkbox(make_keys("en",10)[4:]))
    digit_1 = set_random_1_digit_number(make_keys("ms",7))
    digit_2 = set_random_2_digit_number(make_keys("as",4) + make_keys("sp",4) + make_keys("vi",2))
    send_dict_data.update(digit_1)
    send_dict_data.update(digit_2)
    return send_dict_data


# In[192]:



# In[152]:


def publish(host, topic, message, cl_id):
    mqtt_client = mqtt.Client(client_id=cl_id)
    mqtt_client.connect(host)
    mqtt_client.publish(topic, message)
    mqtt_client.disconnect()


# In[203]:


tmp_predict_model = pkl.load(open("temp_pred_model.pkl",'rb'))
hum_predict_model = pkl.load(open("humi_pred_model.pkl",'rb'))
start_time = datetime.datetime(2019,1,1,0,0)
def shelter_cicle(shelter_info, start_time):

    def make_sensor_data_per_hour(tmp_max, tmp_min, hum_max, hum_min, lux_mean, co2_mean, hours):
        tmp_inputs = np.array([tmp_max, tmp_min] + [hours**(i+1) for i in range(3)]).reshape(-1,5)
#         print(tmp_inputs)
        tmp = float(tmp_predict_model.predict(tmp_inputs))
        hum_inputs = np.array([hum_max, hum_min, tmp] + [hours**(i+1) for i in range(3)]).reshape(-1,6)
        hum = max(float(hum_predict_model.predict(hum_inputs)), 0)
        lux = max(int(random.gauss(lux_mean, 10)),0)
        co2 = int(random.gauss(co2_mean, 10))
        tmp = round(tmp,2)
        hum = round(hum,2)
        return{'tmp':str(tmp), 'hum':str(hum), 'lux':str(lux), 'co2':str(co2)}

    tmp_max = random.randint(-5, 40)
    tmp_min = tmp_max - random.randint(0,20)
    hum_max = random.randint(30,100)
    hum_min = max(hum_max-random.randint(0,50), 0)
    lux_mean = random.choice([0,200,400])
    co2_mean = 400
    for i in range(24):
        if i == 10:
            topic = topic_base+'app/{}'.format(shelter_info['code'])
            date = start_time+datetime.timedelta(hours=i)
            date = date.strftime(format_app_datetime)
            shelter_info['date'] = date
            send_data = json.dumps(shelter_info,ensure_ascii=False)
            publish(host,topic, send_data, cl_id=shelter_info['code'])
            sleep(5)

#         print(tmp_max, tmp_min, hum_max, hum_min, lux_mean, co2_mean, i)
        sensor_data = make_sensor_data_per_hour(tmp_max, tmp_min, hum_max, hum_min, lux_mean, co2_mean, i)
        time = (start_time+datetime.timedelta(hours=i)).strftime(format_sensor_datetime)
        sensor_data['time'] = time
        topic = topic_base+'sensor/{}'.format(shelter_info['code'])
        send_data = json.dumps(sensor_data,ensure_ascii=False)
#         print(send_data)
        publish(host,topic,send_data, cl_id=shelter_info['code'])
        sleep(20+random.randint(-5,5))

# In[204]:
def main(serial_num):
    # mqtt_clients = [mqtt.Client(client_id=str(i)) for i in range(100)]
    shelter_infos = []
    for i in range(150):
        shelter_name = "第{}避難所".format(i)
        shelter_code = "sh990{}{}".format(serial_num,str(i).zfill(3))
        shelter_infos.append(set_dict_data(shelter_name, shelter_code))

    # print(shelter_infos[0], len(shelter_infos))
    thread_list = []
    for info in shelter_infos:
        thread = threading.Thread(target=shelter_cicle,args=(info, start_time))
        thread_list.append(thread)
    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

if __name__ == '__main__':
    main(sys.argv[1])
