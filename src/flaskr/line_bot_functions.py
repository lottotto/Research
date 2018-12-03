from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import sys
import json
import logging
from collections import defaultdict
import paho.mqtt.client as mqtt

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)
register_flag_dict = defaultdict(bool)
change_mode_flag_dict = defaultdict(lambda :{"flag":False, "mode":"training"})
change_event_flag_dict = defaultdict(lambda :{"flag":False, "event":"201801"})
# 環境変数取得
env_data = json.load(open(sys.argv[1],'r'))
# YOUR_CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
# YOUR_CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
# MQTT_BROKER_ADDRESS = os.environ["MQTT_BROKER_ADDRESS"]
YOUR_CHANNEL_ACCESS_TOKEN = env_data["CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = env_data["CHANNEL_SECRET"]
MQTT_BROKER_ADDRESS = env_data["MQTT_BROKER_ADDRESS"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

def registration_process(event):
    register_flag_dict[event.source.user_id] = True
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="名前を入力してください"))

def change_mode(event):
    change_mode_flag_dict[event.source.user_id]['flag'] = True
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="モードコードを入力してください"))

def change_event(event):
    change_event_flag_dict[event.source.user_id]['flag'] = True
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="イベントコードを入力してください"))


def get_topic(user_id):
    mode = change_mode_flag_dict[user_id]["mode"]
    event = change_event_flag_dict[user_id]["event"]
    return "/saito/{}/{}/shelter/line/XXXXX".format(mode, event)

def publish(host,topic, message):
    mqtt_client = mqtt.Client()
    mqtt_client.connect(host=host)
    mqtt_client.publish(topic, message)
    mqtt_client.disconnect()

@app.route("/line")
def hello_world():
    return "hello world!"

@app.route("/line/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print(body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_id = event.source.user_id
    if event.message.text == '登録':
        registration_process(event)
    elif event.message.text == 'モード変更':
        change_mode(event)
    elif event.message.text == 'イベント変更':
        change_event(event)

    elif register_flag_dict[user_id]:
        send_message = json.dumps({"user_name":event.message.text, "user_id":event.source.user_id})
        topic = get_topic(event.source.user_id)
        publish(topic, send_message)
        register_flag_dict[user_id] = False
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="トピック:{}\nユーザー名:{}で登録しました".format(topic, event.message.text)))

    elif change_mode_flag_dict[user_id]['flag']:
        change_mode_flag_dict[user_id]['mode'] = event.message.text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="モードコード:{}に変更しました".format(event.message.text)))
        change_mode_flag_dict[user_id]['flag'] = False

    elif change_event_flag_dict[user_id]['flag']:
        change_event_flag_dict[user_id]['event'] = event.message.text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="イベントコード:{}に変更しました".format(event.message.text)))
        change_event_flag_dict[user_id]['flag'] = False

    elif event.message.text == 'トピック確認':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=get_topic(event.source.user_id)))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="「登録」と入力してください。"))


# if __name__ == "__main__":
# #    app.run()
#     port = int(os.getenv("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)
