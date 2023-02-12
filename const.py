import sqlite3
import telebot
from telebot import types
from exps import exp

token = "1012154742:AAEgZTWElbIucFdiKfy-jLjpnorY1KErLpU"
bot = telebot.TeleBot(token)
conn = sqlite3.connect("imagination.db")
max_users = 20
SQLITE_FILE = "imagination.db"
DEBUG = True


def inmarkup_start(lang):
    inmark_start = types.InlineKeyboardMarkup()
    inmark_start.row(types.InlineKeyboardButton(text=exp["create room"][lang], callback_data='create room'),
                   types.InlineKeyboardButton(text=exp["join room"][lang], callback_data='join room'))
    inmark_start.row(types.InlineKeyboardButton(text=exp["rules"][lang], callback_data='rules'),
                 types.InlineKeyboardButton(text=exp["settings"][lang], callback_data='settings'),
                 types.InlineKeyboardButton(text=exp["help"][lang], callback_data='help'))
    return inmark_start


def inmarkup_roominfo(lang):
    inmark_roominfo = types.InlineKeyboardMarkup()
    inmark_roominfo.row(types.InlineKeyboardButton(text=exp["update roominfo"][lang], callback_data='update roominfo'))
    inmark_roominfo.row(types.InlineKeyboardButton(text=exp["leave room"][lang], callback_data='leave room'))
    return inmark_roominfo


def inmarkup_roomcreator(lang):
    inmark_roominfo = types.InlineKeyboardMarkup()
    inmark_roominfo.row(types.InlineKeyboardButton(text=exp["update roominfo"][lang], callback_data='update roominfo'))
    inmark_roominfo.row(types.InlineKeyboardButton(text=exp["start game"][lang], callback_data='start game'))
    inmark_roominfo.row(types.InlineKeyboardButton(text=exp["delete room"][lang], callback_data='delete room'))
    return inmark_roominfo


def inmarkup_play():
    inmark_play = types.InlineKeyboardMarkup()
    inmark_play.row(types.InlineKeyboardButton(text="1", callback_data='play_1'),
                    types.InlineKeyboardButton(text="2", callback_data='play_2'),
                    types.InlineKeyboardButton(text="3", callback_data='play_3'))
    inmark_play.row(types.InlineKeyboardButton(text="4", callback_data='play_4'),
                    types.InlineKeyboardButton(text="5", callback_data='play_5'),
                    types.InlineKeyboardButton(text="6", callback_data='play_6'))
    return inmark_play


def inmarkup_discard():
    inmark_discard = types.InlineKeyboardMarkup()
    inmark_discard.row(types.InlineKeyboardButton(text="1", callback_data='discard_1'),
                    types.InlineKeyboardButton(text="2", callback_data='discard_2'),
                    types.InlineKeyboardButton(text="3", callback_data='discard_3'))
    inmark_discard.row(types.InlineKeyboardButton(text="4", callback_data='discard_4'),
                    types.InlineKeyboardButton(text="5", callback_data='discard_5'),
                    types.InlineKeyboardButton(text="6", callback_data='discard_6'))
    return inmark_discard


def inmarkup_vote(amount):
    inmark_vote = types.InlineKeyboardMarkup()
    count = 0
    while amount >= 3:
        inmark_vote.row(types.InlineKeyboardButton(text=str(count + 1), callback_data='vote_' + str(count + 1)),
                           types.InlineKeyboardButton(text=str(count + 2), callback_data='vote_' + str(count + 2)),
                           types.InlineKeyboardButton(text=str(count + 3), callback_data='vote_' + str(count + 3)))
        count += 3
        amount -= 3
    if amount == 2:
        inmark_vote.row(types.InlineKeyboardButton(text=str(count + 1), callback_data='vote_' + str(count + 1)),
                           types.InlineKeyboardButton(text=str(count + 2), callback_data='vote_' + str(count + 2)))
    if amount == 1:
        inmark_vote.row(types.InlineKeyboardButton(text=str(count + 1), callback_data='vote_' + str(count + 1)))
    return inmark_vote





















def markup_1(lang):
    mark1 = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    mark1.row(exp["create room"][lang])
    mark1.row(exp["join room"][lang])
    mark1.row(exp["leave room"][lang])
    mark1.row(exp["delete room"][lang])
    mark1.row(exp["start game"][lang])
    mark1.row(exp["play card"][lang])
    mark1.row(exp["discard card"][lang])
    mark1.row(exp["vote"][lang])
    return mark1

def markup_2():
    mark2 = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    mark2.row("1", "2", "3")
    mark2.row("4", "5", "6")
    return mark2

def markup_menu_default(lang):
    mark_m_d = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    mark_m_d.row(exp["create room"][lang], exp["join room"][lang])
    mark_m_d.row(exp["rules"][lang], exp["settings"][lang], exp["help"][lang])

def markup_menu_created(lang):
    mark_m_c = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    mark_m_c.row(exp["delete room"][lang], exp["start game"][lang])
    mark_m_c.row(exp["room info"][lang], exp["room settings"], exp["main menu"][lang])

def markup_menu_joined(lang):
    mark_m_j = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    mark_m_j.row(exp["leave room"][lang], exp["invite code"][lang])
    mark_m_j.row(exp["room info"][lang], exp["room settings"], exp["main menu"][lang])
    
def markup_back_menu(lang):
    mark_m_
