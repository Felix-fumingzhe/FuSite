from requests import post

def ai_draw(text, size):
    try:
        data = {
            "text": text,
            "size": size
        }
        response = post("http://fumingzhe.pythonanywhere.com/ai_draw", data=data).text
        return response
    except:
        return None
