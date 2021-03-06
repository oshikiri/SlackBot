#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'oshikiri'
__email__ = 't.oshikiri.0137@gmail.com'
__date__ = '2015-02-20'


import os
import sys
import requests
import json
import time

import pdb


SLEEP_TIME = 1


class SlackBot:
    '''Slack用汎用bot

    SlackのAPIを叩いてメッセージをpostしたり情報を取得したりする．
    '''

    def __init__(self, name, icon_emoji=':lips:', token=None):
        '''
        Args
        ===========
        name : string
            Slack上でのbotの名前
        icon_emoji : string, optional (default=':lips:')
            Slack上でbotがアイコンとして使うemojiを指定する
        token : string, optional (default=None)
            Slack の API token
        '''

        self.name = name
        self.icon_emoji = icon_emoji

        if token:
            self.token = token
        elif 'SLACKTOKEN' in os.environ:
            self.token = os.environ['SLACKTOKEN']
        else:
            raise RuntimeError('SLACKTOKEN does not exist.')

    def get_session(self, url, payload):
        '''sleepしてから指定したurlからgetする
        '''
        time.sleep(SLEEP_TIME)

        res = requests.get(url, params=payload)
        res_dict = json.loads(res.text)

        if 'error' in res_dict:
            print(res_dict['error'])
            sys.exit("Error : get_session()")

        return res_dict


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

        res_dict = self.get_session(base_history, payload)
        return res_dict['messages']


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

        return requests.post(base_post, data=payload)


    def post_file(self, path, channels, text):
        '''
        API reference:
        https://api.slack.com/methods/files.upload
        '''

        base_url = 'https://slack.com/api/files.upload'
        payload = {
            'token': self.token,
            'icon_emoji': self.icon_emoji,
            'channels': channels,
            'initial_comment': text
        }
        files = {'file': open(path, 'rb')}
        return requests.post(base_url, data=payload, files=files)


    def get_channel_dict(self):
        ''' channelの名前とidを取得して，辞書にして返す

        API reference:
        https://api.slack.com/methods/channels.list
        '''

        base_url = 'https://slack.com/api/channels.list'
        payload = {'token': self.token, 'exclude_archived': 1}

        res_dict = self.get_session(base_url, payload)

        return {c['name']: c['id'] for c in res_dict['channels']}


    def get_users_list(self):
        '''Slackを使っているユーザーの一覧を辞書にして返す．
        '''

        base_url = 'https://slack.com/api/users.list'
        payload = {'token': self.token}

        res_dict = self.get_session(base_url, payload)

        return {m['id']: m['name'] for m in res_dict['members']}
