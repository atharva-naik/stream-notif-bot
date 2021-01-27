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

def send_message(reddit, user, subject, message):
    reddit.redditor(user).message(subject, message)

def parse_command(reddit, cmd, user, subscribers):
    flag = 0
    cmd = cmd.replace("u/stream-notif-bot", "").strip()
    if cmd.startswith("!subscribe"):
        if user not in subscribers:
            subscribers.append(user)
            flag = 1
        else:
            flag = 2
    # formant for message is !notify: 10 minutes
    elif cmd.startswith("!notify"):
        if user in priviledged_users:
            time_string = cmd.split(':')[-1].strip()
            subject = f"u/heartmyboo is streaming in {time_string}"
            message = f"^(This message was automatically, sent by )[^(stream-notif-bot)](https://atharva-naik.github.io/stream-notif-bot). [^(source code)](https://github.com/atharva-naik/stream-notif-bot). ^(If you want to **unsubscribe** from these messages, contact u/atharvanaik)"
            print(f"{user} asked me to notify that stream will happen in {time_string}")
            flag = 0
            for subscriber in subscribers:
                print(color(f'notifying {subscriber}', fg='red'))
                send_message(reddit, user, subject, message)
        else:
            flag=-1
    else:
        flag=-1
    return subscribers, flag

ctr=0
while True:
    ctr += 1
    loading = '.'.join(["" for i in range(ctr%4+1)])
    for i in range(3-len(loading)):
        loading += " "
    print("    "+color(f" listening {loading} ", bg='blue', style='bold')+f" {len(subscribers)} are subscribed for notifications", end="\r")
    
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
                    user=comment.author.name
                    subject="Thanks for subscribing to u/heartmyboo's streams!"
                    message=f"{user}, you summoned me [here]({comment.context}). I will send you notifications for all of u/heartmyboo's streams :).\n\n ^(This message was automatically, sent by )[^(stream-notif-bot)](https://atharva-naik.github.io/stream-notif-bot). [^(source code)](https://github.com/atharva-naik/stream-notif-bot). ^(If you want to **unsubscribe** from these messages, contact u/atharvanaik)"
                    send_message(reddit, user, subject, message)
                elif flag == 2:
                    print(f"{comment.author.name} is already subscribed")
                elif flag == 0:
                    print(f"{comment.author.name} notified everyone!")
                else:
                    print("No notif or subscribtion request found!")
                    user=comment.author.name
                    subject="You issued an invalid command!"
                    users=', '.join(['u/'+user for user in priviledged_users])
                    message=f"Please use !subscribe to subscribe, and !notif to notify subscribers. Only {users} can notify people. \n\n ^(This message was automatically, sent by )[^(stream-notif-bot)](https://atharva-naik.github.io/stream-notif-bot). [^(source code)](https://github.com/atharva-naik/stream-notif-bot). ^(If you want to **unsubscribe** from these messages, contact u/atharvanaik)"
                    send_message(reddit, user, subject, message)
                    # notified=False
                    # while(not(notified)):
                    #     try:
                    #         users = ', '.join(['u/'+user for user in priviledged_users])
                    #         comment.reply(f"Please use !subscribe to subscribe, and !notif to notify subscribers\n\nOnly {users} can notify people")
                    #         print(f"User {comment.author.name} added to subscribers :)")
                    #         notified=True
                    #     except:
                    #         print("Failed to notify!, retrying in 60s :(")
                    #         for i in tqdm(range(60)):
                    #             time.sleep(1)
                comment.mark_read()
                print(color('————————————————————————————————————————————————————————————————————————————————', fg='#ffa500', style='bold'))
    json.dump(summoners, open('summoners.json', 'w'))
    json.dump(subscribers, open('subscribers.json', 'w'))
    time.sleep(1)
    # os.system("clear")
