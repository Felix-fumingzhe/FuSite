# encoding = utf-8

from flask import Flask, redirect, render_template, session, request, jsonify, abort, send_file
from main_settings import key, init_session, DEBUG, HOST, PORT, directory, client_users, history
from users_app import users_app
from music_app import music_app
from chat_app import chat_app
from admin_app import admin_app
from blog_app import blog_app
from tools_app import tools_app
import os
import datetime
import random


app = Flask(__name__)
app.secret_key = key


app.register_blueprint(users_app)
app.register_blueprint(music_app)
app.register_blueprint(chat_app)
app.register_blueprint(admin_app)
app.register_blueprint(blog_app)
app.register_blueprint(tools_app)


@app.before_request
def before():
    init_session()
    if request.headers.get('User-Agent', 'python').startswith('python'):
        return abort(404)
    if session["login_time"] == 1:
        session.permanent = False
    else:
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(days=5)
    if request.path == "/users/login" \
        or request.path == "/users/forget_password" \
        or request.path == "/users/register" \
        or request.path == "/admin/login" \
        or request.path == "/users/send_email":
        return None
    elif request.path.split("/")[1] == "admin" \
        or request.path.split("/")[1] == "admin_users" \
        or request.path.split("/")[1] == "admin_blog" \
        or request.path.split("/")[1] == "upload_admin_images":
        if session["admin_login"] == "admin_login":
            return None
        else:
            return redirect("/admin/login")
    elif request.path.split("/")[1] in ["static", "share"]:
        return None
    elif session["login"] == "login":
        history()
        return None
    else:
        return redirect("/users/login")

@app.template_filter("jscdn")
def cdn(name):
    if name == "bulma":
        return "https://cdn.bootcdn.net/ajax/libs/bulma/0.9.4/css/bulma.min.css"
    elif name == "ionicons":
        return "https://cdn.staticfile.org/ionicons/2.0.1/css/ionicons.min.css"
    elif name == "mui":
        return "https://cdn.bootcdn.net/ajax/libs/mui/3.7.1/js/mui.min.js"
    elif name == "jquery":
        return "https://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js"
    elif name == "APlayer-css":
        return "https://cdn.bootcdn.net/ajax/libs/aplayer/1.10.1/APlayer.min.css"
    elif name == "APlayer-js":
        return "https://cdn.bootcdn.net/ajax/libs/aplayer/1.10.1/APlayer.min.js"
    elif name == "main-css":
        return "https://fu-mingzhe.github.io/static/css/main.css"
    else:
        return None

@app.template_filter("strftime")
def strftime(time):
    if isinstance(time, datetime.datetime):
        return time.strftime("%Y年%m月%d日 %H时%M分%S秒")
    return time

@app.template_filter("handle_time")
def handle_time(time):
    if isinstance(time, datetime.datetime):
        now = datetime.datetime.now()
        timestamp = (now - time).total_seconds()
        if timestamp < 60:
            return "刚刚"
        elif (timestamp >= 60) and (timestamp < 60*60):
            minutes = int(timestamp // 60)
            return "{}分钟前".format(minutes)
        elif (timestamp >= 60*60) and (timestamp < 60*60*24):
            hours = int(timestamp // (60*60))
            return "{}小时前".format(hours)
        else:
            days = int(timestamp // (60*60*24))
            return "{}天前".format(days)
    else:
        return time


@app.template_filter("is_admin")
def is_admin(zz):
    if zz == session.get("admin_name"):
        return True
    else:
        return False

@app.template_filter("color")
def color(username):
    return random.choice(["is-primary", "is-link", "is-info", "is-success", "is-warning", "is-danger"])


@app.template_filter("text_color")
def text_color(name):
    return random.choice(["has-text-primary", "has-text-link", "has-text-info", "has-text-success", "has-text-warning", "has-text-danger"])


@app.route("/index")
@app.route("/")
def index():
    context = {
        "username": session["username"]
    }
    users = client_users.find_one({"用户名": session["username"]})
    if users["个人主页"].isspace() or users["个人主页"] == "":
        users["个人主页"] = None
    context["index_content"] = users["个人主页"]
    context["id"] = users["用户id"]
    if session.get("index_text") is None:
        return render_template("index.html", **context)
    else:
        context["index_text"] = session["index_text"]
        session.pop("index_text")
        return render_template("index.html", **context)


@app.route("/share/<id>")
def share(id):
    user = client_users.find_one({"用户id": id})
    if user is not None:
        content = {
            "username": user["用户名"],
            "index_content": user["个人主页"],
            "Personal_Introduction": user["个人简介"],
            "age": user["年龄"],
            "birthday": user["生日"],
            "sexual": user["性别"],
            "phone": user["手机号"],
            "email": user["邮箱"],
            "head": user["头像"],
            "Personal_signature": user["个性签名"]
        }
        return render_template("share.html", **content)
    abort(404)


@app.route("/upload_images", methods=["POST"])
def upload_images():
    users_image_dir = directory+"static/images/users/{username}".format(username=session["username"])
    if os.path.exists(users_image_dir) is False:
        os.mkdir(users_image_dir)
    file = request.files.get("file")
    file_name = "{}.png".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    file.save(users_image_dir+"/{}".format(file_name))
    return jsonify({"location": "/static/images/users/{username}/{file}".
                    format(username=session["username"], file=file_name)})


@app.route("/static/images/Face/<filename>", methods=["GET", "POST"])
def images_file1(filename):
    try:
        if os.path.exists(directory+"static/images/Face/"+filename):
            if session["login"] == "login" and session["username"] == "".join(filename.split(".")[:-1]):
                return send_file(directory+"static/images/Face/"+filename)
            else:
                abort(404)
        else:
            abort(404)
    except:
        abort(404)

@app.route("/static/images/WordCloud/<filename>", methods=["GET", "POST"])
def images_file2(filename):
    try:
        if os.path.exists(directory+"static/images/WordCloud/"+filename):
            if session["login"] == "login" and (session["username"] == "".join(filename.split(".")[:-1]) or session["username"] + "_img" == "".join(filename.split(".")[:-1])):
                return send_file(directory+"static/images/WordCloud/"+filename)
            else:
                abort(404)
        else:
            abort(404)
    except:
        abort(404)


@app.errorhandler(404)
def html404(error):
    session["error"] = session["error"] + 1
    if session["error"] >= 1:
        print(request.remote_addr)
    return render_template('404.html', error=error), 404


if __name__ == '__main__':
    # socketio.run(app, host=HOST, debug=DEBUG, port=PORT)
    app.run(host=HOST, port=PORT, debug=DEBUG)
    # server = pywsgi.WSGIServer(('0.0.0.0', 5555), app)
    # server.serve_forever()
