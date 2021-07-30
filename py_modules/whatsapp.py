import threading
import requests

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def check_whatsapp():
    try:
        if(requests.get("https://whatsapp-web-potato.herokuapp.com/qrfound", timeout=3).text != "true"):
            requests.get("https://api.telegram.org/bot1102080505:AAGsEigzYhCOrrllbOrk42hJYpKAVlbrA0E/sendMessage?chat_id=256721170&text=whatsappfailed")
        else:
            requests.get("https://api.telegram.org/bot1102080505:AAGsEigzYhCOrrllbOrk42hJYpKAVlbrA0E/sendMessage?chat_id=256721170&text=whatsappok")
    except:
        requests.get("https://api.telegram.org/bot1102080505:AAGsEigzYhCOrrllbOrk42hJYpKAVlbrA0E/sendMessage?chat_id=256721170&text=whatsappfailed")

check_whatsapp()
set_interval(check_whatsapp, 10 * 60)