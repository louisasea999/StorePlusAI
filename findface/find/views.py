# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
import base64
import urllib2
import urllib
import time
import socket
import sys,json
import string
import random
import cv2
import os
import re
import numpy as np
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from find.models import AllFaces,ErrFaces,AllFaceSets
from findface.settings import STATIC_URL
from json.decoder import errmsg
from django.template.context_processors import request
from PIL import Image,ImageEnhance
import pytesseract

socket.setdefaulttimeout(20.0) 


reload(sys)

sys.setdefaultencoding('utf8')
# Create your views here.

key = "cY2YOwFKwF_c9yu4nnBruTgBvjT_9Tb1"
secret = "iMMYMgYt2cJu25-skaf0oOiRnZpum9rX"

key_concurrency = "cY2YOwFKwF_c9yu4nnBruTgBvjT_9Tb1"
secret_concurrency = "iMMYMgYt2cJu25-skaf0oOiRnZpum9rX"

key_list = []
secret_list = []

key_list.append(key)
key_list.append(key_concurrency)

secret_list.append(secret)
secret_list.append(secret_concurrency)

scale_landmark = '0'
scale_attrs = 'gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus'
pictime_base = {}

def getmain(request):
	return render(request,"test.html")

def savepic(request):
	global pictime_base
	result_dict = {}
	pic = str(request.POST["data_info"])
	pic_data = pic.replace('data:image/png;base64,', '')
	pic_data = base64.b64decode(pic_data)
	
	pic_hour = str(request.POST["data_info_hour"])
	pic_data_hour = pic_hour.replace('data:image/png;base64,', '')
	pic_data_hour = base64.b64decode(pic_data_hour)
	pic_min = str(request.POST["data_info_min"])
	pic_data_min = pic_min.replace('data:image/png;base64,', '')
	pic_data_min = base64.b64decode(pic_data_min)
	pic_sec = str(request.POST["data_info_sec"])
	pic_data_sec = pic_sec.replace('data:image/png;base64,', '')
	pic_data_sec = base64.b64decode(pic_data_sec)
	
	
	ISOTIMEFORMAT='%Y%m%d%H%M%S'
	pwd = os.getcwd()
	interval_sec = request.POST["intsec"]
	snapseq = request.POST["snapseq"]
	pic_dir =  request.POST["file_name"] + '_' + interval_sec
	#pwd 图像存储路径
	pic_path = pwd + '\\find\\static\\pic\\' + pic_dir + '\\'
	currenttime = str(time.strftime(ISOTIMEFORMAT))
	pic_name = currenttime + '.png'
	pic_name_hour = currenttime + '_hour.png'
	pic_name_min = currenttime + '_min.png'
	pic_name_sec = currenttime + '_sec.png'
	pic_fullpath = pic_path + pic_name
	pic_fullpath_hour = pic_path + pic_name_hour
	pic_fullpath_min = pic_path + pic_name_min
	pic_fullpath_sec = pic_path + pic_name_sec
	if not os.path.exists(pic_path):
		os.makedirs(pic_path)
	file = open(pic_fullpath,'wb')
	file.write(pic_data)
	file.close()

	if len(pictime_base) == 0:
		file_hour = open(pic_fullpath_hour,'wb')
		file_hour.write(pic_data_hour)
		file_hour.close()
		file_min = open(pic_fullpath_min,'wb')
		file_min.write(pic_data_min)
		file_min.close()
		file_sec = open(pic_fullpath_sec,'wb')
		file_sec.write(pic_data_sec)
		file_sec.close()
		pictime_hour = Reg_DateTime(pic_fullpath_hour, 'hour')
		pictime_min = Reg_DateTime(pic_fullpath_min, 'min')
		pictime_sec = Reg_DateTime(pic_fullpath_sec, 'sec')
		#2018-05-16 13:53:51.401192
		if pictime_hour != None and pictime_min != None and pictime_sec != None:
			pictime = '2018-04-01 ' + str(pictime_hour) + ':' + str(pictime_min) + ':' + str(pictime_sec)
			pictime_base['seqno'] = int(snapseq)
			pictime_base['time'] = pictime
			print str(pictime)
		else:
			print 'delete ',pic_fullpath_hour
			os.remove(pic_fullpath_hour)
			os.remove(pic_fullpath_min)
			os.remove(pic_fullpath_sec)

	db_save_picpath = '\\static\\pic\\' + pic_dir + '\\'
	db_save_picname = pic_name
	
	global scale_landmark,scale_attrs

	face_data = DetectFace(pic_fullpath,scale_landmark,scale_attrs)
	
	if face_data:
		if 'error_message' in face_data:
			face_data = json.loads(face_data)
			newerr = ErrFaces()
			newerr.picpath = db_save_picpath + db_save_picname
			newerr.errmsg = face_data['error_message']
			newerr.fixstatus = 'N'
			newerr.snapseq = snapseq
			newerr.snapint = interval_sec
			newerr.save()
		elif len(face_data['faces']) == 0:
			newerr = ErrFaces()
			newerr.picpath = db_save_picpath + db_save_picname
			newerr.errmsg = 'No faces detected'
			newerr.snapseq = snapseq
			newerr.snapint = interval_sec
			newerr.save()
		elif len(face_data['faces']) > 0:
			if len(pictime_base) > 0:
				t = time.mktime(time.strptime(pictime_base['time'], "%Y-%m-%d %H:%M:%S"))
				diffsec = 0.0
				diffsec = (int(snapseq) - pictime_base['seqno']) * int(interval_sec) / 1000
				t = t + diffsec
				pic_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
			else:
				pic_time = None
			savenewface(face_data,db_save_picpath,db_save_picname,snapseq,interval_sec,pic_time)
	
	result_dict['valid_num'] = AllFaces.objects.filter(picpath=db_save_picpath).count()
	result_dict['invalid_num'] = ErrFaces.objects.filter(picpath__contains=db_save_picpath,errmsg='No faces detected').count()
	result_dict['err_num'] = ErrFaces.objects.filter(fixstatus='N',picpath__contains=db_save_picpath).count()

	result_info = json.dumps(result_dict)
	return HttpResponse(result_info,content_type="application/json")

	
def fixpic(request):
	valid_num2 = 0
	invalid_num2 = 0
	pic_time = None
	global scale_landmark,scale_attrs
	needfix = ErrFaces.objects.filter(fixstatus='N').order_by('picpath')
	save_pre_picpath = ''
	result_list = []
	
	pwd = os.getcwd()
	for fixdata in needfix:
		pic_path = pwd + '\\find'+fixdata.picpath
		if save_pre_picpath != fixdata.picpath:
			face_data = DetectFace(pic_path,scale_landmark,scale_attrs)
			if face_data:
				if 'error_message' in face_data:
					pass
				elif len(face_data['faces']) == 0:
					errface = ErrFaces.objects.get(id=fixdata.id)
					errface.errmsg = 'No faces detected'
					errface.fixstatus = 'Y'
					errface.save()
					invalid_num2 += 1
				elif len(face_data['faces']) > 0:
					pic_time = '1990-01-01 00:00:00'
					fix_path = ('\\').join(fixdata.picpath.split('\\')[:-1]) + '\\'
					fix_name = fixdata.picpath.split('\\')[-1]
					savenewface(face_data,fix_path,fix_name,fixdata.snapseq,fixdata.snapint,pic_time)
					errface = ErrFaces.objects.get(id=fixdata.id)
					errface.errmsg = 'Faces detected'
					errface.fixstatus = 'Y'
					errface.save()
					valid_num2 += 1
		else:
			ErrFaces.objects.filter(id=fixdata.id).delete()
		save_pre_picpath = fixdata.picpath
	
	fixtime_data = AllFaces.objects.filter(pictime='1990-01-01 00:00:00').values('picpath').distinct()
	for i in fixtime_data:
		fix_result = AddDateTime(i['picpath'])
		result_list.append(fix_result)
					
	result_info = 'Fixing error pics result\r\n' + \
				'Number of pics needing fixed      :' + str(len(needfix)) + \
				'\r\nNumber of pics fixed successfully :' + str(valid_num2+invalid_num2) + '\r\n\r\n'
	if len(result_list) > 0:
		result_info = result_info + 'Adding datetime result\r\n'
		for i in range(len(result_list)):
			result_info = result_info + result_list[i]['path'] + ': ' + result_list[i]['num'] + '\r\n'
	return HttpResponse(result_info,content_type="text/plain")

def addtofaceset(request):
	data_add = AllFaces.objects.filter(faceset_status='N')
	result = [0,0]
	for face_add in data_add:
		all_outer_id = GetOuterId()
		facetoken = face_add.facetoken
		searchresult = SearchFaceSet(facetoken,all_outer_id)
		result[0] += searchresult[0]
		result[1] += searchresult[1]

	result_info = str(result[0]) + ' new facesets are created; ' + str(result[1]) + ' facesets are updated!'
	return HttpResponse(result_info,content_type="text/plain")

def DetectFace(filepath,landmark,attrs):
	face_dict={}
	http_url='https://api-cn.faceplusplus.com/facepp/v3/detect'
	face_token=''
	filepath = filepath
	boundary = '----------%s' % hex(int(time.time() * 1000))
	data = []
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
	data.append(key)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
	data.append(secret)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
	data.append(landmark)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
	data.append(attrs)
	data.append('--%s' % boundary)
	fr=open(filepath,'rb')
	data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
	data.append('Content-Type: %s\r\n' % 'application/octet-stream')
	data.append(fr.read())
	fr.close()
	data.append('--%s--\r\n' % boundary)

	http_body='\r\n'.join(data)
	#buld http request
	req=urllib2.Request(http_url)
	#header
	req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
	req.add_data(http_body)
	try:
		#req.add_header('Referer','http://remotserver.com/')
		#post data to server
		resp = urllib2.urlopen(req, timeout=10)
		#get response
		qrcont=resp.read()
		face_dict = json.loads(qrcont)
		return face_dict
	except urllib2.HTTPError as e:
		return e.read()
	#if face_dict:
		#face_token=face_dict['faces'][0]['face_token']
		#return face_dict
		
def SearchFaceSet(facetoken,all_outer_id):
	max_outer_id = ''
	max_facetoken = ''
	score = 0
	http_url_create='https://api-cn.faceplusplus.com/facepp/v3/search'
	newfaceset_num = 0
	updfaceset_num = 0
	if len(all_outer_id) == 0:
		new_outer_id = GenerateNewOuterId()
		#在face++新建一个faceset
		new_faceset = CreatFaceSet(facetoken,new_outer_id)
		#同步本地faceset
		Insert_FaceSet_db(new_faceset)
		#更新facetable
		Update_AllFaces_FaceSet_db(facetoken,new_faceset['outer_id'])
		newfaceset_num += 1
		print 'New faceset:', new_faceset['outer_id']
	else:
		for i in range(len(all_outer_id)):
			outer_id = all_outer_id[i]
			boundary = '----------%s' % hex(int(time.time() * 1000))
			data = []
			data.append('--%s' % boundary)
			data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
			data.append(key)
			data.append('--%s' % boundary)
			data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
			data.append(secret)
			data.append('--%s' % boundary)
			data.append('Content-Disposition: form-data; name="%s"\r\n' % 'face_token')
			data.append(facetoken)
			data.append('--%s' % boundary)
			data.append('Content-Disposition: form-data; name="%s"\r\n' % 'outer_id')
			data.append(outer_id)
			data.append('--%s--\r\n' % boundary)
			
			http_body_create='\r\n'.join(data)
			#buld http request
			req=urllib2.Request(http_url_create)
			#header
			req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
			req.add_data(http_body_create)
			try:
				#req.add_header('Referer','http://remotserver.com/')
				#post data to server
				resp = urllib2.urlopen(req, timeout=10)
				#get response
				qrcont=resp.read()
				qrcont = json.loads(qrcont)
				if 'results' in qrcont:
					if qrcont['results'][0]['confidence'] > score:
						score = qrcont['results'][0]['confidence']
						max_outer_id = outer_id
						max_facetoken = qrcont['results'][0]['face_token']
	
				if score > 85:    #分数大于85直接认定为本人 防止运行太频繁造成QPS爆掉
					break
	
			except urllib2.HTTPError as e:
				print e.read()
		if score != 0 and score > 65:
			#我觉得没必要再compare，这里的分数跟上面search的最优分数应该是一致的(经测试，是一样的）。主要来确定这个score多少分合适
			#comp_result = Compare_2Faces(facetoken,max_facetoken)
			#comp_score = comp_result['confidence']
			#添加人脸到分数大于65的faceset
			add_face_result = AddFace(facetoken,max_outer_id)
			#同步本地faceset
			Update_FaceSet_db(add_face_result)
			#更新facetable
			Update_AllFaces_FaceSet_db(facetoken,max_outer_id)
			updfaceset_num += 1
			print 'Add to faceset:', max_outer_id,'|',score
		else:
			new_outer_id = GenerateNewOuterId()
			#在face++新建一个faceset
			new_faceset = CreatFaceSet(facetoken,new_outer_id)
			#同步本地faceset
			Insert_FaceSet_db(new_faceset)
			#更新facetable
			Update_AllFaces_FaceSet_db(facetoken,new_faceset['outer_id'])
			newfaceset_num += 1
			print 'New faceset:', new_faceset['outer_id'],'|',score
	
	result = []
	result.append(newfaceset_num)
	result.append(updfaceset_num)
	return result

def CreatFaceSet(facetoken,outer_id):
	result = {}
	http_url_create='https://api-cn.faceplusplus.com/facepp/v3/faceset/create'
	boundary = '----------%s' % hex(int(time.time() * 1000))
	data = []
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
	data.append(key)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
	data.append(secret)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'outer_id')
	data.append(outer_id)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'face_tokens')
	data.append(facetoken)
	data.append('--%s--\r\n' % boundary)

	http_body_create='\r\n'.join(data)
	#buld http request
	req=urllib2.Request(http_url_create)
	#header
	req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
	req.add_data(http_body_create)
	try:
		#req.add_header('Referer','http://remotserver.com/')
		#post data to server
		resp = urllib2.urlopen(req, timeout=10)
		#get response
		qrcont=resp.read()
		qrcont = json.loads(qrcont)
		result['faceset_token'] = qrcont['faceset_token']
		result['face_count'] = qrcont['face_count']
		result['outer_id'] = qrcont['outer_id']
		result['face_tokens'] = facetoken

	except urllib2.HTTPError as e:
	    print e.read()
	return result
	    
def AddFace(facetoken,outer_id):
	result = {}
	http_url_create='https://api-cn.faceplusplus.com/facepp/v3/faceset/addface'
	boundary = '----------%s' % hex(int(time.time() * 1000))
	data = []
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
	data.append(key)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
	data.append(secret)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'outer_id')
	data.append(outer_id)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'face_tokens')
	data.append(facetoken)
	data.append('--%s--\r\n' % boundary)

	http_body_create='\r\n'.join(data)
	#buld http request
	req=urllib2.Request(http_url_create)
	#header
	req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
	req.add_data(http_body_create)
	try:
		#req.add_header('Referer','http://remotserver.com/')
		#post data to server
		resp = urllib2.urlopen(req, timeout=10)
		#get response
		qrcont=resp.read()
		qrcont = json.loads(qrcont)
		result['faceset_token'] = qrcont['faceset_token']
		result['face_count'] = qrcont['face_count']
		result['outer_id'] = qrcont['outer_id']
		result['face_tokens'] = facetoken

	except urllib2.HTTPError as e:
	    print e.read()
	return result
	
def Compare_2Faces(facetoken1,facetoken2):
	result = {}
	http_url_create='https://api-cn.faceplusplus.com/facepp/v3/compare'
	boundary = '----------%s' % hex(int(time.time() * 1000))
	data = []
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
	data.append(key)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
	data.append(secret)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'face_token1')
	data.append(facetoken1)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'face_token2')
	data.append(facetoken2)
	data.append('--%s--\r\n' % boundary)

	http_body_create='\r\n'.join(data)
	#buld http request
	req=urllib2.Request(http_url_create)
	#header
	req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
	req.add_data(http_body_create)
	try:
		#req.add_header('Referer','http://remotserver.com/')
		#post data to server
		resp = urllib2.urlopen(req, timeout=10)
		#get response
		qrcont=resp.read()
		qrcont = json.loads(qrcont)
		result['confidence'] = qrcont['confidence']

	except urllib2.HTTPError as e:
	    print e.read()
	return result

def savenewface(facesdata,save_path,save_name,snapseq,snapint,pictime):
	for singleface in facesdata['faces']:
		newface = AllFaces()
		newface.imageid = facesdata['image_id']
		newface.facetoken = singleface['face_token']
		newface.picpath = save_path
		newface.picname = save_name
		newface.pictime = pictime
		newface.snapseq = snapseq
		newface.snapint = snapint
		attrs = singleface['attributes']
		newface.gender = attrs['gender']['value']
		newface.age = attrs['age']['value']
		newface.eyestatus = attrs['eyestatus']
		newface.emotion = attrs['emotion']
		newface.ethnicity = attrs['ethnicity']['value']
		newface.male_score = attrs['beauty']['male_score']
		newface.female_score = attrs['beauty']['female_score']
		newface.skinstatus = attrs['skinstatus']
		newface.save()


def recognize_datetime(filepath):
	face_dict={}
	http_url='https://api-cn.faceplusplus.com/imagepp/beta/recognizetext'
	face_token=''
	filepath = filepath
	boundary = '----------%s' % hex(int(time.time() * 1000))
	data = []
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
	data.append(key)
	data.append('--%s' % boundary)
	data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
	data.append(secret)
	data.append('--%s' % boundary)
	fr=open(filepath,'rb')
	data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
	data.append('Content-Type: %s\r\n' % 'application/octet-stream')
	data.append(fr.read())
	fr.close()
	data.append('--%s--\r\n' % boundary)

	http_body='\r\n'.join(data)
	#buld http request
	req=urllib2.Request(http_url)
	#header
	req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
	req.add_data(http_body)
	try:
		#req.add_header('Referer','http://remotserver.com/')
		#post data to server
		resp = urllib2.urlopen(req, timeout=10)
		#get response
		qrcont=resp.read()
		face_dict = json.loads(qrcont)
		return face_dict
	except urllib2.HTTPError as e:
		return e.read()

def GetOuterId():
	outer_id_arr = []
	all_outer_ids = AllFaceSets.objects.all()
	for id in all_outer_ids:
		outer_id_arr.append(id.outer_id)
	return outer_id_arr

def GenerateNewOuterId():
	return str(int(time.time()))+''.join(random.choice(string.uppercase) for _ in range(6))


def Update_AllFaces_FaceSet_db(facetoken,new_outerid):
	face_data = AllFaces.objects.get(facetoken = facetoken)
	face_data.faceset_status = 'Y'
	face_data.faceset_outerid = new_outerid
	face_data.save()

def Update_FaceSet_db(faceset):
	faceset_token = faceset['faceset_token']
	outer_id = faceset['outer_id']
	faceset_data = AllFaceSets.objects.get(faceset_token=faceset_token,outer_id=outer_id)
	faceset_data.face_count = faceset['face_count']
	faceset_data.face_tokens['face_tokens'].append(faceset['face_tokens'])
	faceset_data.save()
	
def Insert_FaceSet_db(faceset):
	newfaceset = AllFaceSets()
	newfaceset.faceset_token = faceset['faceset_token']
	facetokens_arr = []
	facetokens_dict = {}
	facetokens_arr.append(faceset['face_tokens'])
	facetokens_dict['face_tokens'] = facetokens_arr
	newfaceset.face_tokens = facetokens_dict
	newfaceset.face_count = faceset['face_count']
	newfaceset.outer_id = faceset['outer_id']
	newfaceset.save()
	
def Reg_DateTime(filepath,type):
	im = Image.open(filepath)
	#0,2,8,20
	#0,0.2,1.2,0 for time
	i = 0
	j = 0.2
	k = 1.2
	l = 0
	enhancer_i = ImageEnhance.Color(im)
	enhancer_i = enhancer_i.enhance(i)
	enhancer_j = ImageEnhance.Brightness(enhancer_i)
	enhancer_j = enhancer_j.enhance(j)
	enhancer_k = ImageEnhance.Contrast(enhancer_j)
	enhancer_k = enhancer_k.enhance(k)
	enhancer_l = ImageEnhance.Sharpness(enhancer_k)
	im = enhancer_l.enhance(l)

	time_str = pytesseract.image_to_string(im)
	# 删除非数字(-)的字符串 
	time_str = re.sub(r'\D', "", time_str)
	if time_str != '':
		time_dig = int(time_str)
		if len(time_str) == 2:
			if type == 'hour':
				if time_dig > 23 or time_dig < 0:
					return None
				else:
					return '%02d'%time_dig
			elif type == 'min' or type == 'sec':
				if time_dig > 59 or time_dig < 0:
					return None
				else:
					return '%02d'%time_dig
			else:
				return None
		else:
			return None
	else:
		return None
def AddDateTime(picpath):
	fixtime_num = 0	
	result = {}
	needfix = AllFaces.objects.filter(pictime='1990-01-01 00:00:00',picpath=picpath)
	for fixdata in needfix:
		getbase = AllFaces.objects.filter(pictime__gt='1990-01-01 00:00:00',picpath=picpath).order_by('snapseq')
		if len(getbase) == 0:
			break
		else:
			fixtime_base = getbase[0]
		t = time.mktime(time.strptime(fixtime_base.pictime.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
		diffsec = 0.0
		diffsec = (fixdata.snapseq - fixtime_base.snapseq) * int(fixdata.snapint) / 1000
		t = t + diffsec
		pic_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))	
		fixdata.pictime = pic_time
		fixdata.save()
		fixtime_num += 1
		
	result['path'] = picpath
	if fixtime_num == 0:
		result['num'] = 'No valid datetime is recognized!'
	else:
		result['num'] = str(fixtime_num)
	return result
