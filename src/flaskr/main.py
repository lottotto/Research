import os
from flask import Flask, request, render_template
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from calc_remarkable import CalcRemarkProblem
from collections import defaultdict

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
    ret_dict = defaultdict(int)
    calc_problem_instance = CalcRemarkProblem(mongo_document)
    temp_keys = []
    temp_keys.append()
    temp_keys.append(calc_problem_instance.lack_of_water_risk())
    temp_keys.append(calc_problem_instance.infection_risk())
    temp_keys.append(calc_problem_instance.lack_of_sleep_risk())
    temp_keys.append(calc_problem_instance.toilet_risk())
    temp_keys.append(calc_problem_instance.research_info_risk())
    continue_problems = mongo_document['problem']
    for key in temp_keys:
        continue_problems[key] += 1

    mongo_document['problem'] = continue_problems

    del ret_dict['特になし']

    return {"code":mongo_document['code'], "problem":list(ret_dict.keys())}


def make_document_list(db_name, collection_name, search_condition=None):
    mongo_app = PyMongo(app, uri="mongodb://localhost:27017/{}".format(db_name))
    return [document for document in mongo_app.db[collection_name].find(search_condition)]


@app.route('/<db_name>/<collection_name>/detail.html', methods=['GET','POST'])
def show_entries(db_name='', collection_name=''):
    entries = make_document_list(db_name, collection_name)
    Line_entries = make_document_list('LINE', collection_name)
    if request.method == 'POST':
        send_LINE(user_id=request.form['user_id'], message=request.form['message'])

    return render_template('detail.html', entries=entries, Line_entries=Line_entries)


@app.route('/<db_name>/<collection_name>/summary.html', methods=['GET','POST'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
