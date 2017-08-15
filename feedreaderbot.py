# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen #http://stackoverflow.com/questions/2792650/python3-error-import-error-no-module-name-urllib2#2792652
import feedparser
from telegraphapi import Telegraph
import telegram
from telegram import *
import time
import os
import re
import sqlite3
import schedule
import datetime
from telegram.error import NetworkError, Unauthorized
import threading 
from feedfinder2 import find_feeds


telegraph = Telegraph()
telegraph.createAccount("PythonTelegraphAPI")
TOKEN_TELEGRAM = '282010348:AAHWydTbEOODrsZIzJMYFvmuVyVSK6G1b_Q' 
DATABASE_NAME = 'RSS.db'
bot = telegram.Bot(TOKEN_TELEGRAM)
chat_id_List = []


try:
    update_id = bot.getUpdates()[0].update_id
except IndexError:
    update_id = None

def init_DB():
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	cursor.execute("""CREATE TABLE IF NOT EXISTS urlSites (id integer primary key autoincrement, url text , int chat_id) """)           
	cursor.execute("""CREATE TABLE IF NOT EXISTS feedUser (id integer primary key autoincrement, url text, base_url text, chat_id int , name text, dateAdded text, active int) """)
	cursor.execute("""CREATE TABLE IF NOT EXISTS users (id integer primary key autoincrement, chat_id int , name text, time_added text) """)
	conn.commit()
	conn.close()

def insert_RSS_Feed_DB(url,user):
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	cursor.execute("INSERT OR IGNORE INTO feedUser VALUES (?,?)",url,user)
	conn.commit()
	conn.close()

def load_chat_id():
	global chat_id_List
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	cursor.execute("""SELECT * FROM users """)
	conn.commit()
	chat_id_List = [item[0] for item in cursor.fetchall()]
	conn.close()

def load_User_Me():
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	chat_id = (31923577,)
	cursor.execute("INSERT OR IGNORE INTO users (chat_id,name, time_added ) VALUES (?,?,?)",(31923577,"me","") )
	conn.commit()
	conn.close()


def sendNewFeedsToEveryUser():
	pass

def listenForBotCommandsandNewUsers():
	global update_id
	waitListAdd = set()
	waitListRemove = set()
	while True:
		try:
			for update in bot.getUpdates(offset=update_id, timeout=10):
				#print(update)
				
				try:
					update_id = update.update_id + 1
				except Exception as e:
					print("Error getting update ", e)
				
				try:
					if update.callback_query:
						query = update.callback_query
						bot.answerCallbackQuery(callback_query_id = query.id)
						chat_id = query.message.chat_id
						print(query.data, chat_id)
				except Exception as e:
					print("error in answering query ", e)
				
				####
				    #ADD NEW USERS
				####
				
				
				
				if update.message:
					chat_id = update.message.chat_id
					try:
						if update.message.chat_id:  # your bot can receive updates without messages
							if chat_id not in chat_id_List:
								now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
								conn = sqlite3.connect( DATABASE_NAME ) 
								cursor = conn.cursor()
								url = chat_id
								username = update.message.from_user.first_name + " " + update.message.from_user.last_name
								cursor.execute( "INSERT OR IGNORE INTO users (chat_id,name, time_added) VALUES (?,?,?)", (chat_id, username, now) )
								conn.commit()
								conn.close()			
						#bot.getUpdates(offset=update_id,timeout=0)
					except Exception as e:
						print("error in getting new users", e)
						
						
					####
						#ADD/REMOVE NEW FEED
					####
					try:
						if update.message.entities[0].type == "bot_command":
							if "/add" in update.message.text:
								print("add", end=" ")
								print(chat_id)
								waitListAdd.add(chat_id) 
								print(waitListAdd)
					except Exception as e:
						print("error in adding new feed", e)
					
					try:	
						if "/list" in update.message.text:
							print("list", end=" ")
							#print(chat_id)
							conn = sqlite3.connect( DATABASE_NAME ) 
							cursor = conn.cursor()
							cursor.execute("""SELECT url FROM feedUser WHERE chat_id = {} AND active = 1""".format(chat_id) )
							conn.commit()
							allRssFeedUser = cursor.fetchall() 
							conn.close()
							COLUMN = 0
							allRssFeedUser = [elt[COLUMN] for elt in allRssFeedUser]
							lenFeed = len(allRssFeedUser)
							text = "<b>You have {} feed subscriptions:\n\n</b>".format( lenFeed )
							keyboard = [	
											[
												InlineKeyboardButton("<<", callback_data='start'),
												InlineKeyboardButton("< Previous", callback_data='previous'),
												InlineKeyboardButton("Next >", callback_data='next'),
												InlineKeyboardButton(">>", callback_data='end'),
											]
									   ]
							reply_markup = InlineKeyboardMarkup(keyboard)
							textFeeds = ""
							i = 0
							for item in allRssFeedUser:
								i = i+1
								textFeeds = textFeeds + '<b>{}. </b><a href="{}">{}</a>\n'.format(i,item,item)
							bot.sendMessage(disable_web_page_preview = True, chat_id=chat_id, text = text + textFeeds, parse_mode="Html", reply_markup = reply_markup)
							
					except Exception as e:
						print("error in sending user subscribed feeds ", e)
					
					try:
						if "/remove" in update.message.text:
							print("remove", end=" ")
							print(chat_id)
							waitListRemove.add(chat_id) 
							print(waitListRemove)
							conn = sqlite3.connect( DATABASE_NAME ) 
							cursor = conn.cursor()
							cursor.execute("""SELECT url FROM feedUser WHERE chat_id = {} AND active=1""".format(chat_id) )
							conn.commit()
							allRssFeedUser = cursor.fetchall() 
							conn.close()
							COLUMN = 0
							allRssFeedUser=[elt[COLUMN] for elt in allRssFeedUser]
							#print("a: allRssFeedUser")
							print(allRssFeedUser)
							if len( allRssFeedUser ) > 0:
								i = 0
								reply_keyboard = []
								for item in allRssFeedUser:
									i = i+1
									reply_keyboard.append( [str(i) + ". " + item] )
								
								
								bot.sendMessage(chat_id = chat_id, text= 'Select feed to remove: ', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
							else:
								bot.sendMessage(chat_id = chat_id, text= "You don't have any feed yet")
					except Exception as e:
						print("error in get request of removing feeds ", e)
					
					
					#remove feed
					try:
						if chat_id in waitListRemove and update.message.text.split(" ")[1]:
							try:
								url = update.message.text.split(" ")[1]
								waitListRemove.discard(chat_id) 
								conn = sqlite3.connect( DATABASE_NAME ) 
								cursor = conn.cursor()
								cursor.execute("""UPDATE FeedUser SET active=0 WHERE chat_id = {} AND url='{}'""".format(chat_id,url) )
								conn.commit()
								conn.close()
								bot.sendMessage(chat_id = chat_id, text = "Feed {} Successfully removed!".format(url))
							except Exception as e:
								print("error actual removing feed from database ",e)	
					except:
						pass
					
					try:
						if update.message.entities[0].type == "url":
							if chat_id in waitListAdd:
								conn = sqlite3.connect( DATABASE_NAME ) 
								cursor = conn.cursor()
								offset = update.message.entities[0].offset
								length = update.message.entities[0].length
								url = update.message.text[offset:length+offset]
								username = update.message.from_user.first_name + " " + update.message.from_user.last_name
								print(url)
								
								try:
									now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
									cursor.execute( "INSERT  INTO feedUser (url,base_url,chat_id,name,dateAdded,active) VALUES (?,?,?,?,?,?)", (url,"",chat_id,username,now,1) )
									conn.commit()
									bot.sendMessage(chat_id = chat_id, text = "Feed {} Successfully added!".format(url))
									
								except Exception as e:
									print("error adding 123 feed url database 123 ", e)
									bot.sendMessage(chat_id = chat_id, text = "Error adding url: {}".format(url))
								conn.close()		
								waitListAdd.discard(chat_id)
					except Exception as e:
						print("error in entities add url in database ", e)
						
				
					
					
		except NetworkError:
			print("netErr")
			time.sleep(1)
		except Unauthorized:
			print("unath")
			update_id += 1
		except Exception as e :
			print("error at start ", e)
	
def main():
	init_DB()
	load_User_Me()
	load_chat_id()
	threading.Thread(target=listenForBotCommandsandNewUsers).start()
	schedule.every(20).minutes.do( sendNewFeedsToEveryUser )
	while True:
		try:
			schedule.run_pending()
		except NetworkError:
			time.sleep(10)
		except Unauthorized:
			update_id += 1
			
main()



