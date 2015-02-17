#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
import pdb
import time


SLEEP_TIME = 1


class SlackBot:
    def __init__(self, name, token, icon_emoji=':lips:'):
        self.name = name
        self.token = token
        self.icon_emoji = icon_emoji
        self.session = requests.session()

    def get_messages(self, channel, latest=None, oldest=None, count=100):
        '''指定したチャンネルのメッセージの履歴を取得する．

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
        '''チャンネルにメッセージをポストする．

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
        u''' channelの名前とidを取得

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

        base_url = 'https://slack.com/api/users.list'
        payload = {'token': self.token}

        res = self.session.get(base_url, params=payload)
        members = json.loads(res.text)['members']

        return {m['id']: m['name'] for m in members}
