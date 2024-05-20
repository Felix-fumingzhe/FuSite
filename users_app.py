# encoding = utf-8

from flask import render_template, request, Blueprint, redirect, abort, session
from main_settings import client_users, directory, client_blog
import hashlib
import random
from tools.send_email import send_email
import os
import datetime


users_app = Blueprint("users", __name__)


@users_app.route("/users/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        remember = request.form.get("remember")
        username_Or_email = request.form["username_Or_email"]
        password1 = request.form["password"]
        password = hashlib.sha256(password1.encode("utf-8")).hexdigest()
        context = {
            "username_Or_email": username_Or_email,
            "password": password1,
            "remember": remember
        }
        users_username = client_users.find_one({"用户名": username_Or_email})
        users_email = client_users.find_one({"邮箱": username_Or_email})
        if users_username is not None:
            users = client_users.find_one({"用户名": username_Or_email, "密码": password})
            if users is not None:
                if users["权限"] == 2:
                    context["error"] = "您的账号已禁用请联系管理员"
                    return render_template("users/login.html", **context)
                session["login"] = "login"
                session["username"] = users["用户名"]
                session["index_text"] = "欢迎"+users["用户名"]+"登录"
                if users["年龄"] != "":
                    sr_sp = users["生日"].split("-")
                    sr_date = datetime.datetime(int(sr_sp[0]), int(sr_sp[1]), int(sr_sp[2]))
                    now = datetime.datetime.today()
                    users["年龄"] = str((now - sr_date).days // 365) + "岁"
                    client_users.update_one({"用户名": session["username"]}, {"$set": users})
                return redirect("/")
            else:
                context["error"] = "密码错误"
                return render_template("users/login.html", **context)
        elif users_email is not None:
            users = client_users.find_one({"邮箱": username_Or_email, "密码": password})
            if users is not None:
                if users["权限"] == 2:
                    context["error"] = "您的账号已禁用请联系管理员"
                    return render_template("users/login.html", **context)
                session["login"] = "login"
                session["username"] = users["用户名"]
                session["index_text"] = "欢迎"+users["用户名"]+"登录"
                if remember == "on":
                    session["login_time"] = 2
                else:
                    session["login_time"] = 1
                users = client_users.find_one({"用户名": session["username"]})
                if users["年龄"] != "":
                    sr_sp = users["生日"].split("-")
                    sr_date = datetime.datetime(int(sr_sp[0]), int(sr_sp[1]), int(sr_sp[2]))
                    now = datetime.datetime.today()
                    users["年龄"] = str((now - sr_date).days // 365) + "岁"
                    client_users.update_one({"用户名": session["username"]}, {"$set": users})
                return redirect("/")
            else:
                context["error"] = "密码错误"
                return render_template("users/login.html", **context)
        else:
            context["error"] = "用户名或邮箱错误"
            return render_template("users/login.html", **context)
    context = {}
    if session.get("login_text") is not None:
        context = {
            "login_text": session.get("login_text")
        }
        session.pop("login_text")
    return render_template("users/login.html", **context)


@users_app.route("/users/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password1 = request.form["password1"]
        verification = request.form["verification"]
        context = {
            "username": username,
            "email": email,
            "password": password,
            "password1": password1,
            "verification": verification
        }
        if password != password1:
            context["error"] = "两次输入的密码不一致"
            return render_template("users/register.html", **context)
        elif username.isspace():
            context["error"] = "用户名不能为空"
            return render_template("users/register.html", **context)
        elif password.isspace() or password1.isspace():
            context["error"] = "密码不能为空"
            return render_template("users/register.html", **context)
        elif session.get("verification") is None:
            context["error"] = "请先获取验证码"
            return render_template("users/register.html", **context)
        elif datetime.datetime.now() > datetime.datetime(session["verification"][3][0],
                                                         session["verification"][3][1],
                                                         session["verification"][3][2],
                                                         session["verification"][3][3],
                                                         session["verification"][3][4],
                                                         session["verification"][3][5]):
            context["error"] = "验证码已过期，请重新获取"
            return render_template("users/register.html", **context)
        elif username != session.get("verification")[0]:
            context["error"] = "获取验证码时和现在的用户名不一样"
            return render_template("users/register.html", **context)
        elif email != session.get("verification")[1]:
            context["error"] = "获取验证码时和现在的邮箱不一样"
            return render_template("users/register.html", **context)
        elif verification != session.get("verification")[2]:
            context["error"] = "验证码有误"
            return render_template("users/register.html", **context)
        else:
            session.pop("verification")
            password = hashlib.sha256(password.encode("utf-8")).hexdigest()
            user_list = list(client_users.find())
            id_list = []
            for i in user_list:
                id_list.append(i["用户id"])
            user_id = ""
            while True:
                for i in range(15):
                    user_id += random.choice("1234567890QERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm")
                if user_id not in id_list:
                    break
                else:
                    user_id = ""
            client_users.insert_one({
                "用户名": username,
                "邮箱": email,
                "密码": password,
                "权限": 1,
                "用户id": user_id,
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
            session["login_text"] = "注册成功请登录"
            return redirect("/users/login")
    return render_template("users/register.html")


@users_app.route("/users/forget_password", methods=["GET", "POST"])
def forget_password():
    if request.method == "POST":
        username_Or_email = request.form["username_Or_email"]
        password = request.form["password"]
        password1 = request.form["password1"]
        verification = request.form["verification"]
        users_username = client_users.find_one({"用户名": username_Or_email})
        users_email = client_users.find_one({"邮箱": username_Or_email})
        context = {
            "username_Or_email": username_Or_email,
            "password": password,
            "password1": password1,
            "verification": verification
        }
        if password != password1:
            context["error"] = "两次输入的密码不一致"
            return render_template("users/forget_password.html", **context)
        elif password.isspace() or password1.isspace():
            context["error"] = "密码不能为空"
            return render_template("users/forget_password.html", **context)
        elif session.get("verification_forget") is None:
            context["error"] = "请先获取验证码"
            return render_template("users/forget_password.html", **context)
        elif datetime.datetime.now() > datetime.datetime(session["verification_forget"][3][0],
                                                         session["verification_forget"][3][1],
                                                         session["verification_forget"][3][2],
                                                         session["verification_forget"][3][3],
                                                         session["verification_forget"][3][4],
                                                         session["verification_forget"][3][5]):
            context["error"] = "验证码已过期，请重新获取"
            return render_template("users/forget_password.html", **context)
        if users_username is not None:
            if session["verification_forget"][2] != verification:
                context["error"] = "验证码有误"
                return render_template("users/forget_password.html", **context)
            else:
                session.pop("verification_forget")
                users = client_users.find_one({"用户名": username_Or_email})
                users["密码"] = hashlib.sha256(password.encode("utf-8")).hexdigest()
                client_users.update_one(users_username, {"$set": users})
                session["login_text"] = "密码修改成功"
                return redirect("/users/login")
        elif users_email is not None:
            if session["verification_forget"][2] != verification:
                context["error"] = "验证码有误"
                return render_template("users/forget_password.html", **context)
            else:
                session.pop("verification_forget")
                users = client_users.find_one({"邮箱": username_Or_email})
                users["密码"] = hashlib.sha256(password.encode("utf-8")).hexdigest()
                client_users.update_one(users_email, {"$set": users})
                session["login_text"] = "密码修改成功"
                return redirect("/users/login")
        else:
            context["error"] = "获取验证码时和现在的用户名或邮箱不一样"
            return render_template("users/forget_password.html", **context)
    return render_template("users/forget_password.html")


@users_app.route("/users/login_out")
def login_out():
    session["login_text"] = session["username"]+",您已成功退出登录"
    session.pop("username")
    session["login"] = "not_login"
    return redirect("/users/login")


@users_app.route("/users/profile")
def profile():
    users = client_users.find_one({"用户名": session["username"]})
    if session.get("profile_text") is not None:
        text = session["profile_text"]
        session.pop("profile_text")
        return render_template("users/profile.html", **users, profile_text=text)
    else:
        return render_template("users/profile.html", **users)


@users_app.route("/users/profile_editor", methods=["GET", "POST"])
def editor():
    users = client_users.find_one({"用户名": session["username"]})
    if request.method == "POST":
        gxqm = request.form["gxqm"]
        xb = request.form.get("xb")
        sjh = request.form["sjh"]
        sr = request.form["sr"]
        if sr != "":
            sr_sp = sr.split("-")
            sr_date = datetime.datetime(int(sr_sp[0]), int(sr_sp[1]), int(sr_sp[2]))
            now = datetime.datetime.today()
            users["年龄"] = str((now-sr_date).days//365)+"岁"
        else:
            users["年龄"] = ""
        head_file = request.files["head"]
        if head_file.filename != "":
            users["头像"] = head_file.filename[head_file.filename.rfind("."):]
            head_file.save(directory+"static/images/users/{name}.png".format(name=session["username"]))
        dz = request.form["dz"]
        grjj = request.form["grjj"]
        ah = request.form["ah"]
        users["个性签名"] = gxqm
        if xb is not None:
            users["性别"] = xb
        else:
            users["性别"] = ""
        users["手机号"] = sjh
        users["生日"] = sr
        users["爱好"] = ah
        users["地址"] = dz
        users["个人简介"] = grjj
        client_users.update_one({"用户名": session["username"]}, {"$set": users})
        session["profile_text"] = "个人信息修改成功"
        return redirect("/users/profile")
    context = {
        "gxqm": users["个性签名"],
        "xb": users["性别"],
        "sjh": users["手机号"],
        "sr": users["生日"],
        "ah": users["爱好"],
        "dz": users["地址"],
        "grjj": users["个人简介"],
    }
    return render_template("users/profile_editor.html", **users, **context)


@users_app.route("/users/profile_home", methods=["GET", "POST"])
def profile_home():
    users = client_users.find_one({"用户名": session["username"]})
    if request.method == "POST":
        content = request.form["content"]
        users["个人主页"] = content
        client_users.update_one({"用户名": session["username"]}, {"$set": users})
        session["profile_text"] = "个人主页修改成功"
        return redirect("/users/profile")
    return render_template("users/profile_home.html", **users)


@users_app.route("/users/change_username", methods=["GET", "POST"])
def change_username():
    users = client_users.find_one({"用户名": session["username"]})
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        context = {
            "username": username,
            "password": password
        }
        users_username = client_users.find_one({"用户名": username})
        if username.isspace():
            context["error"] = "用户名不能为空"
            return render_template("users/change_username.html", **users, **context)
        elif username == session["username"]:
            context["error"] = "用户名不能和现在一样"
            return render_template("users/change_username.html", **users, **context)
        elif username.isspace():
            context["error"] = "用户名不能为空"
            return render_template("users/change_username.html", **users, **context)
        elif users_username is not None:
            context["error"] = "用户名已存在"
            return render_template("users/change_username.html", **users, **context)
        elif hashlib.sha256(password.encode("utf-8")).hexdigest() != users["密码"]:
            context["error"] = "密码错误"
            return render_template("users/change_username.html", **users, **context)
        else:
            ago_username = session["username"]
            session["username"] = username
            os.rename(directory+"static/images/users/{}.png".format(ago_username),
                        directory+"static/images/users/{name}.png".format(name=username))
            os.rename(directory+"static/images/users/{}".format(ago_username),
                        directory+"static/images/users/{}".format(username))
            session["profile_text"] = "用户名更改成功"
            users["用户名"] = username
            client_users.update_one({"用户名": ago_username}, {"$set": users})
            user_blogs = client_blog.find({"作者": ago_username})
            if user_blogs is not None:
                client_blog.update_many({"作者":ago_username},{"$set":{"作者":username}})
                user_blogs = client_blog.find({"作者": username})
                for i in list(user_blogs):
                    id = i["文章id"]
                    i["文章内容"] = i["文章内容"].replace("../static/images/users/"+ago_username, "../static/images/users/"+username)
                    client_blog.update_one({"文章id": id}, {"$set": i})
            return redirect("/users/profile")
    return render_template("users/change_username.html", **users)


@users_app.route("/users/change_email", methods=["GET", "POST"])
def change_email():
    users = client_users.find_one({"用户名": session["username"]})
    if request.method == "POST":
        email = request.form["email"]
        verification = request.form["verification"]
        context = {
            "email": email,
            "verification": verification
        }
        if session.get("verification_change_email") is None:
            context["error"] = "请先获取验证码"
            return render_template("users/change_email.html", **users, **context)
        elif datetime.datetime.now() > datetime.datetime(session["verification_change_email"][3][0],
                                                        session["verification_change_email"][3][1],
                                                        session["verification_change_email"][3][2],
                                                        session["verification_change_email"][3][3],
                                                        session["verification_change_email"][3][4],
                                                        session["verification_change_email"][3][5]):
            context["error"] = "验证码已过期，请重新获取"
            return render_template("users/change_email.html", **users, **context)
        elif session["verification_change_email"][1] != email:
            context["error"] = "获取验证码时和现在的邮箱不一样"
            return render_template("users/change_email.html", **users, **context)
        elif verification != session["verification_change_email"][2]:
            context["error"] = "验证码有误"
            return render_template("users/change_email.html", **users, **context)
        else:
            session.pop("verification_change_email")
            users["邮箱"] = email
            client_users.update_one({"用户名": session["username"]}, {"$set": users})
            session["profile_text"] = "邮箱修改成功"
            return redirect("/users/profile")

    return render_template("users/change_email.html", **users)


@users_app.route("/users/change_password", methods=["GET", "POST"])
def change_password():
    users = client_users.find_one({"用户名": session["username"]})
    if request.method == "POST":
        password = request.form["password"]
        password1 = request.form["password1"]
        verification = request.form["verification"]
        context = {
            "password": password,
            "password1": password1,
            "verification": verification
        }
        if password != password1:
            context["error"] = "两次输入的密码不一致"
            return render_template("users/change_password.html", **users, **context)
        elif password.isspace() or password1.isspace():
            context["error"] = "密码不能为空"
            return render_template("users/change_password.html", **users, **context)
        elif session.get("verification_change") is None:
            context["error"] = "请先获取验证码"
            return render_template("users/change_password.html", **users, **context)
        elif datetime.datetime.now() > datetime.datetime(session["verification_change"][3][0],
                                                            session["verification_change"][3][1],
                                                            session["verification_change"][3][2],
                                                            session["verification_change"][3][3],
                                                            session["verification_change"][3][4],
                                                            session["verification_change"][3][5]):
            context["error"] = "验证码已过期，请重新获取"
            return render_template("users/forget_password.html", **users, **context)
        elif verification != session["verification_change"][2]:
            context["error"] = "验证码有误"
            return render_template("users/forget_password.html", **users, **context)
        else:
            session.pop("verification_change")
            users = client_users.find_one({"用户名": session["username"]})
            users["密码"] = hashlib.sha256(password.encode("utf-8")).hexdigest()
            client_users.update_one({"用户名": session["username"]}, {"$set": users})
            session["profile_text"] = "密码修改成功"
            return redirect("/users/profile")
    return render_template("users/change_password.html", **users)


@users_app.route("/users/add_blog", methods=["GET","POST"])
def usres_add_blog():
    if request.method == "POST":
        bt = request.form.get("bt")
        ms = request.form.get("ms")
        content = request.form.get("content")
        now = datetime.datetime.now()
        user_list = list(client_blog.find())
        id_list = []
        for i in user_list:
            id_list.append(i["文章id"])
        word_id = ""
        while True:
            for i in range(20):
                word_id += random.choice("1234567890QERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm")
            if word_id not in id_list:
                break
            else:
                word_id = ""
        client_blog.insert_one({
            "标题": bt,
            "描述": ms,
            "作者": session["username"],
            "文章内容": content,
            "浏览量": "0",
            "是否热门": "否",
            "上传日期": now,
            "修改日期": now,
            "文章id": word_id
        })
        session["profile_text"] = "文章添加成功"
        return redirect("/users/profile")
    user = client_users.find_one({"用户名": session["username"]})
    return render_template("users/add_blog.html", **user)


@users_app.route("/users/blogs_info")
def users_blogs_info():
    if request.args.get("delete") == "delete" and client_blog.find_one({"文章id": request.args.get("id")}) in client_blog.find({"作者": session["username"]}):
        client_blog.delete_one({"文章id": request.args.get("id")})
        session["profile_text"] = "文章删除成功"
        return redirect("/users/profile")
    blogs = list(client_blog.find({"作者":session["username"]}).sort("上传日期"))
    context = {
        "用户名": session["username"],
        "blogs": blogs
    }
    return render_template("users/blogs_info.html", **context)


@users_app.route("/users/editor_blog", methods=["GET", "POST"])
def editor_blog():
    if request.method == "POST":
        blog = client_blog.find_one({"文章id": request.form.get("id")})
        blog["标题"] = request.form.get("bt")
        blog["描述"] = request.form.get("ms")
        blog["文章内容"] = request.form.get("content")
        blog["修改日期"] = datetime.datetime.now()
        client_blog.update_one({"文章id": request.form.get("id")},{"$set":blog})
        session["profile_text"] = "修改文章成功"
        return redirect("/users/profile")
    blog = client_blog.find_one({"文章id": request.args.get("id")})
    if blog in list(client_blog.find({"作者": session["username"]})):
        return render_template("users/editor_blog.html", blog=blog)
    else:
        abort(404)


@users_app.route("/users/settings")
def setting():
    return render_template("users/settings.html")


@users_app.route("/users/info")
def settings():
    return render_template("users/info.html")


@users_app.route("/users/send_email", methods=["GET", "POST"])
def send_e():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        email_type = request.form["type"]
        user_email = client_users.find_one({"邮箱": email})
        user_username = client_users.find_one({"用户名": username})
        if email_type == "register":
            if user_email is None:
                if user_username is None:
                    session["verification"] = send_email(email, username)
                    return "3"
                else:
                    return "2"
            else:
                return "1"
        elif email_type == "forget_password":
            if user_username is not None:
                users = client_users.find_one({"用户名": username})
                session["verification_forget"] = send_email(users["邮箱"], username)
                return "2"
            elif user_email is not None:
                users = client_users.find_one({"邮箱": email})
                session["verification_forget"] = send_email(email, users["用户名"])
                return "2"
            else:
                return "1"
        elif email_type == "change_password":
            users = client_users.find_one({"用户名": session["username"]})
            session["verification_change"] = send_email(users["邮箱"], session["username"])
            return "1"
        elif email_type == "change_email":
            if user_email is None:
                session["verification_change_email"] = send_email(email, session["username"])
                return "2"
            else:
                return "1"
    abort(404)
