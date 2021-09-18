import logging
from os import access
import config
import json
import requests
import pyowm

from bs4 import BeautifulSoup as BS
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

owm = pyowm.OWM(config.wApiKey)
w = owm.weather_manager().weather_at_place("Дубно")
myWeather = w.weather
temp = myWeather.temperature('celsius')["temp"]
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

    soup = BS(r.text, "lxml")
    news = soup.find_all("div", class_="art-box-body")
    for article in news:
        title = article.find("span", class_="art-postheadericon").text.strip()
        #desc = article.find("span").text.strip()
        return title

@dp.message_handler(commands=['help'])
async def info(msg : types.Message):
    await msg.answer("""Вот список доптупних Команд для усіх : 
/temp - Температура в м.Дубно
/news - Крайні новини з сайту Коледжу https://dubnopk.com.ua/index.php/news
/schedulemon- розклад Пар на Понеділок
/scheduletue - розклад Пар на Вівторок
/schedulewed - розклад Пар на Середу
/schedulethu - розклад Пар на Четвер
/schedulefri - розклад Пар на П'ятницю

Інші команди доступні тільки для Старости)))
""")

@dp.message_handler(commands=['SetInfo'])
async def SetInfo(args : types.Message):
    a = args.get_args().split(",")
    if len(a) != 6:
        await args.answer("Потрібно 6 аргументів")
        return
    surname = a[0]
    KeyInfo = {
        "surname" : "surname",
        "full name" : "name",
        "age" : 15,
        "status" : None,
        "num in list" : 1,
        "phone" : "немає",
    }
    arr = list(KeyInfo.keys())
    for i in range(len(arr)):
        KeyInfo[arr[i]] = a[i]

    data["StudentsInfo"][surname] = KeyInfo
    with open("data.json", "w", encoding="utf8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

@dp.message_handler(commands=['GetInfo'])
async def Getinfo(args : types.Message):
    answer = ""
    try:
        answer += f"___{data['StudentsInfo'][args.get_args()]['surname']}___\n"
        for key, value in data["StudentsInfo"][args.get_args()].items():
            answer += f"{key} - {value}\n"
    except KeyError:
        answer = "Ім'я не знайдено"
    await args.answer(answer)

@dp.message_handler(commands=['GetAllInfo'])
async def GetAllInfo(args : types.Message):
    for st in list(data["StudentsInfo"].keys()):
        answer = f"___{data['StudentsInfo'][st]['surname']}___\n"
        for key, value in data['StudentsInfo'][st].items():
            answer += f"{key} - {value}\n"
        await args.answer(answer)
        answer = ""

@dp.message_handler(commands=["scheduleMon", "scheduleTue", "scheduleWed", "scheduleThu", "scheduleFri"])
async def Schedule(msgs : types.Message):
    msg = msgs.text.split('S')[0]
    arg = msg[-4:-1]
    try:
        await msgs.answer('\n'.join(data['Days'][arg].keys()))
    except KeyError:
        await msgs.answer("day not found !")

@dp.message_handler(commands=["news"])
async def news(message : types.Message):
    await message.answer(f"НОВИНИ  :\n{get_news()}\n - https://dubnopk.com.ua/index.php/news")

@dp.message_handler(commands=["temp"])
async def weather(message : types.Message):
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
