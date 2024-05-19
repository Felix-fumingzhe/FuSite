# encoding = utf-8

from flask import Blueprint, request, render_template, session, abort, jsonify
from main_settings import client_music
from tools import get_music_dict


music_app = Blueprint("music", __name__)

@music_app.route("/music")
@music_app.route("/music/index")
def music_index():
    music_list = list(client_music.find())
    if music_list != []:
        music_list = list(client_music.find())[0]
    context = {
        "username": session["username"],
        "music": music_list
    }
    return render_template("music/index.html", **context)


@music_app.route("/music/get_music")
def get_music():
    music_name = request.args.get("music_name")
    if music_name is not None:
        music = get_music_dict(music_name)
        context = {
            "username": session["username"],
            "music_name": music_name,
            "music": music
        }
        return render_template("music/get_music.html", **context)
    else:
        abort(404)
