import requests
from main_settings import directory, session

url = "https://zj.v.api.aa1.cn/api/zuoye"
headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70"
}

def get_Handwriting(msg):
    a = requests.get(url, headers=headers, params={"msg": msg})
    f = open(directory + "static/images/Handwriting/" + session["username"] + ".png", "wb")
    f.write(a.content)
    f.close()
    

