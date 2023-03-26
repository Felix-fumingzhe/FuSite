# encoding = utf-8

from flask import Blueprint, render_template, session, request
from tools import cloud, translate, face_info, idiom_search, get_Handwriting, ai_draw
from main_settings import directory


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


@tools_app.route("/tools/face_recognition", methods=["GET", "POST"])
def face_recognition():
    context = {
        "username": session["username"]
    }
    if request.method == "POST":
        request.files.get("face_img").save(directory+f"static/images/Face/{session['username']}.png")
        text = face_info(session["username"])
        context["text"] = text
    return render_template("tools/Face_recognition.html", **context)


@tools_app.route("/tools/idiom_search")
def idiomSearch():
    context = {
        "username": session["username"]
    }
    keyword = request.args.get("keyword")
    if keyword is not None:
        context["idiom_list"] = idiom_search(keyword)
        context["keyword"] = keyword
    return render_template("tools/Idiom_search.html", **context)
    

@tools_app.route("/tools/Handwriting")
def Handwriting():
    content = {
        "username": session["username"]
    }
    msg = request.args.get("msg")
    if msg is not None:
        content["msg"] = msg
        get_Handwriting(msg)
    return render_template("tools/Handwriting.html", **content)


# @tools_app.route("/tools/AI_Chat", methods=["GET", "POST"])
# def AI_Chat():
#     content = {
#         "username": session["username"]
#     }
#     if request.method == "POST":
#         text = request.form.get("text")
#         content["text"] = text
#         chat = chatgpt(text)
#         content["chat"] = chat
#     return render_template("tools/AI_Chat.html", **content)

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