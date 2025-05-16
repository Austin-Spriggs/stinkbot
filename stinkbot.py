from dotenv import load_dotenv
from stinkbot_db.db import connect_db
from stinkbot_util.fart_messages import fart_messages

import os
import praw
import sqlite3
import random

load_dotenv(dotenv_path="stinkbot_config/.env")

reddit = praw.Reddit(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    username=os.getenv('BOT_NAME'),
    password=os.getenv('PASSWORD'),
    user_agent=os.getenv('USER_AGENT')
)

conn = connect_db()
cursor = conn.cursor()

subreddit = reddit.subreddit('testingground4bots')
# this function will be called when user info is needed
def get_user(user):
    cursor.execute("SELECT * FROM stinkbot WHERE user = ?", (user,))
    result = cursor.fetchone()

    if result:
        return result
    else:
        return None
    
# this function is called to add a user to the database, with their first fart
def log_fart(user):
    user_data = get_user(user)
    footer = "\n\n🛠️ Powered by StinkBot v1 — stay tuned for more features and fresher farts!"

    if user_data:
        fart_list = fart_messages()
        fart_counter = user_data[2] + 1

        cursor.execute("UPDATE stinkbot SET fart_count = ? WHERE user = ?", (fart_counter, user))
        message = random.choice(fart_list)(user, fart_counter)

    else:
        cursor.execute("INSERT INTO stinkbot (user, fart_count) VALUES (?, ?)", (user, 1))
        message = f"{user} has farted for the first time! What a stinker!"
    
    conn.commit()
    return message + footer

for comment in subreddit.stream.comments(skip_existing=True):
    if (
        "fart" in comment.body.lower() and
        comment.author is not None and
        comment.author != reddit.user.me()
    ):
        user = comment.author.name
        reply = log_fart(user)

        comment.reply(reply)
