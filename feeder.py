#!/usr/bin/env python3
import os
import re
import time
import redis
import codecs
REGEX_MESSAGE=re.compile('(?P<action>(\+|\-)?)'+'(?P<rt_prefix>\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?\/\d\d?)', re.MULTILINE)
NEXT_HOP='127.0.0.1'
COMMUNITY_PREFIX='65432:'
data_dir='./raw'
def get_action(action):
    if not action:
        return 'announce'
    if re.match('^\+', action):
        return 'announce'
    if re.match('^\-', action):
        return 'withdraw'

def parse_messages(data):
    messages = []
    for message in REGEX_MESSAGE.finditer(data):
        action = get_action(message.group('action'))
        route = message.group('rt_prefix')
        messages.append(action+':'+route)
    return messages

def load_dir(data_dir):
    community_messages = {}
    for FILENAME in os.listdir(data_dir):
        if FILENAME.endswith('.txt'):
            with codecs.open(os.path.join(data_dir, FILENAME), 'r', encoding='utf-8', errors='ignore') as f:
                data = f.read()
                messages = parse_messages(data)
                community_suffix = FILENAME.replace('.txt', '')
                if messages:
                    community_messages[COMMUNITY_PREFIX+community_suffix] = messages
    return community_messages



#!!!!!!!!!!!!!!!!!!!!TEST
r = redis.Redis(host='localhost', port=6379, db=7)
pipe = r.pipeline()
r.flushdb()                                                                                                                           
msgs = load_dir(data_dir)
for community in msgs.keys():
    count = 0
    for msg in msgs[community]:
        count += 1
        transaction=community+':'+msg
        pipe.rpush('messages',transaction)
        if count % 1000 == 0:
            pipe.execute()
            count = 0
    pipe.execute()

