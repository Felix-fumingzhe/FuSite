from main_settings import client_date
from datetime import datetime
from zhdate import ZhDate


def date(id):
    print(id)
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date = client_date.find_one({"id": "main"})
    f_gong = date["date"]["f_gong"]
    f_nong = date["date"]["f_nong"]
    f_week = date["date"]["f_week"]
    user_date  = client_date.find_one({"id": id})
    if user_date is None:
        client_date.insert_one({"id": id, "date": {"b_gong": {}, "b_nong": {}}})
    date = client_date.find_one({"id": id})
    b_gong = date["date"]["b_gong"]
    b_nong = date["date"]["b_nong"]
    data_nongli = f_nong
    data_nongli.update(b_nong)
    data_gong = f_gong
    data_gong.update(b_gong)
    data_week = f_week
    data_all = []
    today = datetime.now()
    today = datetime(today.year, today.month, today.day)
    year_nongli = int(str(ZhDate.today()).split("农历")[1].split("年")[0])
    year_gong = datetime.now().year

    def month_week(name, month, week):
        for a in range(2):
            day = 0
            num = 0
            while True:
                day += 1
                data = datetime(year_gong+a, month, day)
                if data.weekday() == week[1]:
                    num += 1
                    if num == week[0]:
                        if today > data:
                            break
                        else:
                            return {"name": name, "gong": "公历"+data.strftime("%Y年%m月%d日"), "nong": str(ZhDate.from_datetime(data)), "distance": (data-today).days, "week": week_list[week[1]]}

    for i in data_nongli:
        data = data_nongli[i]
        if i == "除夕":
            data1 = data[1]
            while True:
                try:
                    data_to_gong = ZhDate(year_nongli, data[0], data1).to_datetime()
                    break
                except:
                    data1 -= 1
        else:
            data_to_gong = ZhDate(year_nongli, data[0], data[1]).to_datetime()
        if today > data_to_gong:
            data_to_gong = ZhDate(
                year_nongli+1, data[0], data[1]).to_datetime()
            data_all.append({"name": i, "gong": "公历"+data_to_gong.strftime("%Y年%m月%d日"), "nong": str(ZhDate.from_datetime(
                data_to_gong)), "distance": (data_to_gong - today).days, "week": week_list[data_to_gong.weekday()]})
        else:
            data_all.append({"name": i, "gong": "公历"+data_to_gong.strftime("%Y年%m月%d日"), "nong": str(ZhDate.from_datetime(
                data_to_gong)), "distance": (data_to_gong - today).days, "week": week_list[data_to_gong.weekday()]})
    for i in data_gong:
        data = data_gong[i]
        data_to_gong = datetime(year_gong, data[0], data[1], 0, 0)
        if today > data_to_gong:
            data_to_gong = datetime(year_gong+1, data[0], data[1], 0, 0)
            data_all.append({"name": i, "gong": "公历"+data_to_gong.strftime("%Y年%m月%d日"), "nong": str(ZhDate.from_datetime(
                data_to_gong)), "distance": (data_to_gong - today).days, "week": week_list[data_to_gong.weekday()]})
        else:
            data_all.append({"name": i, "gong": "公历"+data_to_gong.strftime("%Y年%m月%d日"), "nong": str(ZhDate.from_datetime(
                data_to_gong)), "distance": (data_to_gong - today).days, "week": week_list[data_to_gong.weekday()]})
    for i in data_week:
        data_all.append(month_week(i, data_week[i][0], data_week[i][1]))
    data_all.sort(key=lambda dictionary: dictionary['distance'])
    name_list = []
    for i in b_gong:
        name_list.append(i)
    for i in b_nong:
        name_list.append(i)
    for i in range(len(data_all)):
        if data_all[i]["name"] in name_list:
            data_all[i]["delete"] = True
        else:
            data_all[i]["delete"] = False
    return data_all
