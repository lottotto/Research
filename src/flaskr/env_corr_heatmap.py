import os
from datetime import datetime as dt
import pickle as pkl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def make_keys(char, num):
    ret_list = [char+str(i+1).zfill(2)for i in range(num)]
    return ret_list

def env_data_filter():
    key_list = make_keys("il",10)
    key_list += make_keys("im",3)
    key_list += make_keys("en",10)
    return key_list

def convert_chk(data):
    if data == '1':
        return 1.0
    elif data == '0':
        return 0
    else:
        return data

def convert_alp(data):
    if data == 'A':
        return 1
    elif data == 'B':
        return 0.75
    elif data == 'C':
        return 0.25
    elif data == 'D':
        return 0
    else:
        return data

def calc_correspond_index(corr_dataframe):
    corr = corr_dataframe
    ret_list = []
    for i in range(len(corr)):
        corr.iloc[i,i] = 0
    for i in range(len(corr)*len(corr)):
        max_arg = corr.stack().idxmax()
        ans = corr.loc[max_arg]
        if ans > 0.25:
            ret_val = "R={:1.4f}, {}".format(ans, max_arg)
            ret_list.append(ret_val)
            corr.loc[max_arg] = -1
        else:
            break
    return ret_list

def main(dict_list,db_name, col_name):
    date = dt.now().strftime('%Y-%m-%d-%H%M')
    store_path = "fig/{}/{}/{}.png".format(db_name, col_name, date)
    if os.path.exists(store_path):
        with open(store_path.replace('png', 'pkl'),'rb') as f:
            result_list = pkl.loads(f)
        return store_path, result_list
    else:
        try:
            os.makedirs("fig/{}/{}".format(db_name, col_name))
        except:
            pass
        df = pd.DataFrame(dict_list)
        df = df[env_data_filter()]
        df = df.applymap(convert_chk)
        df = df.applymap(convert_alp)
        plt.figure(figsize=(10,10))
        sns.heatmap(df.corr())
        plt.savefig(store_path)
        result_list = calc_correspond_index(df.corr())
        with open(store_path.replace('png', 'pkl'),'wb') as f:
            pkl.dump(result_list, f)
        return store_path, result_list
