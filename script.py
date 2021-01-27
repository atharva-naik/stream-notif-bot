#!/usr/bin/python
import os
import re
import json
import praw
import tqdm
import time
import colors
import random
import datetime
from tqdm import tqdm
from colors import color
from datetime import datetime
from dotenv import load_dotenv
from praw.models import Redditor, Subreddit

# Enter your correct Reddit information into the variable below
load_dotenv()
userAgent = 'Stream Notif Bot'
ID = os.getenv('ID')
secret = os.getenv('SECRET')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
priviledged_users = os.getenv('PRIVILEDGED_USERS').split(',')
# print(priviledged_users)

reddit = praw.Reddit(user_agent=userAgent, client_id=ID,
                     client_secret=secret, username=username, password=password)
allowed_subs = ['botyard', 'heartmyboo', 'theartiststudio']
summoners = json.load(open('summoners.json', 'r'))
subscribers = json.load(open('subscribers.json', 'r'))

# def clean(text):
#     text = re.sub('u/[^\s]*', '', text)
#     text = re.sub(r'[^\w\s]', '', text)
#     text = ' '.join(text.split())
#     text = text.strip("\n")
#     text = text.strip()

#     return text

def send_message(reddit, user, time_string):
    subject = f"u/heartmyboo is streaming in {time_string}"
    message = f'''This message was automatically, sent by [stream-notif-bot](https://atharva-naik.github.io/stream-notif-bot).\n\n 
    [source code](https://atharva-naik.github.io/stream-notif-bot).\n\n
    If you want to **unsubscribe** from these messages, contact u/atharvanaik'''
    reddit.redditor(user).message(subject, message)

def parse_command(reddit, cmd, user, subscribers):
    flag = 0
    if cmd.startswith("!subscribe"):
        subscribers.append(user)
        flag = 1
    # formant for message is !notify: 10 minutes
    elif cmd.startswith("!notify"):
        if user in priviledged_users:
            time_string = cmd.split(':')[-1].strip()
            for subscriber in subscribers:
                send_message(reddit, user, time_string)
    else:
        flag=-1
    return subscribers, flag

while True:
    print(color("listening ...", bg='blue', style='bold'))
    print(f"{len(subscribers)} are subscribed for notifications")
    for comment in reddit.inbox.unread():
        if comment.type=='username_mention':
            if comment.subreddit.display_name in allowed_subs:
                print(color('————————————————————————————————————————————————————————————————————————————————', fg='#ffa500', style='bold'))
                print(color(f"{comment.author.name} summoned me", fg='yellow'))
                summoners[comment.id]={'author' : comment.author.name, 
                                       'parent_id' : comment.parent_id,
                                       'auhtor_id' : comment.author_fullname,
                                       'fullname' : comment.fullname,
                                       'url' : comment.context,
                                       'is_new' : comment.new,
                                       'date' : comment.created_utc,
                                       'score' : comment.score,
                                       'is_root' : comment.is_root,
                                       'post_id' : comment.submission.id,
                                       'post_title' : comment.link_title,
                                       'timestamp' : comment.created_utc,
                                       'subreddit' : comment.subreddit.display_name}
                subscribers, flag = parse_command(reddit, comment.body, comment.author.name, subscribers)
                if flag == 1:
                    print(f"{comment.author.name} susbcribed!")
                    notified=False
                    while(not(notified)):
                        try:
                            comment.reply("Thanks for subscribing! :)")
                            print(f"User {comment.author.name} added to subscribers :)")
                            notified=True
                        except:
                            print("Failed to notify!, retrying in 60s :(")
                            for i in tqdm(range(60)):
                                time.sleep(1)
                elif flag == 0:
                    print(f"{comment.author.name} notified everyone!")
                else:
                    print("No notif or subscribtion request found!")
                    notified=False
                    while(not(notified)):
                        try:
                            users = ', '.join(['u/'+user for user in priviledged_users])
                            comment.reply(f"Please use !subscribe to subscribe, and !notif to notify subscribers\n\nOnly {users} can notify people")
                            print(f"User {comment.author.name} added to subscribers :)")
                            notified=True
                        except:
                            print("Failed to notify!, retrying :(")
                comment.mark_read()
                print(color('————————————————————————————————————————————————————————————————————————————————', fg='#ffa500', style='bold'))
    json.dump(summoners, open('summoners.json', 'w'))
    json.dump(subscribers, open('subscribers.json', 'w'))
    time.sleep(10)
    # os.system("clear")
