# encoding = utf-8

import requests
import json
import re
import hashlib
import os
import time
from jsonpath import jsonpath


MID = "0376045b610cd30487f66855d296194b"
UUID = "0376045b610cd30487f66855d296194b"
DFID = "34cTSp3R2RvO1lnyUh353ByL"
TOKEN = "2e145f0776574048ee733b73e0f5644e175dd8ba6cd97f85c3e3cb3b0e3f5d1e"
USERID = 954283296
SEARCH_PAGE_SIZE = 10
T = round(time.time() * 1000)



def md5_hash(string):
    # 创建一个md5对象
    md5 = hashlib.md5()
    # 将字符串转换为字节流并进行MD5加密
    md5.update(string.encode('utf-8'))
    # 获取加密后的十六进制结果
    encrypted_string = md5.hexdigest()
    return encrypted_string


class Audio:
    def __init__(self, id):
        self.id = id
        self.info_url = 'https://wwwapi.kugou.com/play/songinfo'

    def audio(self):
        params = {
            "srcappid": 2919,
            "clientver": 20000,
            f"clienttime": T,
            "mid": MID,
            "uuid": UUID,
            "dfid": DFID,
            "appid": 1014,
            "platid": 4,
            "encode_album_audio_id": self.id,
            "token": TOKEN,
            "userid": USERID,
            "signature": self._signature(),
        }

        resp = requests.get(url=self.info_url, params=params)
        url = resp.json()['data']['play_url']
        img = resp.json()['data']['img']
        lyrics = resp.json()['data']['lyrics']
        return (url, img, lyrics)

    def _signature(self):
        """
        解密 signature 参数
        这些参数，params中都有，初步猜测，请求提交到服务器时，
        会按顺序排列 params 中的参数为下面 p 的形状，
        用 md5 加密后再与 params 中的 signature 做对比
        """
        p = [
            "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt",
            "appid=1014",  #
            f"clienttime={T}",
            "clientver=20000",  #
            f"dfid={DFID}",
            f"encode_album_audio_id={self.id}",
            f"mid={MID}",
            "platid=4",  #
            "srcappid=2919",  #
            f"token={TOKEN}",
            f"userid={USERID}",
            f"uuid={UUID}",
            "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
        ]

        signature = md5_hash(''.join(p))
        return signature


class Search:

    def __init__(self, keyword):
        self.url = 'https://complexsearch.kugou.com/v2/search/song'
        self.keyword = keyword
        self.page_size = SEARCH_PAGE_SIZE

    def get_info(self):
        params = {
            "callback": "callback123",
            "srcappid": 2919,
            "clientver": 1000,
            "clienttime": T,
            "mid": MID,
            "uuid": UUID,
            "dfid": DFID,
            "keyword": self.keyword,
            "page": 1,
            "pagesize": self.page_size,
            "bitrate": 0,
            "isfuzzy": 0,
            "inputtype": 0,
            "platform": "WebFilter",
            "userid": USERID,
            "iscorrection": 1,
            "privilege_filter": 0,
            "filter": 10,
            "token": TOKEN,
            "appid": 1014,
            "signature": self._signature(),
        }
        r = requests.get(url=self.url, params=params).text
        pattern = re.compile('^callback123\((.*?)\)$')
        json_info = json.loads(pattern.findall(r)[0])
        id = jsonpath(json_info, '$..EMixSongID')
        singer_names = jsonpath(json_info, '$..SingerName')
        song_names = jsonpath(json_info, '$..SongName')
        album_names = jsonpath(json_info, '$..AlbumName')
        return zip(id, singer_names, song_names, album_names)

    def _signature(self):
        p = [
            "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt",
            "appid=1014",
            "bitrate=0",
            "callback=callback123",
            f"clienttime={T}",
            "clientver=1000",
            f"dfid={DFID}",
            "filter=10",
            "inputtype=0",
            "iscorrection=1",
            "isfuzzy=0",
            f"keyword={self.keyword}",
            f"mid={MID}",
            "page=1",
            f"pagesize={self.page_size}",
            "platform=WebFilter",
            "privilege_filter=0",
            "srcappid=2919",
            f"token={TOKEN}",
            f"userid={USERID}",
            f"uuid={UUID}",
            "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
        ]
        signature = md5_hash(''.join(p))
        return signature

def is_string_digit(s):
    """检查字符串是不是数字"""
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_music_dict(song_name):
    num = 1
    song_dict = {}
    for index, info in enumerate(Search(song_name).get_info()):
        try:
            song = {}
            info2 = Audio(info[0]).audio()
            song["music_name"] = info[2]
            song["music_artist"] = info[1]
            song["music_album"] = info[3]
            song["music_picUrl"] = info2[1]
            song["music_url"] = info2[0]
            song["music_lyrics"] = info2[2]
            song_dict[str(num)] = song
            if num == SEARCH_PAGE_SIZE:
                break
            num += 1
        except:
            continue
    return song_dict
