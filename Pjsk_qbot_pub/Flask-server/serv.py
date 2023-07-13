#!/usr/bin/env python3

import os
import json
import requests
from flask import request, Flask
import time
import re
from PIL import Image, ImageDraw, ImageFont
import random

def imageGen(font_size, edge_size, font_choice, image_file, text, pos, color, lean):
	if font_choice == 1:
		font = ImageFont.truetype('Fonts/ShangShouFangTangTi.ttf', font_size)
	else :
		font = ImageFont.truetype('Fonts/YurukaStd.ttf', font_size)
	lines = text.split('\n')
	max_width = max([font.getsize(t)[0] for t in lines])
	total_height = int(len(lines) * font_size * 0.97) 
	text_img = Image.new('RGBA', (max_width + 2*edge_size, total_height + 2*edge_size), (0, 0, 0, 0))
	text_draw = ImageDraw.Draw(text_img)
	for i, line in enumerate(lines):
		line_height = i * font_size * 0.97
		for dx in range(-edge_size, edge_size + 1):
			for dy in range(-edge_size, edge_size + 1):
				text_draw.text((dx + edge_size, dy + edge_size + line_height), line, font=font, fill="white")
		text_draw.text((edge_size, edge_size + line_height), line, font=font, fill=color)
	if lean!=0:
		text_img = text_img.rotate(lean, expand=1)
	image = Image.open('img/' + image_file)
	image.paste(text_img, pos,text_img)
	return image

def process_sticker_command(uid,cmd):
	if not cmd.startswith('/sticker'):
		return 'Invalid Format'
	
	parts = cmd.split()
	content = parts[1]
	content=content.replace('&amp;br','\n')
	content=content.replace('&amp;sp',' ')
	try :
		character_input = parts[2].lower()
		remain = " ".join(parts[2:]).lower()
	except Exception:
		character_input=''
		remain=''
	errors=0
	errorMsg=''
	
	character_list=['airi','akito','an','emu','ena','haruka','honami','ichika','kaito','kanade','kohane','len','luka','mafuyu','meiko','miku','minori','mizuki','nene','rin','rui','saki','shiho','shizuku','touya','tsukasa']
	character_len={'airi':18,'akito':16,'an':16,'emu':16,'ena':19,'haruka':16,'honami':18,'ichika':18,'kaito':16,'kanade':17,'kohane':17,'len':17,'luka':16,'mafuyu':17,'meiko':16,'miku':16,'minori':17,'mizuki':17,'nene':16,'rin':16,'rui':19,'saki':18,'shiho':18,'shizuku':16,'touya':18,'tsukasa':18}
	character_name = ''.join(c for c in character_input if c.isalpha())
	character_name = character_name if character_name in character_list else random.choice(character_list)
	character_number = ''.join(c for c in character_input if c.isdigit())
	character_number = character_number.zfill(2) if character_number and 1 <= int(character_number) <= character_len[character_name] and character_number%5!=0 else str(random.choice([x for x in range(1, character_len[character_name]) if x % 5 != 0])).zfill(2)
	character = character_name+'/'+character_name + '_' + character_number+'.png'
	
	
	pos = (20, 10)
	sp=','
	if '，' in remain:
		sp='，'
	if "pos=" in remain:
		spos = remain.split("pos=")[1].split()[0]
		spos_parts = spos.split(sp)
		if len(spos_parts) == 2 and spos_parts[0].isdigit() and spos_parts[1].isdigit():
			pos1, pos2 = int(spos_parts[0]), int(spos_parts[1])
			if 0 <= pos1 < 1000 and 0 <= pos2 < 1000:
				pos = (pos1, pos2)
				
	lean = 0
	if "lean=" in remain:
		slean = remain.split("lean=")[1].split()[0]
		if slean.isdigit():
			slean_val = int(slean)
			if 0 <= slean_val < 360:
				lean = slean_val
				
	fsize = 50
	if "fsize=" in remain:
		sfsize = remain.split("fsize=")[1].split()[0]
		if sfsize.isdigit():
			sfsize_val = int(sfsize)
			if 25 <= sfsize_val < 100:
				fsize = sfsize_val
				
	esize = 4
	if "esize=" in remain:
		sesize = remain.split("esize=")[1].split()[0]
		if sesize.isdigit():
			sesize_val = int(sesize)
			if 1 <= sesize_val < 8:
				esize = sesize_val
				
	font = 1
	if "font=1" in remain:
		font = 1
	elif "font=2" in remain:
		font = 2
		
	character_clr={'airi':(216,95,116),'akito':(224,94,62),'an':(91,91,106),'emu':(212,129,169),'ena':(109,91,101),'haruka':(49,94,168),'honami':(172,125,130),'ichika':(77,93,127),'kaito':(46,63,181),'kanade':(176,185,214),'kohane':(182,172,145),'len':(244,224,135),'luka':(240,198,223),'mafuyu':(97,72,146),'meiko':(168,136,93),'miku':(128,194,197),'minori':(201,142,124),'mizuki':(217,179,176),'nene':(183,186,174),'rin':(246,231,141),'rui':(206,160,240),'saki':(246,201,217),'shiho':(179,173,179),'shizuku':(141,170,197),'touya':(167,180,222),'tsukasa':(235,190,155)}
	clr = character_clr[character_name]
	if "clr=" in remain:
		sclr = remain.split("clr=")[1].split()[0]
		sclr_parts = sclr.split(sp)
		if len(sclr_parts) == 3 and all(part.isdigit() for part in sclr_parts):
			clr1, clr2, clr3 = int(sclr_parts[0]), int(sclr_parts[1]), int(sclr_parts[2])
			if 0 <= clr1 < 256 and 0 <= clr2 < 256 and 0 <= clr3 < 256:
				clr = (clr1, clr2, clr3)
				
	results_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Go-cqhttp",'data', "images")
	image_path = os.path.join(results_directory,str(uid)+'.png')
	imageGen(fsize,esize,font,character,content,pos,clr,lean).save(image_path, format='PNG')

	return str(uid)+'.png'

	
with open("config.json", "r") as jsonfile:
	config_data = json.load(jsonfile)
	config_data = config_data["qq_bot"]
	cqhttp_url = config_data['cqhttp_url']
	adminQQ = config_data['adminQQ']


server = Flask(__name__)


@server.route('/', methods=["GET"])
def index():
	return 'ok'


@server.route('/', methods=["POST"])
def get_message():
	character_list=['airi','akito','an','emu','ena','haruka','honami','ichika','kaito','kanade','kohane','len','luka','mafuyu','meiko','miku','minori','mizuki','nene','rin','rui','saki','shiho','shizuku','touya','tsukasa']
	if request.get_json().get('message_type') == 'private':
		uid = request.get_json().get('sender').get('user_id')
		message = request.get_json().get('raw_message')
		if re.search(r'^/help',message):
			send_private_message(uid,'[CQ:image,file=helper2.png]')
			print('help')
		elif re.search(r'^/preview',message):
			nam=message[9:]
			print(nam)
			nam = nam if nam in character_list else random.choice(character_list)
			send_private_message(uid,'[CQ:image,file='+nam+'.png]')
		elif re.search(r'^/sticker',message):
			send_private_message(uid,'[CQ:image,file='+process_sticker_command(uid,message)+']')
		elif re.search(r'^/echo',message) and uid==int(adminQQ):
			send_private_message(uid,'ECHO')
			print('echo')
	if request.get_json().get('message_type') == 'group':
		gid = request.get_json().get('group_id')
		uid = request.get_json().get('sender').get('user_id')
		message = request.get_json().get('raw_message')
		if re.search(r'^/help',message):
			send_group_message(gid,'[CQ:image,file=helper2.png]',uid)
			print('help')
		elif re.search(r'^/preview',message):
			nam=message[9:]
			print(nam)
			nam = nam if nam in character_list else random.choice(character_list)
			send_group_message(gid,'[CQ:image,file='+nam+'.png]',uid)
		elif re.search(r'^/sticker',message):
			send_group_message(gid,'[CQ:image,file='+process_sticker_command(uid,message)+']',uid)
	return "ok"


def send_private_message(uid, message):
	try:
		res = requests.post(url=cqhttp_url + "/send_private_msg",params={'user_id': int(uid), 'message': message}).json()
		if res["status"] == "ok":
			print("私聊消息发送成功")
		else:
			print(res)
			print("私聊消息发送失败，错误信息：" + str(res['wording']))
	except Exception as error:
		print("私聊消息发送失败")
		print(error)
		
		
def send_group_message(gid, message, uid):
	try:
		message = str('[CQ:at,qq=%s]\n' % uid) + message
		res = requests.post(url=cqhttp_url + "/send_group_msg",params={'group_id': int(gid), 'message': message}).json()
		if res["status"] == "ok":
			print("群消息发送成功")
		else:
			print("群消息发送失败，错误信息：" + str(res['wording']))
	except Exception as error:
		print("群消息发送失败")
		print(error)
		
		
server.run(port=7771, host='0.0.0.0', use_reloader=False)	
