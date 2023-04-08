# encoding = utf-8

from pymongo import MongoClient
import hashlib
from .main_settings import get_now_music

client = MongoClient()

client.FuSite.users.insert_one({
    "用户名": "这里填你的用户名", #这里填你的用户名
    "邮箱": "这里填你的邮箱", #这里填你的邮箱
    "密码": hashlib.sha256("这里填你的密码".encode("utf-8")).hexdigest(), #这里填你的密码
    "权限": 3,
    "用户id": "aM3di3j1SpEQkmb",
    "个性签名": "",
    "生日": "",
    "性别": "",
    "年龄": "",
    "个人简介": "",
    "手机号": "",
    "地址": "",
    "头像": "",
    "个人主页": "",
    "爱好": "",
    "历史记录": []
})

get_now_music()