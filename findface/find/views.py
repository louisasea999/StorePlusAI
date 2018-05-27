# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
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
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from find.models import AllFaces,ErrFaces,AllFaceSets
#from findface.settings import STATIC_URL
#from json.decoder import errmsg
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

SCALE_LANDMARK = '0'
SCALE_ATTRS = 'gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus'
SUPPORTED_FORMATS = ['mp4','m4v','mkv','webm','mov','avi','wmv','mpg','flv',]

def getmain(request):
	return render(request,"test2.html")

def savepic(request):
	result_dict = {}
	rst_ctx = ''
	handlevideos = []
	validfacepic_num = 0
	newfaceset_num = 0
	updfaceset_num = 0
	
	interval_sec = int(request.POST["intsec"])
	file_path = request.POST["filepath"]
	
	if os.path.isdir(file_path):
		handlevideos = HandleAllVideos(file_path,interval_sec)
	elif os.path.isfile(file_path):
		f = file_path.split('\\')[-1]
		root = ('\\').join(file_path.split('\\')[0:-1]) 
		snapshot_dir = os.path.join(root,'snapshots_') + f + '_' + str(interval_sec)
		if CheckVideo(f):
			HandleSingleVideo(root,f,interval_sec)
			handlevideos.append({'snapshot_dir':snapshot_dir,'file_fullpath':file_path})
	
	try_limit = 20
	try_count = 0
	#Fix error pics
	fixpic_status = True
	while fixpic_status and try_count <= try_limit:
		fixpic_status = FixPic()
		try_count += 1
		
	#Add time
	ADT_result = AddDateTime()

	#Add to faceset
	ATF_result = [0,0]
	ATF_result = AddToFaceset()
	newfaceset_num = ATF_result[0] 
	updfaceset_num = ATF_result[1]
	
	if len(handlevideos) > 0:
		if len(handlevideos) == 1:
			rst_ctx = 'Analyzed 1 video, details as below:\r\n'
		if len(handlevideos) > 1:
			rst_ctx = 'Analyzed '+str(len(handlevideos))+' videos, details as below:\r\n'
		for i in handlevideos:
			num = AllFaces.objects.filter(picpath=i['snapshot_dir']).count()
			rst_ctx = rst_ctx + i['file_fullpath'] +': ' + str(num) + ' valid face pics.\r\n'
		rst_ctx += '\r\n'
	
	if newfaceset_num != 0 or updfaceset_num != 0:
		rst_ctx = rst_ctx+'Created '+str(newfaceset_num)+' facesets.\r\n' + 'Updated '+str(updfaceset_num)+' facesets.\r\n'
		rst_ctx += '\r\n'
	
	for res in ADT_result:
		if not res['num'].isdigit():
			rst_ctx = rst_ctx + 'No date time recognized for the video ' + res['path'] + '\r\n'
			
	result_dict['data_info'] = rst_ctx
	result_info = json.dumps(result_dict)
	return HttpResponse(result_info,content_type="application/json")
	
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
		resp = urllib2.urlopen(req, timeout=20)
		#get response
		qrcont=resp.read()
		face_dict = json.loads(qrcont)
		return face_dict
	except urllib2.HTTPError as e:
		#print "test:::",e.read()
		return e.read()
		
def SearchFaceSet(facetoken,all_outer_id):
	result = []
	max_outer_id = ''
	max_facetoken = ''
	score = 0
	http_url_create='https://api-cn.faceplusplus.com/facepp/v3/search'
	newfaceset_num = 0
	updfaceset_num = 0
	if len(all_outer_id) == 0:  #to create a new faceset initially
		new_outer_id = GenerateNewOuterId()
		#在face++新建一个faceset
		new_faceset = CreatFaceSet(facetoken,new_outer_id)
		if new_faceset:
			#同步本地faceset
			Insert_FaceSet_db(new_faceset)
			#更新facetable
			Update_AllFaces_FaceSet_db(facetoken,new_faceset['outer_id'])
			newfaceset_num += 1
			#print 'New faceset:', new_faceset['outer_id']
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
				#print e.read()
				result.append(newfaceset_num)
				result.append(updfaceset_num)
				return result
		if score != 0 and score > 65:
			#我觉得没必要再compare，这里的分数跟上面search的最优分数应该是一致的(经测试，是一样的）。主要来确定这个score多少分合适
			#comp_result = Compare_2Faces(facetoken,max_facetoken)
			#comp_score = comp_result['confidence']
			#添加人脸到分数大于65的faceset
			add_face_result = AddFace(facetoken,max_outer_id)
			if add_face_result:
				#同步本地faceset
				Update_FaceSet_db(add_face_result)
				#更新facetable
				Update_AllFaces_FaceSet_db(facetoken,max_outer_id)
				updfaceset_num += 1
				#print 'Add to faceset:', max_outer_id,'|',score
		else:
			new_outer_id = GenerateNewOuterId()
			#在face++新建一个faceset
			new_faceset = CreatFaceSet(facetoken,new_outer_id)
			#同步本地faceset
			Insert_FaceSet_db(new_faceset)
			#更新facetable
			Update_AllFaces_FaceSet_db(facetoken,new_faceset['outer_id'])
			newfaceset_num += 1
			#print 'New faceset:', new_faceset['outer_id'],'|',score
	
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
	    #print e.read()
	    return {}
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
	    #print e.read()
	    return {}
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
	    #print e.read()
	    pass
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

#def fixpic(request): call this directly from savepic
def FixPic():
	pic_time = None
	global SCALE_LANDMARK,SCALE_ATTRS
	needfix = ErrFaces.objects.filter(fixstatus='N').order_by('picpath')
	save_pre_picpath = ''
	
	for fixdata in needfix:
		if save_pre_picpath != fixdata.picpath:
			face_data = DetectFace(fixdata.picpath,SCALE_LANDMARK,SCALE_ATTRS)
			if face_data:
				if 'error_message' in face_data:
					pass
				elif len(face_data['faces']) == 0:
					'''not needed
					errface = ErrFaces.objects.get(id=fixdata.id)
					errface.errmsg = 'No faces detected'
					errface.fixstatus = 'Y'
					errface.save()
					'''
					pass
				elif len(face_data['faces']) > 0:
					pic_time = None
					fix_path = ('\\').join(fixdata.picpath.split('\\')[:-1])
					fix_name = fixdata.picpath.split('\\')[-1]
					savenewface(face_data,fix_path,fix_name,fixdata.snapseq,fixdata.snapint,pic_time)
					errface = ErrFaces.objects.get(id=fixdata.id)
					errface.errmsg = 'Faces detected'
					errface.fixstatus = 'Y'
					errface.save()
		else:
			ErrFaces.objects.filter(id=fixdata.id).delete()
		save_pre_picpath = fixdata.picpath
		
	#check if there is still err pics to fix		
	if ErrFaces.objects.filter(fixstatus='N').count() > 0:
		return True
	else:
		return False
	
def AddDateTime():
	#add time
	ADT_result = []
	fixtime_data = AllFaces.objects.filter(pictime__isnull=True).values('picpath').distinct()
	for i in fixtime_data:
		ADT_result.append(CalDateTime(i['picpath']))
	return ADT_result

#def addtofaceset(request): call this directly from savepic
def AddToFaceset():
	data_add = AllFaces.objects.filter(faceset_status='N')
	result = [0,0]
	for face_add in data_add:
		all_outer_id = GetOuterId()
		facetoken = face_add.facetoken
		searchresult = SearchFaceSet(facetoken,all_outer_id)
		result[0] += searchresult[0]
		result[1] += searchresult[1]

	#result_info = str(result[0]) + ' new facesets are created; ' + str(result[1]) + ' facesets are updated!'
	#return HttpResponse(result_info,content_type="text/plain")
	return result

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
	
def RegDateTime(filepath,type):
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
	
def CalDateTime(picpath):
	fixtime_num = 0	
	result = {}
	needfix = AllFaces.objects.filter(pictime__isnull=True,picpath=picpath)
	for fixdata in needfix:
		getbase = AllFaces.objects.filter(pictime__isnull=False,picpath=picpath).order_by('snapseq')
		if len(getbase) == 0:
			break
		else:
			fixtime_base = getbase[0]
		t = time.mktime(time.strptime(fixtime_base.pictime.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
		diffsec = 0.0
		diffsec = (fixdata.snapseq - fixtime_base.snapseq) * int(fixdata.snapint)
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
	
def HandleAllVideos(file_path,interval_sec):
	videos_list = []
	for root,dirs,files in os.walk(file_path):
		for file in files:
			videos_dict = {}
			if CheckVideo(file):
				snapshot_dir = os.path.join(root,'snapshots_') + file + '_' + str(interval_sec)
				file_fullpath = os.path.join(root,file)
				#print snapshot_dir
				#print file_fullpath
				videos_dict['snapshot_dir'] = snapshot_dir
				videos_dict['file_fullpath'] = file_fullpath
				videos_list.append(videos_dict)
				HandleSingleVideo(root,file,interval_sec)
			else:
				pass             
		for dir in dirs:
			videos_list += HandleAllVideos(dir,interval_sec)
	return videos_list

def HandleSingleVideo(root,f,interval_sec):
	global SCALE_LANDMARK,SCALE_ATTRSs
	pictime_base = []
	seqno = 0
	count = 0
	fullfile = os.path.join(root,f)
	vc = cv2.VideoCapture(fullfile) #读入视频文件  
	framerate = int(vc.get(5))  #Get video frame rate
	framelimit = int(vc.get(7))
	#print fullfile
	#print framerate
	if vc.isOpened():      #判断是否正常打开  
		rval , frame = vc.read()  
		#print 'open'
	else:  
		rval = False  
		
	#create snapshot folder
	snapshot_dir = os.path.join(root,'snapshots_') + f + '_' + str(interval_sec)
	if rval and not os.path.exists(snapshot_dir):
		os.makedirs(snapshot_dir)
		
	timeF = int(framerate * interval_sec)  #视频帧计数间隔频率  
	#print timeF
	while rval and count <= framelimit:   #循环读取视频帧  
		#print 'test'
		if count % timeF == 0:  #每隔timeF帧进行存储操作  
			seqno = count / timeF
			pic_name = str(count) + '.jpg'
			img_path = os.path.join(snapshot_dir,pic_name)
			cv2.imwrite(img_path,frame) #存储为图像  
			if len(pictime_base) < 2:
				#copyimage = cv2.imread(img_path)
				img_hour = frame[80:134,760:838]
				img_min = frame[80:134,855:933]
				img_sec = frame[80:134,950:1028]
				img_hour_name = str(count) + '_hour' +'.jpg'
				img_min_name = str(count) + '_min' +'.jpg'
				img_sec_name = str(count) + '_sec' +'.jpg'
				img_hour_path = os.path.join(snapshot_dir,img_hour_name)
				img_min_path = os.path.join(snapshot_dir,img_min_name)
				img_sec_path = os.path.join(snapshot_dir,img_sec_name)
				cv2.imwrite(img_hour_path,img_hour) #存储为图像  
				cv2.imwrite(img_min_path,img_min) #存储为图像  
				cv2.imwrite(img_sec_path,img_sec) #存储为图像  
				pictime_hour = RegDateTime(img_hour_path, 'hour')
				pictime_min = RegDateTime(img_min_path, 'min')
				pictime_sec = RegDateTime(img_sec_path, 'sec')
				#2018-05-16 13:53:51.401192
				if pictime_hour != None and pictime_min != None and pictime_sec != None:
					pictime = '2018-04-01 ' + str(pictime_hour) + ':' + str(pictime_min) + ':' + str(pictime_sec)
					base_dict = {}
					base_dict['seqno'] = seqno
					base_dict['time'] = pictime
					pictime_base.append(base_dict)
					#print str(pictime)
				else:
					#print 'delete ',img_hour_path
					os.remove(img_hour_path)
					os.remove(img_min_path)
					os.remove(img_sec_path)
					
			face_data = DetectFace(img_path,SCALE_LANDMARK,SCALE_ATTRS)
			if face_data:
				if 'error_message' in face_data:
					face_data = json.loads(face_data)
					newerr = ErrFaces()
					newerr.picpath = img_path
					newerr.errmsg = face_data['error_message']
					newerr.fixstatus = 'N'
					newerr.snapseq = str(seqno)
					newerr.snapint = interval_sec
					newerr.save()
				elif len(face_data['faces']) == 0:
					pass
					'''not needed
					newerr = ErrFaces()
					newerr.picpath = img_path
					newerr.errmsg = 'No faces detected'
					newerr.snapseq = str(seqno)
					newerr.snapint = interval_sec
					newerr.save()
					'''
				elif len(face_data['faces']) > 0:
					if len(pictime_base) > 0:
						t = time.mktime(time.strptime(pictime_base[0]['time'], "%Y-%m-%d %H:%M:%S"))
						diffsec = 0.0
						diffsec = (seqno - pictime_base[0]['seqno']) * int(interval_sec)
						t = t + diffsec
						pic_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
					else:
						pic_time = None
					savenewface(face_data,snapshot_dir,pic_name,seqno,interval_sec,pic_time)
		count = count + timeF
		if vc.set(1, count): #set 0-based index of the frame to be decoded/captured next.
			rval, frame = vc.read()  
			cv2.waitKey(1)  
		else:
			rval = False
			
	vc.release()  
	print pictime_base

def CheckVideo(f):
	if f.split('.')[-1] not in SUPPORTED_FORMATS:
		return False
	else:
		return True
