from flask import Flask, current_app, request, flash,redirect,url_for,render_template
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['MONGO_URI'] = "mongodb://localhost:27017/shelter"
app.config['MONGO_HOST'] = "localhost"
app.config['MONGO_PORT'] = 27017
app.config['MONGO_DBNAME'] = "shelter"
mongo = PyMongo(app)


def make_index_recode(mongo_document):
    ret_dict = {}
    ret_dict['code'] = mongo_document['code']
    ret_dict['datetime'] = mongo_document['datetime'].strftime("%Y年%m月%d日 %H時%M分")
    temperature = mongo_document['sensor']['tmp']
    ret_dict['sensor_tmp'] = temperature
    humidity = mongo_document['sensor']['hum']
    ret_dict['sensor_hum'] = humidity
    ret_dict['sensor_lux'] = mongo_document['sensor']['lux']
    ret_dict['sensor_co2'] = mongo_document['sensor']['co2']
    if 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3 > 85:
        ret_dict['remark'] = '【危険】不快指数 85以上！'
    return ret_dict


@app.route('/', methods=['GET', "POST"])
def show_entries():
    shelters = mongo.db.shelter.find()
    entries = []
    for document in shelters:
        temp_dict = make_index_recode(document)
        entries.append(temp_dict)

    return render_template('index.html', entries=entries)


# @app.route('/post', methods=['POST'])
# def test_post():
#     print("Execute function test_post")
#     return render_template('index.html')


if __name__ == '__main__':
    app.run()