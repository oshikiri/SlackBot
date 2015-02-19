#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'oshikiri'
__email__ = 't.oshikiri.0137@gmail.com'
__date__ = '2015-02-20'


import requests
import json
import time

import pdb


SLEEP_TIME = 1


class SlackBot:
    '''bot for Slack

    SlackのAPIを叩いてメッセージをpostしたり情報を取得したりする．
    '''

    def __init__(self, name, token, icon_emoji=':lips:'):
        '''
        Args
        ===========
        name : string
            Slack上でのbotの名前
        token : string
            Slackのアクセストークン
        icon_emoji : string, optional (default=':lips:')
            Slack上でbotがアイコンとして使うemojiを指定する
        '''

        self.name = name
        self.token = token
        self.icon_emoji = icon_emoji
        self.session = requests.session()

    def get_messages(self, channel=None, 
                     latest=None, oldest=None, count=100):
        '''指定したチャンネルのメッセージの履歴を取得する．

        Args
        ===========
        channel : string, optional (default=None) 
            メッセージを取得したいチャンネル
        latest : string, optional (default=None)
            取得したいメッセージの範囲のうち，最新のtime stamp
        oldest : string, optional (default=None)
            取得したいメッセージの範囲のうち，最古のtime stamp
        count : int, optional (default=100)
            取得する件数
            指定できる範囲は 1 <= count <= 1000

        API reference:
        https://api.slack.com/methods/channels.history
        '''

        base_history = 'https://slack.com/api/channels.history?'
        payload = {
            'token': self.token,
            'channel': channel,
            'count': count,
            'pretty': 1
        }

        if latest:
            payload['latest'] = latest

        if oldest:
            payload['oldest'] = oldest

        time.sleep(SLEEP_TIME)

        res = self.session.get(base_history, params=payload)
        return json.loads(res.text)['messages']


    def post_message(self, text, channel):
        '''チャンネルにtextをポストする．

        Args
        ===========
        text : string
            投稿したいtext
        channel : string 
            メッセージを投稿したいチャンネル

        API reference:
        https://api.slack.com/methods/chat.postMessage
        '''

        base_post = 'https://slack.com/api/chat.postMessage?'
        payload = {
            'token': self.token,
            'username': self.name,
            'icon_emoji': self.icon_emoji,
            'channel': channel,
            'text': text
        }

        time.sleep(SLEEP_TIME)

        return self.session.post(base_post, data=payload)


    def get_channel_dict(self):
        ''' channelの名前とidを取得して，辞書にして返す

        API reference:
        https://api.slack.com/methods/channels.list
        '''

        base_url = 'https://slack.com/api/channels.list'
        payload = {'token': self.token, 'exclude_archived': 1}

        time.sleep(SLEEP_TIME)

        res = self.session.get(base_url, params=payload)
        channels = json.loads(res.text)['channels']

        return {c['name']: c['id'] for c in channels}


    def get_users_list(self):
        '''Slackを使っているユーザーの一覧を辞書にして返す．
        '''

        base_url = 'https://slack.com/api/users.list'
        payload = {'token': self.token}

        time.sleep(SLEEP_TIME)

        res = self.session.get(base_url, params=payload)
        members = json.loads(res.text)['members']

        return {m['id']: m['name'] for m in members}
