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

logging.basicConfig(level=logging.INFO)

wikipedia.set_lang("uk")
gc = gspread.service_account(filename="credentials.json")
sh = gc.open_by_key("1ddyrobtVFD0rk8WMOEMJ_nVk0rLSNN3fZo1twlLL-kM")
data1 = sh.sheet1
access_с = [1835953916, 1009661353]

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

with open("data.json", "r", encoding='utf8') as file:
    data = json.load(file)

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

@dp.message_handler(commands=["wiki", "wikipedia"])
async def wiki(title = types.Message):
    try:
        search = wikipedia.search(title.get_args(), results=1)
        result = wikipedia.page(search)
        await title.answer(f"{result.title}\n_______________\n{wikipedia.summary(search, sentences=9)}\n_______________\n{result.url}")
    except wikipedia.exceptions.WikipediaException:
        await title.answer("Введіть аргумент пошуку\nнаприклад    :     /wiki [запрос]")
    except Exception as a:
        await title.answer(f"[ ! ] помилка : {a}")

@dp.message_handler(commands=['help'])
async def info(msg : types.Message):
    await msg.answer("""Вот список доптупних Команд для усіх : 
/temp - Температура в м.Дубно
/news - Крайні новини з сайту Коледжу https://dubnopk.com.ua/index.php/news
/wiki - пошук інформації у Wikipedia
_________________________________
/schedulemon- розклад Пар на Понеділок
/scheduletue - розклад Пар на Вівторок
/schedulewed - розклад Пар на Середу
/schedulethu - розклад Пар на Четвер
/schedulefri - розклад Пар на П'ятницю

Інші команди доступні тільки для Старости)))
""")

@dp.message_handler(commands=['SetInfo'])
async def SetInfo(args : types.Message):
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

@dp.message_handler(commands=['GetAllInfo'])
async def GetAllInfo(args : types.Message):
    if args.from_user.id not in access_с:
        await args.answer("У вас немає доступу до Команди")
        return

    ls = data1.get_all_records()
    for i in ls:
        answer = ""
        for key, value in i.items():
            answer += f"{key} - {value}\n"
        await args.answer(answer)

@dp.message_handler(commands=['search'])
async def Google_Shearch(args : types.Message):
    for i in search(args.get_args(), tld="co.in", num=10, stop=10, pause=2):
         await args.answer(i)
    
@dp.message_handler(commands=["scheduleMon", "scheduleTue", "scheduleWed", "scheduleThu", "scheduleFri"])
async def Schedule(msgs : types.Message):
    msg = msgs.text.split('@')[0]
    arg = msg[-3] + msg[-2] + msg[-1]
    answer = f"______|{arg.upper()}|______\n"
    lst = list(data["Days"][arg].keys())
    for i in range(len(lst)):
        answer += f"{i + 1} - {lst[i]}\n"
    answer += "_________________"
    await msgs.answer(answer)

@dp.message_handler(commands=["news"])
async def news(message : types.Message):
    await message.answer(f"НОВИНИ  :\n{get_news()}\n - https://dubnopk.com.ua/index.php/news")

@dp.message_handler(commands=["temp"])
async def weather(message : types.Message):
    owm = pyowm.OWM(config.wApiKey)
    w = owm.weather_manager().weather_at_place("Дубно")
    myWeather = w.weather
    temp = myWeather.temperature('celsius')["temp"]

    await message.answer(f"Температура в м.Дубно - {str(temp)}°")
    if temp < 10:
        await message.answer("Бажано одягати куртку і штани)))")

@dp.message_handler()
async def badWord(message : types.Message):
    for word in data["BadWords"]:
        if word.lower() in (message.text.lower()).split(' '):
            await message.delete()
            await message.answer("Давай без матів)))")
            break

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
