import os
from flask import Flask, request, render_template
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

app = Flask(__name__)
bootstrap = Bootstrap(app)
shelter_mongo = PyMongo(app, uri="mongodb://localhost:27017/shelter")
line_mongo = PyMongo(app, uri="mongodb://localhost:27017/LINE")
line_bot_api = LineBotApi(os.environ['LINE_MESSAGE_API_ACCESS_TOKEN'])


def send_LINE(user_id, message):
    try:
        line_bot_api.push_message(user_id,TextSendMessage(text=message))
    except LineBotApiError as e:
        pass

def calc_remark(mongo_document):
    tmp = mongo_document['sensor']['tmp']
    if tmp > 38:
        ret_str = "アツゥイ！"
    else:
        ret_str ="特になし"
    return ret_str

def make_line_entries(collection_name):
    return [document for document in line_mongo.db[collection_name].find()]


@app.route('/<db_name>/<collection_name>/', methods=['GET','POST'])
def show_entries(db_name='', collection_name=''):
    shelter_mongo = PyMongo(app, uri="mongodb://localhost:27017/{}".format(db_name))
    entries = [document for document in shelter_mongo.db[collection_name].find()]
    Line_entries = make_line_entries(collection_name)
    if request.method == 'POST':
        send_LINE(user_id=request.form['user_id'], message=request.form['message'])

    return render_template('new_new_index.html', entries=entries, Line_entries=Line_entries)



@app.route('/', methods=['GET', "POST"])
def top_page():
    return "URLにdb_nameとcollection_nameをつけてね"

if __name__ == '__main__':
    app.run()
