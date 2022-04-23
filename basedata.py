import sqlite3
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

class BaseData:

    daysBttn = ReplyKeyboardMarkup(resize_keyboard=True)
    daysBttn.add(KeyboardButton("Понеділок"), KeyboardButton("Вівторок"), KeyboardButton("Середа"))
    daysBttn.add(KeyboardButton("Четвер"), KeyboardButton("П`ятниця"))

    HWbttn = ReplyKeyboardMarkup(resize_keyboard=True)
    HWbttn.add(KeyboardButton("немає"), KeyboardButton("пропустити"))
    
    removeBttns = ReplyKeyboardRemove()

    days = {
        "mon" : "Понеділок",
        "tue" : "Вівторок",
        "wed" : "Середа",
        "thu" : "Четвер",
        "fri" : "П`ятниця",
    }

    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
    def sql(self, args):
        with self.connection:
            return self.cursor.execute(args).fetchall()
    def get_student_id(self, name):
        with self.connection:
            return self.cursor.execute(f"SELECT user_id FROM Students WHERE username = '{name}' LIMIT 1").fetchall()
    def reg(self,id, name):
        with self.connection:
            return self.cursor.execute(f"INSERT INTO Students VALUES ({id}, '{name}')").fetchall()

    def getSubj(self, day):
        with self.connection:
            bttns = ReplyKeyboardMarkup(resize_keyboard=True)
            for subj in self.cursor.execute(f"SELECT sybject FROM Schedule WHERE day = '{day}'").fetchall():
                if subj[0] != None:
                    bttns.add(KeyboardButton(subj[0]))
            return bttns