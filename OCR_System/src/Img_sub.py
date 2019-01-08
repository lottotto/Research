import paho.mqtt.client as mqtt
import base64
from datetime import datetime as dt
import os
import sys
import MAIN
import CastResult_Publish

host = sys.argv[1]
port = 1883
topic =sys.argv[2]
StorePath = sys.argv[3]
PathToCastDefCsv = './Resource/CastDef20180919.csv'
PathToSheatStyle = './Resource/OCR_style20180919.csv'
# topic /disfor/training/18000/shelter/pic

def makeStoreDir(subTopic):
    LayterList = list(filter(lambda str:str != '', subTopic.split('/')))
    try:
        os.mkdir(StorePath)
    except:
        pass
    path = StorePath
    for layer in LayterList:
        # print(StorePath, layer)
        path = os.path.join(path, layer)
        try:
            os.mkdir(path)
        except:
            continue

def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    client.subscribe(topic)
    print('Connect')

def on_message(client, userdata, msg):
    makeStoreDir(msg.topic)
    print("subscribe START")
    tempPath = os.path.join(StorePath+msg.topic, dt.now().strftime("%Y%m%d-%H%M%S-%f"))
    os.mkdir(tempPath)
    name = os.path.join(tempPath,"form.jpg")
    with open(name, "wb") as fh:
        fh.write(base64.decodebytes(msg.payload))
    print("Image Saved in Path:{}".format(name))
    MAIN.main(srcPATH=name, StyleCsvPath=PathToSheatStyle)
    SheatPATH = os.path.join(tempPath,"corrected.jpg")
    try:
        CastResult_Publish.publish(Host=host, Topic=msg.topic, CastDefCsv=PathToCastDefCsv, SheatPATH=SheatPATH)
        print("{} DONE OCR".format(name))
    except:
        pass


if __name__ == '__main__':
    print(sys.argv)
    # Publisherと同様に v3.1.1を利用
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port=port, keepalive=60)

    # 待ち受け状態にする
    client.loop_forever()
