# encoding = utf-8

import requests
from retrying import retry


@retry(stop_max_attempt_number=5)
def get_music_dict(song_name):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept - encoding': 'gzip, deflate',
        'accept - language': 'zh - CN, zh;q = 0.9',
        'cache - control':'no - cache',
        'Connection': 'keep-alive',
        'csrf': 'HH3GHIQ0RYM',
        'Referer': 'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/99.0.4844.51 Safari/537.36',
        'Cookie': '_ga=GA1.2.218753071.1648798611; _gid=GA1.2.144187149.1648798611; _gat=1; '
                  'Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1648798611; '
                  'Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1648798611; kw_token=HH3GHIQ0RYM'
    }
    search_url = "http://www.kuwo.cn/api/www/search/searchMusicBykeyWord"
    search_data = {
        'key': song_name,
        'pn': '1',
        'rn': '80',
        'httpsStatus': '1',
        'reqId': '858597c1-b18e-11ec-83e4-9d53d2ff08ff'
    }
    num = 1
    song_dict = {}
    song_list = requests.get(search_url, params=search_data, headers=headers, timeout=20).json()
    songs_req_id = song_list["reqId"]
    if song_list["data"]["list"] == []:
        return None
    for item in song_list["data"]["list"]:
        try:
            song = dict({})
            song_rid = item["rid"]
            music_url = 'http://www.kuwo.cn/api/v1/www/music/playUrl?mid={}&type=convert_url3' \
                        '&httpsStatus=1&reqId={}'\
                        .format(song_rid, songs_req_id)
            song["music_name"] = item["name"]
            song["music_artist"] = item["artist"]
            song["music_album"] = item["album"]
            song["music_picUrl"] = item["pic"]
            song["music_id"] = song_rid
            song["music_url"] = music_url
            song_dict[str(num)] = song
            num += 1
        except:
            continue
    return song_dict


def get_music_url(music_url):
    try:
        response_data = requests.get(music_url).json()
        return response_data["data"]["url"]
    except:
        return None