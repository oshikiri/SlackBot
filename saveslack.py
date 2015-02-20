#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'oshikiri'
__email__ = 't.oshikiri.0137@gmail.com'
__date__ = '2015-02-20'


import sqlite3
import pandas as pd
import pdb

from SlackBot import SlackBot


SQLITE_DATA = './chatdata.sqlite3'
TABLE_NAME = 'history'


if __name__ == '__main__':

    ## Connect to Slack
    sbot = SlackBot('savebot')
    channels = sbot.get_channel_dict()

    columns = ['type', 'subtype', 'purpose', 'channel', 'channel_id',
               'ts', 'user', 'username', 'text']

    ## Connect to SQLite
    con = sqlite3.connect(SQLITE_DATA)
    c = con.cursor()

    query = 'SELECT name FROM sqlite_master;'
    c.execute(query)
    res = c.fetchall()

    for key, item in channels.items():
        print(key)

        if TABLE_NAME in res[0]:
            ## if exists `TABLE_NAME`

            ## 最新のメッセージのtime stampを取得する
            ## 実際の例:
            ##
            ## SELECT * FROM history 
            ## WHERE ts = (
            ##  SELECT max(ts) FROM history WHERE channel = 'tech' 
            ## ) 
            ## AND channel = 'tech' LIMIT 1

            query = ('SELECT * FROM {0} ' 
                     'WHERE ts = ('
                     'SELECT max(ts) FROM {0} WHERE channel = \'{1}\' '
                     ') '
                     'AND channel = \'{1}\' '
                     'LIMIT 1').format(TABLE_NAME, key)
            
            ts = pd.read_sql(query, con).ts
            
            if ts.shape == (0,):
                max_ts = 0
            else:
                max_ts = float(ts)
        else:
            ## if not exists db
            max_ts = 0

        messages = sbot.get_messages(channel=item, oldest=max_ts, count=1000)

        if not messages:
            ## 新しいメッセージが無いとき
            continue

        df = pd.DataFrame(messages, columns=columns)
        df['channel'] = key
        df['channel_id'] = item
        df['username'] = df.user.map(sbot.get_users_list())

        df.to_sql(TABLE_NAME, con, if_exists='append', index=False)
