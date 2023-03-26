# encoding = utf-8

from flask import Blueprint, request, render_template, redirect, session
from main_settings import client_blog, PAGE
import math
import datetime


blog_app = Blueprint("blog", __name__)


@blog_app.route("/blog")
@blog_app.route("/blog/index")
def blog_index():
    blogs = list(client_blog.find().sort("上传日期"))
    classification_list = {}
    classification_list_all = [blog["上传日期"].strftime("%Y年%m月") for blog in list(client_blog.find().sort("上传日期", -1))]
    for i in classification_list_all:
        if i not in classification_list:
            classification_list[i] = (int(i.split("年")[0]), int(i.split("年")[1].split("月")[0]))
    page = request.args.get("page")
    if page is None:
        page = 1
    else:
        try:
            if int(page) > math.ceil(len(blogs)/PAGE):
                page = 1
            else:
                page = int(page)
        except:
            page = 1
    blogs = {i: blogs[i*PAGE-PAGE:i*PAGE] for i in range(1, math.ceil(len(blogs)/PAGE)+1)}
    context = {
        "username": session["username"],
        "blogs": blogs,
        "new_blogs": {blog["标题"]: blog["文章id"] for blog in list(client_blog.find().sort("修改日期", -1))[:4]},
        "hot_blogs": {blog["标题"]: blog["文章id"] for blog in list(client_blog.find({"是否热门": "是"}))},
        "classification_list": classification_list,
        "page": page,
        "pages": len(blogs)
    }
    return render_template("blog/index.html", **context)


@blog_app.route("/blogs/<blog_id>")
def blogs(blog_id):
    blog = client_blog.find_one({"文章id": blog_id})
    if blog is not None:
        blog["浏览量"] = str(int(blog["浏览量"])+1)
        client_blog.update_one({"文章id": blog_id}, {"$set": blog})
        blog = client_blog.find_one({"文章id": blog_id})
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
            prev_blog = blogs[index-1]
            next_blog = blogs[index+1]
        classification_list = {}
        classification_list_all = [blog["上传日期"].strftime("%Y年%m月") for blog in
                                    list(client_blog.find().sort("上传日期", -1))]
        for i in classification_list_all:
            if i not in classification_list:
                classification_list[i] = (int(i.split("年")[0]), int(i.split("年")[1].split("月")[0]))
        context = {
            "username": session["username"],
            "blog": blog,
            "new_blogs": {blog["标题"]: blog["文章id"] for blog in list(client_blog.find().sort("修改日期", -1))[:4]},
            "hot_blogs": {blog["标题"]: blog["文章id"] for blog in list(client_blog.find({"是否热门": "是"}))},
            "prev_blog": prev_blog,
            "next_blog": next_blog,
            "classification_list": classification_list
        }
        return render_template("blog/blog.html", **context)
    else:
        return redirect("/blog/index")


@blog_app.route("/blog_classification/<int:year>/<int:month>")
def blog_classification(year, month):
    if month <= 0 or month >= 13:
        return redirect("/blog/index")
    next_year = year
    next_month = month+1
    if month == 12:
        next_year += 1
        next_month = 1
    classification_list = {}
    classification_list_all = [blog["上传日期"].strftime("%Y年%m月") for blog in
                                list(client_blog.find().sort("上传日期", -1))]
    for i in classification_list_all:
        if i not in classification_list:
            classification_list[i] = (int(i.split("年")[0]), int(i.split("年")[1].split("月")[0]))
    blogs = list(client_blog.find({"上传日期": {"$gte": datetime.datetime(year, month, 1),
                                            "$lte": datetime.datetime(next_year, next_month, 1)}}))
    page = request.args.get("page")
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
    all_len = len(blogs)
    blogs = {i: blogs[i * PAGE - PAGE:i * PAGE] for i in range(1, math.ceil(len(blogs) / PAGE) + 1)}
    context = {
        "username": session["username"],
        "blogs": blogs,
        "new_blogs": {blog["标题"]: blog["文章id"] for blog in list(client_blog.find().sort("修改日期", -1))[:4]},
        "hot_blogs": {blog["标题"]: blog["文章id"] for blog in list(client_blog.find({"是否热门": "是"}))},
        "classification_list": classification_list,
        "year": year,
        "month": month,
        "all": all_len,
        "page": page,
        "pages": len(blogs)
    }
    return render_template("blog/classification.html", **context)


@blog_app.route("/blog/search")
def blog_search():
    keyword = request.args.get("keyword")
    page = request.args.get("page")
    if keyword is None:
        return redirect("/blog/index")
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
    classification_list = {}
    classification_list_all = [blog["上传日期"].strftime("%Y年%m月") for blog in
                                list(client_blog.find().sort("上传日期", -1))]
    for i in classification_list_all:
        if i not in classification_list:
            classification_list[i] = (int(i.split("年")[0]), int(i.split("年")[1].split("月")[0]))
    context = {
        "username": session["username"],
        "blogs": blogs,
        "new_blogs": {blog["标题"]: blog["文章id"] for blog in list(client_blog.find().sort("修改日期", -1))[:4]},
        "hot_blogs": {blog["标题"]: blog["文章id"] for blog in list(client_blog.find({"是否热门": "是"}))},
        "classification_list": classification_list,
        "keyword": keyword,
        "page": page,
        "pages": len(blogs),
        "all": all_len,
    }
    return render_template("/blog/search.html", **context)
