import paho.mqtt.client as mqtt
import base64
from datetime import datetime as dt
import os
import sys
import json
import MAIN
import CastResult_Publish

env_data = json.load(open(sys.argv[1],'r'))
host = env_data["host"]
port = 1883
topic =env_data["topic"]
store_path = env_data["store_path"]
cast_def_path = './Resource/CastDef.csv'
style_def_path = './Resource/OCR_style.csv'
# topic /disfor/training/18000/shelter/pic

def makeStoreDir(subTopic):
    LayterList = list(filter(lambda str:str != '', subTopic.split('/')))
    try:
        os.mkdir(store_path)
    except:
        pass
    path = store_path
    for layer in LayterList:
        # print(store_path, layer)
        path = os.path.join(path, layer)
        try:
            os.mkdir(path)
        except:
            continue

def on_connect(client, userdata, flags, respons_code):
    print('status {0}, host:{1}, topic:{2}'.format(respons_code, host, topic))
    client.subscribe(topic)
    print('Connect')

def on_message(client, userdata, msg):
    makeStoreDir(msg.topic)
    print("subscribe START")
    tempPath = os.path.join(store_path+msg.topic, dt.now().strftime("%Y%m%d-%H%M%S-%f"))
    os.mkdir(tempPath)
    name = os.path.join(tempPath,"form.jpg")
    with open(name, "wb") as fh:
        fh.write(base64.decodebytes(msg.payload))
    print("Image Saved in Path:{}".format(name))
    MAIN.main(srcPATH=name, StyleCsvPath=style_def_path)
    sheat_path = os.path.join(tempPath,"corrected.jpg")
    try:
        CastResult_Publish.publish(Host=host, Topic=msg.topic, CastDefCsv=cast_def_path, SheatPATH=sheat_path)
        print("{} DONE OCR".format(name))
    except:
        pass


if __name__ == '__main__':
    # Publisherと同様に v3.1.1を利用
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port=port, keepalive=60)

    # 待ち受け状態にする
    client.loop_forever()
