import paho.mqtt.client as mqtt
import sys
import csv
import json
import os
import pandas as pd
import re


#送るJSONFileを作成
def makeSendJSON(CastDefCsv, SheatPATH):
    CastDef = open(CastDefCsv,'r')
    df_CastDef = pd.read_csv(CastDefCsv, encoding='cp932', header=None)
    ResultDict = {}
    for index, row in df_CastDef.iterrows():
        dst = int(row[0].split('_')[0])
        src = int(row[0].split('_')[1])
        temp_Result = ""

        #dstからsrcまでのイテレータで回す。
        for i in range(dst, src+1):
            FilePATH = makeFilePATH(i,SheatPATH)
            with open(FilePATH,'r') as f:
                temp_Result += f.read()

        #空白の削除
        temp_Result = temp_Result.replace('-','')
        ResultDict[row[1]] = temp_Result
    ResultDict['date'] = "20"+ResultDict['year']+"/"+ResultDict['month']+"/"+ResultDict['day']+' '+ResultDict['hour']+':'+ResultDict['minute']
    del ResultDict['year']
    del ResultDict['month']
    del ResultDict['day']
    del ResultDict['hour']
    del ResultDict['minute']
    del ResultDict['AM']
    del ResultDict['PM']
    code = ResultDict['code']
    SendJSON = json.dumps(ResultDict).encode().decode('unicode-escape')
    CastDef.close()
    return SendJSON,code

def makeFilePATH(Number,SheatPATH):
    FileName = "texts/" + str(Number) + ".txt"
    FilePATH = os.path.join(os.path.split(SheatPATH)[0], FileName)
    return FilePATH

def publish(Host, Topic, CastDefCsv, SheatPATH):
    message,code = makeSendJSON(CastDefCsv, SheatPATH)
    print(message)
    sendTopic = os.path.join(re.sub('pic', 'ocr', Topic), "sh"+code)
    print(sendTopic)
    def on_connect(client, userdata, flags, respons_code):
        client.publish(sendTopic, message)

    def on_publish(client, userdata, result):
        print("Sheat {} was published".format(SheatPATH))
        client.disconnect()

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(Host, port=1883, keepalive=60)
    client.loop_forever()
    return 0



if __name__ == '__main__':
    Host = sys.argv[1]
    Topic = sys.argv[2]
    CastDefCsv = sys.argv[3]
    SheatPATH = sys.argv[4]
    publish(Host, Topic, CastDefCsv, SheatPATH)
