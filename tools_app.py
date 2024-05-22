# encoding = utf-8

from flask import Blueprint, render_template, session, request
from tools import cloud, translate, ai_draw, date
from main_settings import directory, client_users


tools_app = Blueprint("tools", __name__)


@tools_app.route("/tools")
@tools_app.route("/tools/index")
def tools():
    return render_template("/tools/index.html", username=session["username"])


@tools_app.route("/tools/WordCloud", methods=["GET","POST"])
def tools_WordCloud_word():
    if request.method == "POST":
        img = request.files.get("img")
        words = request.form.get("word")
        if img.filename != "":
            img.save(directory+f"static/images/WordCloud/{session['username']}_img.png")
            cloud(words, True)
        else:
            cloud(words)
        return render_template("tools/WordCloud.html", img="True", username=session["username"], words=words)
    return render_template("tools/WordCloud.html", username=session["username"])


@tools_app.route("/tools/translation")
def tools_translation():
    context = {
        "list": ['中文', '英文', '日文', '韩文', '法文', '西班牙文', '葡萄牙文', '德文', '意大利文', '俄文'],
        "username": session["username"]
    }
    word = request.args.get("word")
    _from = request.args.get("from")
    _to = request.args.get("to")
    if word is not None:
        if _from not in context["list"]+["自动检测"]:
            _from = "自动检测"
        if _to not in context["list"]:
            _to = "英文"
        t = translate(_from, _to, word)
        context["f_word"] = t
        context["word"] = word
        context["from"] = _from
        context["to"] = _to
    return render_template("tools/Translation.html", **context)


@tools_app.route("/tools/date", methods=["GET", "POST"])
def tools_date():
    context = {
        "username": session["username"]
    }
    if request.method == "POST":
        pass
    date_all = date(client_users.find_one({"用户名": context["username"]})["用户id"])
    context["date_all"] = date_all
    return render_template("tools/date.html", **context)


@tools_app.route("/tools/AI_Draw", methods=["GET", "POST"])
def AI_Draw():
    content = {
        "username": session["username"]
    }
    if request.method == "POST":
        text = request.form.get("text")
        size = request.form.get("size")
        url = ai_draw(text, size)
        content["url"] = url
        content["text"] = text
        content["size"] = size
    return render_template("tools/AI_Draw.html", **content)