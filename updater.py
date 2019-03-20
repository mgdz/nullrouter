#!/usr/bin/env python3
import git
import os
import redis
import time
import re
COMMUNITY_PREFIX="65432:"
REGEX_MESSAGE=re.compile('(?P<action>(\+|\-)?)'+'(?P<rt_prefix>\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?\/\d\d?)', re.MULTILINE)
repo_path = './raw/repo/test'
repo = git.Repo(repo_path)
cur_revision = repo.head.object.hexsha
r = redis.Redis(host='localhost', port=6379, db=7)
revision = r.get('revision').decode("utf-8")
#update = re.compile('^[\+|\-]\d.*', re.MULTILINE)
while r.get(revision):
    print("waiting...")
    time.sleep(5)
#print("imported revision: ", revision.decode("utf-8"))
#print("current revision: ", sha)

def get_action(action):
    if not action:
        return 'announce'
    if re.match('^\+', action):
        return 'announce'
    if re.match('^\-', action):
        return 'withdraw'

def get_changed_files(revision):
    data=[]
    for item in repo.index.diff(revision):
        if item.a_path.startswith('data/'):
            data.append(item.a_path)
    return data


def get_diff(path, revision):
    data = []
    diff_index = repo.commit(revision).diff(paths=path, create_patch=True)
    diff=diff_index[0].diff.decode("utf-8")
    return diff

def parse_messages(data):
    messages = []
    for message in REGEX_MESSAGE.finditer(data):
        action = get_action(message.group('action'))
        route = message.group('rt_prefix')
        messages.append(action+':'+route)
    return messages   

def load_index():
    community_messages = {}
    changeset = get_changed_files(revision)
    for f in changeset:
        updates=get_diff(f, revision)
        messages=parse_messages(updates)
        community_suffix = os.path.basename(f).replace('.txt', '')
        if messages:
            community_messages[COMMUNITY_PREFIX+community_suffix] = messages
    return community_messages

if cur_revision == revision:
    print ("same version")

msgs = load_index()
for community in msgs.keys():
    for msg in msgs[community]:
        transaction=community+':'+msg
        print(transaction)

