# -*- coding: utf-8 -*-

import urllib2
import urllib
import socket
import sys,json,os,re,time,string,random,math,shutil
import cv2
from PIL import Image,ImageEnhance
import pytesseract
import numpy as np

import django
from __builtin__ import file
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "findface.settings")
django.setup()
from find.models import *

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
f = None
video_results_dir = ''

def savepic(file_path,interval_sec):
    global f,video_results_dir
    f = None
    rst_ctx = ''
    
    new_time = time.strftime('%Y%m%d%H%M%S')
    logpath = os.path.join(os.getcwd(),'log')
    if not os.path.exists(logpath):
        os.mkdir(logpath)
    resultfile = os.path.join(logpath,new_time+'.log')
    f = open(resultfile,'a+')
    rst_ctx = 'The analysis results are as follows:\r\n'
    f.write('%s' % rst_ctx)
    
    #process every videos in folder or only single one video
    if os.path.isdir(file_path):
        video_results_dir = file_path + '_results'
        video_conv_dir = file_path + '_conv'
        HandleAllVideos(video_conv_dir,interval_sec)
        CleanFiles(file_path)
    elif os.path.isfile(file_path):
        fv = file_path.split('\\')[-1]
        root = ('\\').join(file_path.split('\\')[0:-1]) 
        video_results_dir = root + '_results'
        if CheckVideo(fv):    
            HandleSingleVideo(root,fv,interval_sec)
            CleanFiles(root)
    else:
        print 'Please input a valid video path or directory'
        sys.exit()

    #Fix error pics
    #FixPic()
        
    #Add time
    #ADT_result = AddDateTime()

    #Add to faceset
    #ATF_result = [0,0]
    #ATF_result = AddToFaceset(videopath='')
    #newfaceset_num = ATF_result[0] 
    #updfaceset_num = ATF_result[1]
    AddToFaceset(videopath='')
    
    rst_ctx = '*'*100+'\r\n\r\nNotes:\r\n1. Source videos are moved to the directory \'FILEPATH_resluts\' after analysis done.\r\n'
    rst_ctx = rst_ctx+ '2. Snapshots are stored in directory \'FILEPATH_resluts\' for certain days, please check if needed.\r\n'
    f.write('%s' % rst_ctx)
    f.flush()
    f.close()

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
        resp = urllib2.urlopen(req, timeout=6)
        #get response
        qrcont=resp.read()
        face_dict = json.loads(qrcont)
        return face_dict
    except urllib2.HTTPError as e:
        #print "test:::",e.read()
        err_res = json.loads(e.read())
        return err_res
    except urllib2.URLError as e:
        if hasattr(e, 'reason'):
            err_res = {}
            err_res['error_message'] = str(e.reason)[0:200]
            return err_res
    except:
        err_res = {}
        err_res['error_message'] = 'Error in DetectFace()'
        return err_res

def DetectFaceFrame(frame_encode,landmark,attrs):
    face_dict={}
    http_url='https://api-cn.faceplusplus.com/facepp/v3/detect'
    face_token=''
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
    data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
    data.append('Content-Type: %s\r\n' % 'application/octet-stream')
    data.append(frame_encode)
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
        resp = urllib2.urlopen(req, timeout=6)
        #get response
        qrcont=resp.read()
        face_dict = json.loads(qrcont)
        return face_dict
    except urllib2.HTTPError as e:
        #print "test:::",e.read()
        err_res = json.loads(e.read())
        return err_res
    except urllib2.URLError as e:
        if hasattr(e, 'reason'):
            err_res = {}
            err_res['error_message'] = str(e.reason)[0:200]
            return err_res
    except:
        err_res = {}
        err_res['error_message'] = 'Error in DetectFaceFrame()'
        return err_res
        
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
                resp = urllib2.urlopen(req, timeout=6)
                #get response
                qrcont=resp.read()
                qrcont = json.loads(qrcont)
                #print qrcont
                if 'results' in qrcont:
                    if qrcont['results'][0]['confidence'] > score:
                        score = qrcont['results'][0]['confidence']
                        max_outer_id = outer_id
                        max_facetoken = qrcont['results'][0]['face_token']
    
                if score > 90:    #分数大于90直接认定为本人 防止运行太频繁造成QPS爆掉
                    break
    
            except urllib2.HTTPError as e:
                #print e.read()
                result.append(newfaceset_num)
                result.append(updfaceset_num)
                return result
            except urllib2.URLError as e:
                #print e.read()
                result.append(newfaceset_num)
                result.append(updfaceset_num)
                return result
            except:
                result.append(newfaceset_num)
                result.append(updfaceset_num)
                return result
            
        if score != 0 and score > 80:
            #我觉得没必要再compare，这里的分数跟上面search的最优分数应该是一致的(经测试，是一样的）。主要来确定这个score多少分合适
            #comp_result = Compare_2Faces(facetoken,max_facetoken)
            #comp_score = comp_result['confidence']
            faceset_facecount = AllFaceSets.objects.get(outer_id=outer_id).face_count
            #print faceset_facecount
            #设置faceset里面脸的数量上线，防止搜寻时间消耗过大
            if faceset_facecount < 10:
                #添加人脸到分数大于65的faceset
                add_face_result = AddFace(facetoken,max_outer_id)
                if add_face_result:
                    #同步本地faceset
                    Update_FaceSet_db(facetoken,max_outer_id)
                    #更新facetable
                    Update_AllFaces_FaceSet_db(facetoken,max_outer_id)
                    updfaceset_num += 1
                    #print 'Add faceset:', max_outer_id,'|',score
            else:
                #同步本地faceset
                Update_FaceSet_db(facetoken,max_outer_id)
                #更新facetable
                Update_AllFaces_FaceSet_db(facetoken,max_outer_id)
                updfaceset_num += 1
        else:
            new_outer_id = GenerateNewOuterId()
            #在face++新建一个faceset
            new_faceset = CreatFaceSet(facetoken,new_outer_id)
            if new_faceset:
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
        resp = urllib2.urlopen(req, timeout=6)
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
    except urllib2.URLError as e:
        return {}
    except:
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
        resp = urllib2.urlopen(req, timeout=6)
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
    except urllib2.URLError as e:
        return {}
    except:
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
        resp = urllib2.urlopen(req, timeout=6)
        #get response
        qrcont=resp.read()
        qrcont = json.loads(qrcont)
        result['confidence'] = qrcont['confidence']

    except urllib2.HTTPError as e:
        #print e.read()
        pass
    except:
        pass
    return result

def savenewface(facesdata,save_path,save_name,snapseq,snapint,pictime):
    for singleface in facesdata['faces']:
        newface = AllFaces()
        newface.imageid = facesdata['image_id']
        newface.facetoken = singleface['face_token']
        newface.videopath = save_path
        newface.picname = save_name
        newface.pictime = pictime
        newface.snapseq = snapseq
        newface.snapint = snapint
        attrs = singleface['attributes']
        newface.gender = attrs['gender']['value']
        newface.age = attrs['age']['value']
        newface.smile = attrs['smile']
        newface.headpose = attrs['headpose']
        newface.blur = attrs['blur']
        newface.eyestatus = attrs['eyestatus']
        newface.emotion = attrs['emotion']
        newface.facequality = attrs['facequality']
        newface.ethnicity = attrs['ethnicity']['value']
        newface.male_score = attrs['beauty']['male_score']
        newface.female_score = attrs['beauty']['female_score']
        newface.mouthstatus = attrs['mouthstatus']
        newface.eyegaze = attrs['eyegaze']
        newface.skinstatus = attrs['skinstatus']
        newface.mostlike_score = (newface.blur['blurness']['threshold'] - newface.blur['blurness']['value']) * 0.5 + \
                                (newface.facequality['value'] - newface.facequality['threshold']) * 0.5
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
        resp = urllib2.urlopen(req, timeout=6)
        #get response
        qrcont=resp.read()
        face_dict = json.loads(qrcont)
        return face_dict
    except urllib2.HTTPError as e:
        return e.read()
    except:
        pass
        

#def fixpic(request): call this directly from savepic
def FixPic():
    try_limit = 10
    try_count = 0
    #check if there is still err pics to fix        
    while ErrFaces.objects.filter(fixstatus='N').count() > 0 and try_count <= try_limit:
        try_count += 1
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
                        ErrFaces.objects.filter(id=fixdata.id).delete()
                        if not os.path.exists(os.path.splitext(fixdata.picpath)[0]+'_hour'+os.path.splitext(fixdata.picpath)[1]):
                            os.remove(fixdata.picpath)
                    elif len(face_data['faces']) > 0:
                        pic_time = None
                        fix_root = ('\\').join(fixdata.picpath.split('\\')[:-2])
                        fix_name = ('_').join(fixdata.picpath.split('\\')[-2].split('_')[2:])
                        fix_path = os.path.join(fix_root,fix_name)
                        pic_name = fixdata.picpath.split('\\')[-1]
                        savenewface(face_data,fix_path,pic_name,fixdata.snapseq,fixdata.snapint,pic_time)
                        errface = ErrFaces.objects.get(id=fixdata.id)
                        errface.fixmsg = 'Faces detected'
                        errface.fixstatus = 'Y'
                        errface.save()
            else:
                ErrFaces.objects.filter(id=fixdata.id).delete()
            save_pre_picpath = fixdata.picpath
    
def AddDateTime():
    #add time
    ADT_result = []
    fixtime_data = AllFaces.objects.filter(pictime__isnull=True).values('videopath').distinct()
    for i in fixtime_data:
        ADT_result += CalDateTime(i['videopath'])
    return ADT_result

#def addtofaceset(request): call this directly from savepic
def AddToFaceset(videopath):
    result = [0,0]
    try_limit = 5
    try_count = 0
    while try_count <= try_limit:
        try_count += 1
        #print videopath,': ', try_count, 'time'
        if videopath == '':
            data_add = AllFaces.objects.filter(faceset_status='N')
        else:
            data_add = AllFaces.objects.filter(faceset_status='N',videopath=videopath)
        if data_add:
            for face_add in data_add:
                all_outer_id = GetOuterId()
                facetoken = face_add.facetoken
                searchresult = SearchFaceSet(facetoken,all_outer_id)
                result[0] += searchresult[0]
                result[1] += searchresult[1]
        else:
            break
        
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

def Update_FaceSet_db(facetoken,max_outer_id):
    faceset_data = AllFaceSets.objects.get(outer_id=max_outer_id)
    faceset_data.face_tokens['face_tokens'].append(facetoken)
    faceset_data.face_count += 1
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
    
def CalDateTime(videopath):
    fixtime_num = 0    
    result_list = []
    #get different snapint
    needfix_intsec = AllFaces.objects.filter(pictime__isnull=True,videopath=videopath).values('snapint').distinct()
    for dataintsec in needfix_intsec:
        result = {}
        fixtime_base = {}
        #get data which need to add datetime
        needfix = AllFaces.objects.filter(pictime__isnull=True,videopath=videopath,snapint=dataintsec['snapint'])
        for fixdata in needfix:
            if not fixtime_base:
                getbase = AllFaces.objects.filter(pictime__isnull=False,videopath=videopath,snapint=fixdata.snapint).order_by('snapseq')
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
            
        result['videopath'] = videopath
        result['intsec'] = dataintsec['snapint']
        if fixtime_num == 0:
            result['num'] = 'No valid datetime is recognized!'
        else:
            result['num'] = str(fixtime_num)
        result_list.append(result)
    return result_list
    
def HandleAllVideos(file_path,interval_sec):
    for root,dirs,files in os.walk(file_path):
        for file in files:
            if CheckVideo(file):
                file_fullpath = os.path.join(root,file)
                #print snapshot_dir
                #print file_fullpath
                HandleSingleVideo(root,file,interval_sec)
            else:
                pass             
        for dir in dirs:
            HandleAllVideos(dir,interval_sec)

def HandleSingleVideo(root,fv,interval_sec):
    global SCALE_LANDMARK,SCALE_ATTRSs,f,video_results_dir
    time_start = time.time()
    rst_txt = ''
    pictime_base = []
    seqno = int(0)
    count = int(0)
    timeF = int(0)
    fullfile = os.path.join(root,fv)
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
    #snapshot_dir = os.path.join(root,'snapshots_') + str(interval_sec) + '_' + fv
    snapshot_dir = os.path.join(video_results_dir,'snapshots_') + str(interval_sec) + '_' + fv
    if rval and not os.path.exists(snapshot_dir):
        os.makedirs(snapshot_dir)
       
    timeF = int(interval_sec) * int(framerate)  #视频帧计数间隔频率  
    while rval and count <= framelimit:   #循环读取视频帧  
        #print 'test'
        base_flag = False
        if count % timeF == 0:  #每隔timeF帧进行存储操作  
            seqno = int(count / timeF)
            #print seqno
            pic_name = str(count) + '.jpg'
            img_path = os.path.join(snapshot_dir,pic_name)
            #cv2.imwrite(img_path,frame) #存储为图像  
            if len(pictime_base) < 2:
                img_hour = frame[80:134,760:838]
                img_min = frame[80:134,855:933]
                img_sec = frame[80:134,950:1028]
                img_hour_name = str(count) + '_hour' +'.jpg'
                img_min_name = str(count) + '_min' +'.jpg'
                img_sec_name = str(count) + '_sec' +'.jpg'
                img_hour_path = os.path.join(snapshot_dir,img_hour_name)
                img_min_path = os.path.join(snapshot_dir,img_min_name)
                img_sec_path = os.path.join(snapshot_dir,img_sec_name)
                cv2.imwrite(img_hour_path,img_hour)   
                cv2.imwrite(img_min_path,img_min)   
                cv2.imwrite(img_sec_path,img_sec)   
                pictime_hour = RegDateTime(img_hour_path, 'hour')
                pictime_min = RegDateTime(img_min_path, 'min')
                pictime_sec = RegDateTime(img_sec_path, 'sec')
                #2018-05-16 13:53:51.401192
                if pictime_hour != None and pictime_min != None and pictime_sec != None:
                    base_flag = True
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
            
            #face_data = DetectFace(img_path,SCALE_LANDMARK,SCALE_ATTRS)
            img_encode = cv2.imencode('.jpg', frame)[1]
            data_encode = np.array(img_encode)
            frame_encode = data_encode.tostring()
            face_data = DetectFaceFrame(frame_encode,SCALE_LANDMARK,SCALE_ATTRS)
            if face_data:
                if 'error_message' in face_data:
                    cv2.imwrite(img_path,frame) #存储为图像  
                    newerr = ErrFaces()
                    newerr.picpath = img_path
                    #print face_data
                    newerr.errmsg = face_data['error_message']
                    newerr.fixstatus = 'N'
                    newerr.snapseq = str(seqno)
                    newerr.snapint = interval_sec
                    newerr.save()
                elif len(face_data['faces']) == 0:
                    if base_flag:
                        #os.remove(img_path)
                        cv2.imwrite(img_path,frame) #存储为图像  
                    '''not needed
                    newerr = ErrFaces()
                    newerr.picpath = img_path
                    newerr.errmsg = 'No faces detected'
                    newerr.snapseq = str(seqno)
                    newerr.snapint = interval_sec
                    newerr.save()
                    '''
                elif len(face_data['faces']) > 0:
                    cv2.imwrite(img_path,frame) #存储为图像 
                    if len(pictime_base) > 0:
                        t = time.mktime(time.strptime(pictime_base[0]['time'], "%Y-%m-%d %H:%M:%S"))
                        diffsec = 0.0
                        diffsec = (seqno - pictime_base[0]['seqno']) * int(interval_sec)
                        t = t + diffsec
                        pic_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
                    else:
                        pic_time = None
                    savenewface(face_data,fullfile,pic_name,seqno,interval_sec,pic_time)
        count = count + timeF
        if vc.set(1, count): #set 0-based index of the frame to be decoded/captured next.
            rval, frame = vc.read()  
            cv2.waitKey(1)  
        else:
            rval = False
    vc.release()  
    
    #Fix error pics
    FixPic()
    
    rst_txt = '*'*100 + '\r\n'
    rst_txt = rst_txt + fv +', analyzed every ' + str(interval_sec) + ' seconds:\r\n'    
    face_num = AllFaces.objects.filter(videopath=fullfile,snapint=interval_sec).count()
    #Add to faceset and output the result
    ATF_result = [0,0]
    ATF_result = AddToFaceset(fullfile)
    newfaceset_num = ATF_result[0] 
    updfaceset_num = ATF_result[1]
    rst_txt = rst_txt+'Detected '+str(face_num)+' faces, created '+str(newfaceset_num)+' facesets, updated '+str(updfaceset_num)+' facesets.\r\n'
    f.write(rst_txt)
    f.flush()
    
    #output Recognized time
    if len(pictime_base) > 0:
        rst_txt = 'Recognized time: '
        for i in pictime_base:
            rst_txt = rst_txt + 'SeqNo. '+str(i['seqno'])+', '+i['time']+'; '
        rst_txt = rst_txt + '\r\n'
        f.write(rst_txt)
        f.flush()
    
    #verify the time and output result
    if len(pictime_base) == 2:
        t0 = time.mktime(time.strptime(pictime_base[0]['time'], "%Y-%m-%d %H:%M:%S"))
        t1 = time.mktime(time.strptime(pictime_base[1]['time'], "%Y-%m-%d %H:%M:%S"))
        reg_diff = t1 - t0
        exp_diff = (pictime_base[1]['seqno'] - pictime_base[0]['seqno']) * int(interval_sec)
        if abs(exp_diff - reg_diff) <= 2:
            pass
        else:
            rst_txt = 'Probably have a wrong detected time, please check!\r\n'
            f.write(rst_txt)
            f.flush()
    
    #Add datetime and output the result
    CDT_result = CalDateTime(fullfile)
    for res in CDT_result:
        if not res['num'].isdigit():
            rst_txt = 'No date time recognized, when analyzed every '+str(res['intsec'])+' seconds, please check!\r\n'
            f.write(rst_txt)
            f.flush()
        
    time_end = time.time()
    cost_time = ChangeTime(time_end-time_start)
    rst_txt = 'Cost ' + cost_time +'.\r\n'
    f.write(rst_txt)
    f.flush()
    shutil.move(fullfile,video_results_dir)
            
def CheckVideo(f):
    if f.split('.')[-1] not in SUPPORTED_FORMATS:
        return False
    else:
        return True
    
def ChangeTime(allTime):
    day = 24*60*60
    hour = 60*60
    min = 60
    if allTime <60:        
        return  "%d secs"%math.ceil(allTime)
    elif  allTime > day:
        days = divmod(allTime,day) 
        return "%d days, %s"%(int(days[0]),ChangeTime(days[1]))
    elif allTime > hour:
        hours = divmod(allTime,hour)
        return '%d hours, %s'%(int(hours[0]),ChangeTime(hours[1]))
    else:
        mins = divmod(allTime,min)
        return "%d mins, %d sec"%(int(mins[0]),math.ceil(mins[1]))
    
def CleanFiles(path):
    #CLean empty folders under param path           
    for root,dirs,files in os.walk(path,False):
        for dir in dirs:
            tempdir = os.path.join(root,dir)
            if not os.listdir(tempdir):
                os.rmdir(tempdir)
            else:
                CleanFiles(tempdir)
                
if __name__ == '__main__': 
    if len(sys.argv) == 3:
        filepath = sys.argv[1]
        intsec = sys.argv[2]
        print filepath,intsec
        if os.path.split(filepath)[1] == '':
            print "Please specify a video folder, not just a disk driver."
            sys.exit()
        else:
            savepic(filepath,intsec)
    else:
        print "Only accept 2 parameters:\'FILEPATH INETERVALSECOND\' "
        sys.exit()
