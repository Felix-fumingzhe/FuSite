# encoding = utf-8

from wordcloud import WordCloud
import numpy as np
from PIL import Image
import jieba
import re
from flask import session
from main_settings import directory


def cloud(text, img=None):
    if img is not None:
        image1 = Image.open(directory+f"static/images/WordCloud/{session['username']}_img.png")
        MASK = np.array(image1)
        WC = WordCloud(font_path = directory+"static/fonts/simfang.ttf",max_words=2000, height= 400, width=400,mask = MASK, background_color='white', repeat=False,mode='RGBA')
        st1 = re.sub('[，。、“”‘ ’]','',str(text))
        conten = ' '.join(jieba.lcut(st1))
        con = WC.generate(conten)
        con.to_file(directory+f"static/images/WordCloud/{session['username']}.png")
    else:
        WC = WordCloud(font_path = directory+"static/fonts/simfang.ttf",max_words=2000, height= 400, width=400, background_color='white',repeat=False,mode='RGBA')
        st1 = re.sub('[，。、“”‘ ’]','',str(text))
        conten = ' '.join(jieba.lcut(st1))
        con = WC.generate(conten)
        con.to_file(directory+f"static/images/WordCloud/{session['username']}.png")
