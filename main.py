import logging, config,requests, pyowm,random, wikipedia, gspread

from urllib3 import Timeout
from aiogram.dispatcher import FSMContext
from basedata import BaseData
from googlesearch import search
from bs4 import BeautifulSoup as BS
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

try:
    logging.basicConfig(level=logging.INFO)

    wikipedia.set_lang("uk")
    gc = gspread.service_account(filename="credentials.json")
    sh = gc.open_by_key("1ddyrobtVFD0rk8WMOEMJ_nVk0rLSNN3fZo1twlLL-kM")
    data1 = sh.sheet1
    access_с = [1009661353, 1835953916]
    mainChatId = -1001544263329

    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    db = BaseData("basedata.db")
except Exception as E:
    print(f"[Error] {E}")

#---------------------------------------------------------------------------------------------------------------------------#

class Form(StatesGroup):
    googleSearch = State()
    wikisearch = State()
    DayHW = State()
    subj = State()
    HW = State()
    Link = State()
    times = State()
    absent = State()
    sendMsg = State()

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

#---------------------------------------------------------------------------------------------------------------------------#

async def isChatAdmin(memberID):
    try:
        chat = await bot.get_chat_member(mainChatId,memberID)
        print(chat.is_chat_admin())
        return chat.is_chat_admin()
    except Exception as E:
        print(E)
        return False

def reg(args : types.Message):
    if db.get_student_id(str(args.from_user.mention)) == []:
        db.reg(args.from_user.id, str(args.from_user.mention))

@dp.message_handler(commands=['wiki', 'wikipedia'])
async def wiki(msg : types.Message):
    await msg.answer("що ви шукаєте?")
    await Form.wikisearch.set()

@dp.message_handler(commands=['send'])
async def wiki(msg : types.Message):
    if msg.from_user.id in access_с:
        await msg.answer("Введіть текст")
        await Form.sendMsg.set()

#----------------------------------------------------------------------#

@dp.message_handler(commands=['help', 'start'])
async def info(msg : types.Message):
    text = """*Вот список доптупних Команд для усіх* : 
┈───────────ᗊ───────────┈
/temp - Температура в м.Дубно(та не тільки)
/news - Крайні новини з [сайту Коледжу](https://dubnopk.com.ua/index.php/news)
/wiki - пошук інформації у Wikipedia
/search - пошук інформації в GOOGLE

/schedulemon- розклад Пар на Понеділок
/scheduletue - розклад Пар на Вівторок
/schedulewed - розклад Пар на Середу
/schedulethu - розклад Пар на Четвер
/schedulefri - розклад Пар на П'ятницю
┈───────────ᗊ───────────┈
_Інші команди доступні тільки для Старости)))_"""
    await msg.answer(text, parse_mode="Markdown")

#---------------------------------------------------------------------------------------------------------------------------#

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
        del ind
        return
    data1.append_row(a)

#----------------------------------------------------------------------#

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

#----------------------------------------------------------------------#

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
        del answer

#----------------------------------------------------------------------#

@dp.message_handler(commands=['search', 's'])
async def Google_Shearch(args : types.Message):
    reg(args)
    await args.answer("що ви шукаєте?")
    await Form.googleSearch.set()

#----------------------------------------------------------------------#
    
@dp.message_handler(commands=["scheduleMon", "scheduleTue", "scheduleWed", "scheduleThu", "scheduleFri"])
async def Schedule(msgs : types.Message):
    reg(msgs)
    arg = msgs.text[-3::] if '@' not in msgs.text else msgs.text.split('@')[0][-3::]
    day = db.days[arg.lower()]
    answer = f"╰───╮⌬ *{day}* ╭───╯\n"
    for sybject, HW, times, url in db.sql(f"SELECT sybject, HW, times, Link FROM Schedule WHERE day = '{day}'"):
        Hw = f'\n    _ДЗ : {HW}_' if HW != None and HW != '' and HW != ' ' else ''
        answer += f"•{times if times != None else ''} - [{sybject}]({url}){Hw}\n" if sybject != None and sybject != '' and sybject != ' ' else '•\n'
    answer += "┈────────ᗊ────────┈"
    await msgs.answer(answer, parse_mode="Markdown")

#absent
@dp.message_handler(commands=["absent"])
async def Schedule(msgs : types.Message):
    reg(msgs)
    if msgs.from_user.id in access_с:
        await msgs.answer("Введіть відсутніх")
        await Form.absent.set()

@dp.message_handler(commands=["hw"])
async def news(message : types.Message):
    reg(message)
    if await isChatAdmin(message.from_user.id):
        await message.answer("Виберіть день", reply_markup=db.daysBttn)
        db.sql(f"INSERT INTO SetHW(user) VALUES ({message.from_user.id})")
        await Form.DayHW.set()
#----------------------------------------------------------------------#

@dp.message_handler(commands=["news"])
async def news(message : types.Message):
    reg(message)
    await message.answer(f"*НОВИНИ*  :\n{get_news()}\n\n_новини з_ [ДПФК РДГУ](https://dubnopk.com.ua/index.php/news)", parse_mode="Markdown")

#----------------------------------------------------------------------#

@dp.message_handler(commands=["temp"])
async def weather(message : types.Message):
    reg(message)
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

    await message.answer(f"Температура в *м.{city}* - {str(temp)}°", parse_mode="Markdown")

#---------------------------------------------------------------------------------------------------------------------------#

@dp.message_handler(state=Form.googleSearch)
async def googleS(args : types.Message, state : FSMContext):
    await state.finish()
    try:
        answer = "┈───────────ᗊ───────────┈\n"
        msg = await args.answer("Іде пошук...\n_це може зайняти деякий час_", parse_mode='Markdown')
        for url in search(args.text, lang='uk', num_results=15):
            try:
                reqs = requests.get(url)
                soup = BS(reqs.text, 'lxml')
                head = soup.find("head")
                title = head.find('title').get_text()
                answer += f"•[{title}]({url})\n"
            except:
                pass
        answer += "┈───────────ᗊ───────────┈"
        await msg.edit_text(answer, parse_mode="Markdown")
    except Exception as E:
        await args.answer(f"[ ! ] помилка - {E}")

#----------------------------------------------------------------------#

@dp.message_handler(state=Form.wikisearch)
async def wikipedias(title : types.Message, state : FSMContext):
    await state.finish()
    try:
        msg = await title.answer("Іде пошук...\n_це може зайняти деякий час_", parse_mode='Markdown')
        search = wikipedia.search(title.text, results=1)
        result = wikipedia.page(search)
        await msg.edit_text(f"*{result.title}*\n┈──────────────ᗊ──────────────┈\n{wikipedia.summary(search, sentences=9)}\n┈──────────────ᗊ──────────────┈\n[Wikipedia]({result.url})", parse_mode="Markdown")
    except Exception as a:
        await title.answer(f"[ ! ] помилка : {a}")


@dp.message_handler(state=Form.DayHW)
async def DaysHW(title : types.Message, state : FSMContext):
    if db.sql(f"SELECT user FROM SetHW WHERE user = '{title.from_user.id}'") != [] and await isChatAdmin(title.from_user.id):
        await state.finish()
        db.sql(f"UPDATE SetHW SET day = '{title.text}' WHERE user = '{title.from_user.id}'")
        bttn = db.getSubj(title.text)
        await title.answer("Виберіть предмет", reply_markup=bttn)
        await Form.subj.set()

@dp.message_handler(state=Form.subj)
async def DaysHW(title : types.Message, state : FSMContext):
    if db.sql(f"SELECT user FROM SetHW WHERE user = '{title.from_user.id}'") != [] and await isChatAdmin(title.from_user.id):
        await state.finish()
        db.sql(f"UPDATE SetHW SET subject = '{title.text}'")
        await title.answer("Введіть ДЗ\nякщо ДЗ немає або ви не знаєте\nпишіть *немає*", reply_markup=db.removeBttns, parse_mode='Markdown')
        await Form.HW.set()

@dp.message_handler(state=Form.HW)
async def DaysHW(title : types.Message, state : FSMContext):
    if db.sql(f"SELECT user FROM SetHW WHERE user = '{title.from_user.id}'") != [] and await isChatAdmin(title.from_user.id):
        await state.finish()
        if title.text.lower() != 'немає':
            day, subject = db.sql(f"SELECT day, subject FROM SetHW WHERE user = '{title.from_user.id}'")[0]
            db.sql(f"UPDATE Schedule SET HW = '{title.text}' WHERE day = '{day}' and sybject = '{subject}'")
        await title.answer("Введіть посилання\nякщо посилання немає або ви не знаєте\nпишіть *немає*", parse_mode='Markdown')
        await Form.Link.set()

@dp.message_handler(state=Form.Link)
async def DaysHW(title : types.Message, state : FSMContext):
    if db.sql(f"SELECT user FROM SetHW WHERE user = '{title.from_user.id}'") != [] and await isChatAdmin(title.from_user.id):
        await state.finish()
        if title.text.lower() != 'немає':
            day, subject = db.sql(f"SELECT day, subject FROM SetHW WHERE user = '{title.from_user.id}'")[0]
            db.sql(f"UPDATE Schedule SET Link = '{title.text}' WHERE day = '{day}' and sybject = '{subject}'")
        await title.answer("Введіть час зустрічі\n_наприклад:_ *8:30*", parse_mode='Markdown')
        await Form.times.set()

@dp.message_handler(state=Form.times)
async def DaysHW(title : types.Message, state : FSMContext):
    if db.sql(f"SELECT user FROM SetHW WHERE user = '{title.from_user.id}'") != [] and await isChatAdmin(title.from_user.id):
        await state.finish()
        if title.text.lower() != 'немає':
            day, subject = db.sql(f"SELECT day, subject FROM SetHW WHERE user = '{title.from_user.id}'")[0]
            db.sql(f"UPDATE Schedule SET times = '{title.text}' WHERE day = '{day}' and sybject = '{subject}'")
        db.sql(f"DELETE FROM SetHW WHERE user = '{title.from_user.id}'")
        await title.answer("Все готово\nдякую)")
        await Form.times.set()


@dp.message_handler(state=Form.absent)
async def absept(members : types.Message, state : FSMContext):
    if members.from_user.id == 1009661353:
        print(members.from_user.id, type(members.from_user.id))
        await state.finish()
        for member in members.text.split(' '):
            try:
                await bot.send_message(db.get_student_id(member)[0][0], "Напиши старості причину своєї відсутності на парі !\nнегайно !!!")
            except Exception as E:
                print(E)

@dp.message_handler(state=Form.sendMsg)
async def wikipedias(msg : types.Message, state : FSMContext):
    if msg.from_user.id in access_с:
        await state.finish()
        try:
            await bot.send_message(mainChatId, msg.text, parse_mode="Markdown")
        except Exception as a:
            await msg.answer(f"[ ! ] помилка : {a}")

#---------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
