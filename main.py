import logging
from os import access
import config
import json
import requests
import pyowm
import wikipedia
import gspread

from googlesearch import search
from bs4 import BeautifulSoup as BS
from aiogram import Bot, Dispatcher, executor, types

try:
    logging.basicConfig(level=logging.INFO)

    wikipedia.set_lang("uk")
    gc = gspread.service_account(filename="credentials.json")
    sh = gc.open_by_key("1ddyrobtVFD0rk8WMOEMJ_nVk0rLSNN3fZo1twlLL-kM")
    data1 = sh.sheet1
    access_с = [1835953916, 1009661353]

    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(bot)
    def read():
        with open("data.json", "r", encoding='utf8') as file:
            return json.load(file)
    def write(dict1):
        with open("data.json", "w", encoding='utf8') as file:
            return json.dump(dict1, file, indent=4, ensure_ascii=False)
    def Uinfo(msg : types.Message):
        d = read()
        n = 1
        if str(msg.from_user.id) in d["User_Input_Info"].keys(): n = d["User_Input_Info"][str(msg.from_user.id)][0] + 1
        d["User_Input_Info"][str(msg.from_user.id)] = [n,msg.text, msg.from_user.full_name]
        write(d)
        del d, n

except Exception as E:
    print(f"[Error] {E}")

def get_news():
    headers = {
        "User-agent" : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 OPR/77.0.4054.298"    
    }
    url = "https://dubnopk.com.ua/index.php/news/"
    r = requests.get(url=url, headers=headers)
    try:
        soup = BS(r.text, "lxml")
        news = soup.find_all("div", class_="art-box-body")
        for article in news:
            title = article.find("span", class_="art-postheadericon").text.strip()
            #desc = article.find("span").text.strip()
            return title
    except Exception as E:
        return f"[ ! ] помилка - {E}"
def memes_google():
    headers = {
        "User-agent" : "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 OPR/77.0.4054.298"    
    }
    url = "https://www.google.com/search?q=%D0%BC%D0%B5%D0%BC%D1%8B+%D0%BF%D1%80%D0%BE+%D0%BA%D0%BE%D0%BB%D0%BB%D0%B5%D0%B4%D0%B6+%D0%B8+%D1%83%D0%BD%D0%B8%D0%B2%D0%B5%D1%80%D1%8B&client=firefox-b-d&biw=899&bih=497&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiAz97t9pz1AhWHmIsKHaUKBh4Q_AUoAXoECAEQAw"
    r = requests.get(url=url, headers=headers)
    try:
        soup = BS(r.text, "lxml")
        mems = soup.find_all("img", class_="rg_i Q4LuWd")
        for meme in mems:
            return meme["src"]
    except Exception as E:
        return f"[ ! ] помилка - {E}"

@dp.message_handler(commands=["wiki", "wikipedia"])
async def wiki(title = types.Message):
    Uinfo(title)
    try:
        search = wikipedia.search(title.get_args(), results=1)
        result = wikipedia.page(search)
        await title.answer(f"{result.title}\n_______________\n{wikipedia.summary(search, sentences=9)}\n_______________\n{result.url}")
    except wikipedia.exceptions.WikipediaException:
        await title.answer("Введіть аргумент пошуку\nнаприклад : /wiki [запрос]")
    except Exception as a:
        await title.answer(f"[ ! ] помилка : {a}")
        del a
    del search, result

@dp.message_handler(commands=['help'])
async def info(msg : types.Message):
    Uinfo(msg)
    await msg.answer("""Вот список доптупних Команд для усіх : 
/temp - Температура в м.Дубно(та не тільки)
/news - Крайні новини з сайту Коледжу https://dubnopk.com.ua/index.php/news
/wiki - пошук інформації у Wikipedia
/search - пошук інформації в GOOGLE
_________________________________
/schedulemon- розклад Пар на Понеділок
/scheduletue - розклад Пар на Вівторок
/schedulewed - розклад Пар на Середу
/schedulethu - розклад Пар на Четвер
/schedulefri - розклад Пар на П'ятницю
/callschedule - розклад дзвінків
Інші команди доступні тільки для Старости)))
""")

@dp.message_handler(commands=['SetInfo'])
async def SetInfo(args : types.Message):
    Uinfo(args)
    if args.from_user.id not in access_с:
        await args.answer("У вас немає доступу до Команди")
        return

    a = args.get_args().split("\n")
    if len(a) != 9:
        await args.answer("Потрібно 9 аргументів")
        return
    if a[0] in data1.col_values(1):
        ind = data1.col_values(1).index(a[0]) + 1
        data1.update(f"A{ind}:I{ind}", [a])
        del ind
        return
    data1.append_row(a)

@dp.message_handler(commands=['GetInfo'])
async def Getinfo(args : types.Message):
    if args.from_user.id not in access_с:
        await args.answer("У вас немає доступу до Команди")
        return

    arr = data1.col_values(1)
    a = data1.get_all_records()
    if args.get_args() not in arr:
        await args.answer("Призвіще не Знайдено")
        return
    d = a[arr.index(args.get_args()) - 1]
    answer = ""
    for key, value in d.items():
        answer += f"{key} - {value}\n"
    await args.answer(answer)
    Uinfo(args)

@dp.message_handler(commands=['GetAllInfo'])
async def GetAllInfo(args : types.Message):
    Uinfo(args)
    if args.from_user.id not in access_с:
        await args.answer("У вас немає доступу до Команди")
        return

    ls = data1.get_all_records()
    for i in ls:
        answer = ""
        for key, value in i.items():
            answer += f"{key} - {value}\n"
        await args.answer(answer)
        del answer

@dp.message_handler(commands=['search', 's'])
async def Google_Shearch(args : types.Message):
    Uinfo(args)
    if args.get_args() == "":
        await args.answer("Введіть аргумент пошуку\nнаприклад : /search [запрос]")
        return
    try:
        for url in search(args.get_args(), lang='uk', num_results=5):
            await args.answer(url)
    except Exception as E:
        await args.answer(f"[ ! ] помилка - {E}")
    
@dp.message_handler(commands=["scheduleMon", "scheduleTue", "scheduleWed", "scheduleThu", "scheduleFri"])
async def Schedule(msgs : types.Message):
    msg = msgs.text.split('@')[0]
    arg = msg[-3] + msg[-2] + msg[-1]
    answer = f"______|{arg.upper()}|______\n"
    lst = list(read()["Days"][arg].keys())
    for i in range(len(lst)):
        answer += f"{i + 1} - {lst[i]}\n"
    answer += "_________________"
    await msgs.answer(answer)
    Uinfo(msgs)
    del msg, arg, answer, lst
@dp.message_handler(commands = ["callschedule"])
async def LssTimes(msgs : types.message):
    answer = ""
    bd = read()["CallSchedule"]
    for i in bd.keys():
        answer += f"____|{i.upper()}|____\n"
        for t in range(len(bd[i])):
            answer += f"{str(t + 1)} - {bd[i][str(t+1)]}\n"
        answer += "________________\n\n"
    await msgs.answer(answer)

@dp.message_handler(commands=["news"])
async def news(message : types.Message):
    await message.answer(f"НОВИНИ  :\n{get_news()}\n - https://dubnopk.com.ua/index.php/news")
    Uinfo(message)

@dp.message_handler(commands=["temp"])
async def weather(message : types.Message):
    city = "Дубно"
    if len(message.get_args()) >= 2:
        city = message.get_args()
    try:
        owm = pyowm.OWM(config.wApiKey)
        w = owm.weather_manager().weather_at_place(city)
        myWeather = w.weather
        temp = myWeather.temperature('celsius')["temp"]
    except Exception as E:
        await message.answer(f"[ ! ] помилка - {E}")
        return

    await message.answer(f"Температура в м.{city} - {str(temp)}°")
    Uinfo(message)
    del owm, w, myWeather, city, temp

@dp.message_handler(commands=["memes"])
async def memes(message : types.Message):
    await message.answer(memes_google())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)