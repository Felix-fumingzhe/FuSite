import requests


def translate(_from,to,text):
    if text == "":
        return ""
    languageDict = {'自动检测':0,'中文':1,'英文':2,'日文':3,'韩文':4,'法文':5,'西班牙文':6,'葡萄牙文':7,'德文':8,'意大利文':9,'俄文':10}
    data = {
        "text":text,
        "from":languageDict[_from],
        "to":languageDict[to]
    }
    r = requests.post('https://www.yuanfudao.com/ada-student-app-api/api/translate',data=data).json()
    return r["result"]

