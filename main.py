import logging
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

with open("data.json", "r") as file:
    bw = json.load(file)

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

@dp.message_handler(commands=["news"])
async def news(message : types.Message):
    await message.answer(f"НОВИНИ    :\n'{get_news()}'\n - https://dubnopk.com.ua/index.php/news")

@dp.message_handler(commands=["weather"])
async def weather(message : types.Message):
    await message.answer(f"Температура в м.Дубно - {str(temp)}°")
    if temp < 13:
        await message.answer("Бажано одягати куртку і штани)))")

@dp.message_handler()
async def badWord(message : types.Message):
    for word in bw["badWord"]:
        if word in (message.text).split(' '):
            await message.answer("Давай без матів)))")
            await message.delete()
            break

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)