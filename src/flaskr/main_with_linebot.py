import os
import sys
import json
import logging
from flask import Flask, request, render_template
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from calc_remarkable import CalcRemarkProblem
from collections import defaultdict
import line_bot_functions

env_data = json.load(open(sys.argv[1],'r'))
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)
bootstrap = Bootstrap(app)
shelter_mongo = PyMongo(app, uri="mongodb://localhost:27017/shelter")
line_mongo = PyMongo(app, uri="mongodb://localhost:27017/LINE")
line_bot_api = LineBotApi(env_data['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(env_data['CHANNEL_SECRET'])

##LINE_BOT_Server部分
register_flag_dict = defaultdict(bool)
change_mode_flag_dict = defaultdict(lambda :{"flag":False, "mode":"training"})
change_event_flag_dict = defaultdict(lambda :{"flag":False, "event":"201801"})


def send_LINE(user_id, message):
    try:
        line_bot_api.push_message(user_id,TextSendMessage(text=message))
    except LineBotApiError as e:
        pass


def make_document_list(db_name, collection_name, search_condition=None):
    mongo_app = PyMongo(app, uri="mongodb://localhost:27017/{}".format(db_name))
    return [document for document in mongo_app.db[collection_name].find(search_condition)]


@app.route('/shelter/<db_name>/<collection_name>/detail.html', methods=['GET','POST'])
def show_detail(db_name='', collection_name=''):
    entries = make_document_list(db_name, collection_name)
    Line_entries = make_document_list('LINE', collection_name)
    if request.method == 'POST':
        send_LINE(user_id=request.form['user_id'], message=request.form['message'])

    return render_template('detail.html', entries=entries, Line_entries=Line_entries)


@app.route('/shelter/<db_name>/<collection_name>/summary.html', methods=['GET','POST'])
def show_summary(db_name='', collection_name=''):
    temp_list = make_document_list(db_name, collection_name) #コレクション内にある全ての避難所の状態をリストにしたもの
    # entries = list(map(calc_remark, temp_list))
    Line_entries = make_document_list('LINE', collection_name)
    if request.method == 'POST':
        send_LINE(user_id=request.form['user_id'], message=request.form['message'])

    return render_template('summary.html', summary_entries=temp_list, Line_entries=Line_entries)


@app.route('/', methods=['GET', "POST"])
def top_page():
    return "URLにdb_nameとcollection_nameをつけてね"

# Line Bot 部分
@app.route("/line")
def hello_world():
    return "hello world!"

@app.route("/line/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
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
        line_bot_functions.registration_process(event)
    elif event.message.text == 'モード変更':
        line_bot_functions.change_mode(event)
    elif event.message.text == 'イベント変更':
        line_bot_functions.change_event(event)

    elif register_flag_dict[user_id]:
        send_message = json.dumps({"user_name":event.message.text, "user_id":event.source.user_id})
        topic = line_bot_functions.get_topic(event.source.user_id)
        line_bot_functions.publish(env_data['MQTT_BROKER_ADDRESS'], topic, send_message)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
