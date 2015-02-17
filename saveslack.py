#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sqlite3
import pandas as pd

from SlackBot import SlackBot
import mysetup as my

import pdb


SQLITE_DATA = './chatdata.sqlite3'
TABLE_NAME = 'history'


if __name__ == '__main__':

    ## Connect to Slack
    sbot = SlackBot(my.botname, my.token)
    channels = sbot.get_channel_dict()

    columns = ['type', 'subtype', 'purpose', 'channel', 'channel_id',
               'ts', 'user', 'username', 'text']

    ## Connect to SQLite
    con = sqlite3.connect(SQLITE_DATA)
    c = con.cursor()

    query = ('SELECT name '
             'FROM sqlite_master '
             'WHERE type=\'table\' AND name=\'table_name\';')
    c.execute(query)
    res = c.fetchall()

    for key, item in channels.items():
        print(key)

        if res:
            ## if exists db
            ## 最新のメッセージのtime stampを取得する
            query = ('SELECT * FROM {0} ' 
                     'WHERE ts = (SELECT max(ts) FROM {0})' 
                     'LIMIT 1').format(TABLE_NAME)
            
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
            ## 新しいメッセージが無いとき
            continue

        df = pd.DataFrame(messages, columns=columns)
        df['channel'] = key
        df['channel_id'] = item
        df['username'] = df.user.map(sbot.get_users_list())

        df.to_sql(table_name, con, if_exists='append', index=False)
