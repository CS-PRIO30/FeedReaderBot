# -*- coding: utf-8 -*-
from urllib.request import urlopen #http://stackoverflow.com/questions/2792650/python3-error-import-error-no-module-name-urllib2#2792652
import telegram
from telegram import *

TOKEN_TELEGRAM = '282010348:AAHWydTbEOODrsZIzJMYFvmuVyVSK6G1b_Q' 
bot = telegram.Bot(TOKEN_TELEGRAM)

try:
    update_id = bot.getUpdates()[0].update_id
except IndexError:
    update_id = None
def main():
	reply_keyboard = [['Boy'], ['Girl'], ['Other'],]
	bot.sendMessage(chat_id = 31923577, text= 'Hi', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,one_time_keyboard=True))
 
			
main()



