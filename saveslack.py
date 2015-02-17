#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sqlite3
import pandas as pd
from SlackBot import SlackBot
import mysetup as my


if __name__ == '__main__':

    ## Connect to Slack
    sbot = SlackBot(my.botname, my.token)
    channels = sbot.get_channel_dict()

    ## これが全部網羅できているのかよくわからない
    columns = ['type', 'subtype', 'purpose', 'channel', 'channel_id',
               'ts', 'user', 'is_starred',  'text']

    ## Connect to SQLite
    con = sqlite3.connect('./chatdata.sqlite3')
    c = con.cursor()
    table_name = 'history'

    # query = ('CREATE TABLE IF NOT EXISTS ' + table_name 
    #          + ' (' + ','.join(columns) + ') ')
    # c.execute(query)

    query = '''SELECT name FROM sqlite_master WHERE type='table' AND name='table_name';'''
    c.execute(query)
    res = c.fetchall()

    for key, item in channels.items():

        if res:
            ## if exists db
            ## 最新のメッセージのtsを取得する
            query = '''
            SELECT * FROM {0} 
            WHERE ts = (SELECT max(ts) FROM {0}) 
            LIMIT 1'''.format(table_name)
            
            ts = pd.read_sql(query, con).ts
            
            if ts.shape == (0,):
                max_ts = 0
            else:
                max_ts = float(ts)
        else:
            ## if not exists db
            max_ts = 0

        messages = sbot.get_messages(item, oldest=max_ts, count=1000)

        if not messages:
            continue

        df = pd.DataFrame(messages, columns=columns)
        df['channel'] = key
        df['channel_id'] = item

        print(df.head())

        df.to_sql(table_name, con, if_exists='append')

        break
    
