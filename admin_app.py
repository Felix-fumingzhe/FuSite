# encoding = utf-8

from flask import Blueprint, render_template, request, redirect, session, abort, jsonify
from main_settings import init_session, client_users, client_blog, client_music, PAGE, directory, get_now_music
import eyed3
import datetime
import hashlib
import random
import math
import os


admin_app = Blueprint("admin", __name__)

@admin_app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    init_session()
    if request.method == "POST":
        username_Or_email = request.form.get("username_Or_email")
        password = request.form.get("password")
        users_username = client_users.find_one({"用户名": username_Or_email})
        users_email = client_users.find_one({"邮箱": username_Or_email})
        context = {
            "username_Or_email": username_Or_email,
            "password": password,
            "admin_login_text": ""
        }
        if users_username is None and users_email is None:
            context["error"] = "用户名或邮箱不存在"
            return render_template("admin/login.html", **context)
        else:
            if users_username is not None:
                users = users_username
            else:
                users = users_email
        if hashlib.sha256(password.encode("utf-8")).hexdigest() != users["密码"]:
            context["error"] = "密码错误"
            return render_template("admin/login.html", **context)
        if users["权限"] != 3:
            context["error"] = "您不是管理员"
            return render_template("admin/login.html", **context)
        else:
            session["admin_login"] = "admin_login"
            session["admin_name"] = users["用户名"]
            session["admin_text"] = "欢迎管理员"+session["admin_name"]+"登录"
            return redirect("/admin/index")
    context = {
        "admin_login_text": ""
    }
    if session.get("admin_login_text") is not None:
        context["admin_login_text"] = session["admin_login_text"]
        session.pop("admin_login_text")
    elif session.get("username") is not None:
        if client_users.find_one({"用户名": session["username"]})["权限"] == 3:
            context["username"] = session["username"]
            context["qx"] = "1"
    return render_template("admin/login.html", **context)


@admin_app.route("/admin/login_out")
def login_out():
    session["admin_login_text"] = "管理员"+session["admin_name"]+"/n您已退出登录"
    session["admin_login"] = "not_admin_login"
    session.pop("admin_name")
    return redirect("/admin/login")


@admin_app.route("/admin")
@admin_app.route("/admin/index", methods=["GET", "POST"])
def admin_index():
    context = {
        "users": list(client_users.find())
    }
    if request.method == "POST":
        if request.form.get("type") == "search":
            search_content = request.form.get("search_content")
            context["users"] = list(client_users.find({"用户名": {"$regex": search_content, "$options": "$i"}}))
            context["search_content"] = search_content
            return render_template("admin/index.html", **context)
        else:
            new_users = []
            for user in list(client_users.find()):
                qx = request.form.get(user["用户名"]+"_qx")
                if qx is not None:
                    user["权限"] = int(qx)
                    new_users.append(user)
                    client_users.update_one({"用户名": user["用户名"]}, {"$set": user})
                else:
                    new_users.append(user)
            context["users"] = new_users
            context["admin_text"] = "用户权限修改成功"
            return render_template("admin/index.html", **context)
    if session.get("admin_text") is None:
        return render_template("admin/index.html", **context)
    else:
        context["admin_text"] = session["admin_text"]
        session.pop("admin_text")
        return render_template("admin/index.html", **context)


@admin_app.route("/admin_users/<username>")
def admin_users(username):
    user = client_users.find_one({"用户名": username})
    if user is not None:
        if user["个人主页"].isspace() or user["个人主页"] == "":
            user["个人主页"] = None
        context = {
            "user": user
        }
        return render_template("admin/user.html", **context)
    else:
        abort(404)


@admin_app.route("/admin/blog")
def admin_blog():
    blogs = list(client_blog.find().sort("上传日期"))
    page = request.args.get("page")
    all_len = len(blogs)
    if page is None:
        page = 1
    else:
        try:
            if int(page) > math.ceil(len(blogs) / PAGE):
                page = 1
            else:
                page = int(page)
        except:
            page = 1
    blogs = {i: blogs[i * PAGE - PAGE:i * PAGE] for i in range(1, math.ceil(len(blogs) / PAGE) + 1)}
    context = {
        "blogs": blogs,
        "page": page,
        "pages": len(blogs),
        "all": all_len
    }
    if session.get("admin_blog_text") is not None:
        context["admin_text"] = session["admin_blog_text"]
        session.pop("admin_blog_text")
    return render_template("/admin/blogs.html", **context)


@admin_app.route("/admin/add_blog",methods=["GET","POST"])
def admin_add_blog():
    if request.method == "POST":
        title = request.form.get("bt")
        ms = request.form.get("ms")
        content = request.form.get("content")
        if request.form.get("rm") == "是":
            rm = "是"
        else:
            rm = "否"
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
            "标题": title,
            "描述": ms,
            "作者": session["admin_name"],
            "文章内容": content,
            "浏览量": "0",
            "是否热门": rm,
            "上传日期": now,
            "修改日期": now,
            "文章id": word_id
        })
        session["admin_"] = "文章添加成功"
        return redirect("/admin/blog")
    return render_template("admin/add_blog.html")


@admin_app.route("/admin_blog/<word_id>",methods=["GET","POST"])
def admin_word_id(word_id):
    blog = client_blog.find_one({"文章id":word_id})
    if blog is not None:
        if request.method == "POST":
            if request.form.get("rm") == "是":
                blog["是否热门"] = "是"
            else:
                blog["是否热门"] = "否"
            client_blog.update_one({"文章id": word_id}, {"$set": blog})
        if request.args.get("delete") is not None:
            client_blog.delete_one({"文章id":word_id})
            session["admin_blog_text"] = "文章删除成功"
            return redirect("/admin/blog")
        blogs = list(client_blog.find().sort("上传日期"))
        index = blogs.index(blog)
        if len(blogs) == 1:
            prev_blog = None
            next_blog = None
        elif index == 0:
            prev_blog = None
            next_blog = blogs[1]
        elif index == (len(blogs) - 1):
            prev_blog = blogs[-2]
            next_blog = None
        else:
            prev_blog = blogs[index - 1]
            next_blog = blogs[index + 1]
        context = {
            "blog": blog,
            "prev_blog": prev_blog,
            "next_blog": next_blog,
        }
        return render_template("admin/blog.html", **context)
    else:
        return redirect("/admin/blog")


@admin_app.route("/admin_blog/search")
def admin_blog_search():
    keyword = request.args.get("keyword")
    page = request.args.get("page")
    if keyword is None:
        return redirect("/admin/blog")
    blogs = list(client_blog.find({"$or": [{"标题": {"$regex": keyword, "$options": "$i"}}, {"描述": {"$regex": keyword, "$options": "$i"}}]}).sort("上传日期"))
    all_len = len(blogs)
    if page is None:
        page = 1
    else:
        try:
            if int(page) > (len(blogs) // PAGE):
                page = 1
            else:
                page = int(page)
        except:
            page = 1
    blogs = {i: blogs[i * PAGE - PAGE:i * PAGE] for i in range(1, math.ceil(len(blogs) / PAGE) + 1)}
    context = {
        "blogs": blogs,
        "keyword": keyword,
        "page": page,
        "pages": len(blogs),
        "all": all_len,
    }
    return render_template("/admin/blog_search.html", **context)


@admin_app.route("/admin_blog/editor", methods=["GET","POST"])
def admin_blog_editor():
    if request.method == "POST":
        word_id = request.form.get("word_id")
        blog = client_blog.find_one({"文章id":word_id})
        if blog is not None:
            blog["标题"] = request.form.get("bt")
            blog["描述"] = request.form.get("ms")
            blog["文章内容"] = request.form.get("content")
            if request.form.get("rm") == "是":
                blog["是否热门"] = "是"
            else:
                blog["是否热门"] = "否"
            blog["修改日期"] = datetime.datetime.now()
            client_blog.update_one({"文章id":word_id},{"$set":blog})
            session["admin_blog_text"] = "文章修改成功"
            return redirect("/admin/blog")
        else:
            return redirect("/admin/blog")
    blog = client_blog.find_one({"文章id":request.args.get("word_id")})
    if blog is not None:
        context = {
            "blog": blog
        }
        return render_template("admin/editor_blog.html", **context)
    else:
        return redirect("/admin/blog")


@admin_app.route("/admin/music")
def admin_music():
    music = list(client_music.find())
    if music != []:
        music = music[0]
        music.pop("_id")
    content = {
        "music": music
    }
    remove_id = request.args.get("remove")
    if remove_id is not None:
        try:
            if int(remove_id) <= len(music) and int(remove_id) >= 1:
                os.remove(f"{directory}static/music/{music[remove_id]['music_name']}.mp3")
                music_jpg = music[remove_id]['music_name'].replace(" ", "_")
                os.remove(f"{directory}static/music/img/{music_jpg}.jpg")
                client_music.drop()
                music_dict = get_now_music()
                if music_dict != {}:
                    client_music.insert_one(music_dict)
                return redirect("/admin/music")
        except:
            pass
    return render_template("admin/music.html", **content)


@admin_app.route("/admin/add_music", methods=["GET", "POST"])
def add_music():
    if request.method == "POST":
        name = request.form.get("name")
        music_artist = request.form.get("music_artist")
        music_album = request.form.get("music_album")
        file_music = request.files.get("music")
        file_img = request.files.get("img")
        img_name = name.replace(" ", "_")
        file_music.save(f"{directory}static/music/{name}.mp3")
        file_img.save(f"{directory}static/music/img/{img_name}.jpg")
        music = eyed3.load(f"{directory}static/music/{name}.mp3")
        music.initTag()
        music.tag.title = u"".join(name)
        music.tag.artist = u"".join(music_artist)
        music.tag.album = u"".join(music_album)
        music.tag.save()
        client_music.drop()
        client_music.insert_one(get_now_music())
        return redirect("/admin/music")


@admin_app.route("/upload_admin_images", methods=["POST"])
def upload_admin_images():
    users_image_dir = directory+"static/images/users/{username}".format(username=session["admin_name"])
    if os.path.exists(users_image_dir) is False:
        os.mkdir(users_image_dir)
    file = request.files.get("file")
    file_name = "{}.png".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    file.save(users_image_dir+"/{}".format(file_name))
    return jsonify({"location": "/static/images/users/{username}/{file}".
                    format(username=session["admin_name"], file=file_name)})
