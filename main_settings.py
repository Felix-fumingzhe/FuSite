# encoding = utf-8

import os
from pymongo import MongoClient
from flask import session, request
import eyed3
from datetime import datetime


HOST = "0.0.0.0"
PORT = 80
DEBUG = False
THREADED = False
PAGE = 3 #博客的每页展示数目
EMAIL = "邮箱"  #邮箱
EMAIL_PASSWORD = "邮箱授权码" #邮箱授权码
SMTP_ADDRESS = "smtp.qq.com" #SMTP服务器

directory = (os.path.split(os.path.realpath(__file__))[0]).split("\\")
directory = "/".join(directory)+"/"
# key = os.urandom(24)
key = "JFOSejfj8*(*#(*@F(*JDFIPP@(*}fjs38*@!$^fasfsa"
client = MongoClient()
client_users = client.FuSite.users
client_music = client.FuSite.music
client_blog = client.FuSite.blogs
client_settings = client.FuSite.settings
client_date = client.FuSite.date


def init_session():
    if session.get("error") is None:
        session["error"] = 0
    if session.get("login") is None:
        session["login"] = "not_login"
    if session.get("admin_login") is None:
        session["admin_login"] = "not_admin_login"
    if session.get("login_time") is None:
        session["login_time"] = 1


def history():
    client_users.find()

def get_now_music():
    music_list = os.listdir(directory+"static/music/")
    music_list.sort()
    music_id = 1
    music_dict = {}
    for i in music_list:
        if i == "img":
            continue
        music_directory = directory+"static/music/"+i
        music_index = i.rfind(".")
        music_name = i[:music_index]
        music_info = eyed3.load(music_directory)
        music_dict[str(music_id)] = {"music_name": music_name, "music_artist": music_info.tag.artist,
                                     "music_album": music_info.tag.album}
        music_id += 1
    return music_dict


def history():
    user = client_users.find_one({"用户名": session["username"]})
    if user is not None:
        user["历史记录"].append({"date": datetime.now().strftime("%y-%m-%d %I:%M:%S"),"path":request.full_path})
        client_users.update_one({"用户名": session["username"]}, {"$set": user})

def empty_history(username):
    user = client_users.find_one({"用户名": username})
    if user is not None:
        user["历史记录"] = []
        client_users.update_one({"用户名": username}, {"$set": user})


for root, dirs, files in os.walk(directory + "static/images/users"):
    for d in dirs:
        for root1, dirs1, files1 in os.walk(directory + "static/images/users/" + d):
            for n in files1:
                if client_users.find_one({"个人主页": {"$regex": n}}) is None and client_blog.find_one({"文章内容": {"$regex": n}}) is None:
                    os.remove(directory + f"static/images/users/{d}/{n}")


client_music.drop()
client_music.insert_one(get_now_music())
if os.path.exists(f"{directory}static/images/WordCloud") is False:
    os.mkdir(f"{directory}static/images/WordCloud")
if os.path.exists(f"{directory}static/images/users") is False:
    os.mkdir(f"{directory}static/images/users")
