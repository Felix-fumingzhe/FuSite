# encoding = utf-8

import ybc_face
from main_settings import directory
from flask import session


def face_info(img_name):
    face = ybc_face.info_all(directory+f"static/images/Face/{img_name}.png")
    return face.split("\r\n")

