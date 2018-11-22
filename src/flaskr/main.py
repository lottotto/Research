import os
from flask import Flask, current_app, request, flash,redirect,url_for,render_template
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['MONGO_URI'] = "mongodb://localhost:27017/shelter"
mongo = PyMongo(app)
line_mongo = PyMongo(app, uri="mongodb://localhost:27017/LINE")
line_bot_api = LineBotApi(os.environ['LINE_MESSAGE_API_ACCESS_TOKEN'])


def send_LINE(user_id, message):
    try:
        line_bot_api.push_message(user_id, text=TextSendMessage(text=message))
    except LineBotApiError as e:
        pass

# def make_index_recode(mongo_document):
#     ret_dict = {}
#     ret_dict['code'] = mongo_document['code']
#     ret_dict['sensor_time'] = mongo_document['sensor_time'].strftime("%Y%m%d-%H:%M")
#     ret_dict['sensor_tmp'] = mongo_document['sensor']['tmp']
#     ret_dict['sensor_hum'] = mongo_document['sensor']['hum']
#     ret_dict['sensor_lux'] = mongo_document['sensor']['lux']
#     ret_dict['sensor_co2'] = mongo_document['sensor']['co2']
#     try:
#         ret_dict['name'] = mongo_document['name']
#     except:
#         pass
#     tmp = ret_dict['sensor_tmp']
#     hum = ret_dict['sensor_hum']
#     if 0.81 * tmp + 0.01 * hum * (0.99 * tmp - 14.3) + 46.3 > 85:
#         ret_dict['remark'] = '【危険】不快指数 85以上！'
#     return ret_dict

def calc_remark(mongo_document):
    tmp = mongo_document['sensor']['tmp']
    if tmp > 38:
        ret_str = "アツゥイ！"
    else:
        ret_str ="特になし"
    return ret_str

def make_line_entries(collection_name):
    print(line_mongo.db[collection_name])
    return [document for document in line_mongo.db[collection_name].find()]


@app.route('/<db_name>/<collection_name>', methods=['GET','POST'])
def show_entries(db_name='', collection_name=''):
    app.config['MONGO_URI'] = "mongodb://localhost:27017/"+db_name
    mongo.init_app(app)
    shelters = mongo.db[collection_name].find()
    entries = []
    for document in shelters:
        document['remark'] = calc_remark(document)
        entries.append(document)
    Line_entries = make_line_entries(collection_name)
    if request.method == 'POST':
        send_LINE(user_id=request.form['user_id'], message=request.form['message'])

    return render_template('new_new_index.html', entries=entries, Line_entries=Line_entries)



@app.route('/', methods=['GET', "POST"])
def top_page():
    return "URLにdb_nameとcollection_nameをつけてね"


# @app.route('/post', methods=['POST'])
# def test_post():
#     print("Execute function test_post")
#     return render_template('index.html')


if __name__ == '__main__':
    app.run()
