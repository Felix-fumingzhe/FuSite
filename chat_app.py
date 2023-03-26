# encoding = utf-8

from flask import Blueprint, render_template, session
from main_settings import client_users


chat_app = Blueprint("chat", __name__)


@chat_app.route("/chat")
@chat_app.route("/chat/index")
def chat():
    users = client_users.find_one({"用户名": session["username"]})
    context = {
        "username": users["用户名"]
    }
    return render_template("chat/index.html", **context)
