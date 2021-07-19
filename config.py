from datetime import datetime
from pytz import timezone

TOKEN = '1861177956:AAGfxYGzvOlw4Fxwi4S6P_GOns-R_YwUFvA'
URL = 'https://qr-code-telegram-bot.herokuapp.com/'
URI = 'mongodb+srv://H_reugo:Nurmukhambetov@cluster0.vq2an.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
MAX_BALANCE = 20000

cashback = [0.06, 0.11]
def cashback_logic(sum):
    res = 0
    if sum >= 5000: res = cashback[1]
    elif sum >= 3000: res = cashback[0]
    return res

def create_operation(cdate, ctime, text, sum, cashback = -1):
	return {'date': cdate, 'time': ctime, 'details': text, 'sum': sum, 'cashback': cashback}

def get_today():
    local_now = datetime.now(timezone('Asia/Almaty'))
    return local_now
