# -*- coding: utf-8 -*-
from PIL import Image,ImageEnhance
import pytesseract,sys
import os,re,time,datetime,shutil
#上面都是导包，只需要下面这一行就能实现图片文字识别
#os.chdir('C:\Users\hanmi\AppData\Roaming\Python\Python27\site-packages\pytesseract')
#im = Image.open('20180424135047.png')
#bg = Image.new("RGB",im.size,(255,255,255))
#bg.paste(im,im)
#print im
#text=pytesseract.image_to_string(bg,lang='chi_sim')
#text=pytesseract.image_to_string(Image.open('Capture.PNG'),lang='chi_sim')
#print text

#img_name = '20180430170248.PNG'
#img_name = '20180430170709.PNG'
'''
img_name = 'C:\\Users\\hanmi\\Desktop\\Capture.PNG'

im = Image.open(img_name)
#0,2,8,20
colorscale = 0.2
brightscale = 0.2
contrastscale = 0.2
sharpnessscale = 5

color_max = 0
bright_max = 0.2
contrast_max = 3
sharpness_max = 0
#0,0.2,1.4,0 for hour
#0,0.2,0.2-0.8,0 for min
#0.0.2,0.2-1.4,0 for sec

i = 0
j = 0.2
k = 1.2
l = 0
while i <= color_max:
    enhancer_i = ImageEnhance.Color(im)
    enhancer_i = enhancer_i.enhance(i)
    while j <= bright_max:
        enhancer_j = ImageEnhance.Brightness(enhancer_i)
        enhancer_j = enhancer_j.enhance(j)
        while k <= contrast_max:
            enhancer_k = ImageEnhance.Contrast(enhancer_j)
            enhancer_k = enhancer_k.enhance(k)
            while l <= sharpness_max:
                enhancer_l = ImageEnhance.Sharpness(enhancer_k)
                im = enhancer_l.enhance(l)
                if pytesseract.image_to_string(im):
                    print pytesseract.image_to_string(im),'|| i:',i,',j:',j,',k:',k,',l:',l
                l += sharpnessscale
            k += contrastscale
            l = 0.0
        j += brightscale
        k = 0.0
        l = 0.0
    i += colorscale
    j = 0.0
    k = 0.0
    l = 0.0
    
time_str = pytesseract.image_to_string(im)
# 删除非数字(-)的字符串 
time_str = re.sub(r'\D', "", time_str)
print time_str
'''
'''
time1 = time.time()
print time1
print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time1))
now_time = datetime.datetime.now()  
#当前时间加半小时  
yes_time = now_time + datetime.timedelta(hours=+0.5)  
print now_time

a = '2016-11-04 15:29:58'
print a
t = time.mktime(time.strptime(a, "%Y-%m-%d %H:%M:%S"))
print t
t = t + 10.234
print t
b = time.localtime(t)
c = time.strftime("%Y-%m-%d %H:%M:%S", b)
print c

'''

'''
import cv2  
         
vc = cv2.VideoCapture('C:\\Users\\hanmi\\eclipse-workspace\\fileforfindface\\4.mp4') #读入视频文件  
c=1  
i = 0
while i < 20:
    print i,vc.get(i)
    i+=1
framerate = vc.get(5) 
intsec = 4

if vc.isOpened(): #判断是否正常打开  
    rval , frame = vc.read()  
else:  
    rval = False  
  
timeF = framerate * intsec  #视频帧计数间隔频率  

while rval:   #循环读取视频帧  
    vc.set(1,1000)
    c = vc.get(1)
    rval, frame = vc.read()  
    if(c%timeF == 0): #每隔timeF帧进行存储操作  
        print c
        print timeF
        print c/timeF
        imgpath = 'C:\\Users\\hanmi\\eclipse-workspace\\findface\\image\\'
        cv2.imwrite(imgpath +str(c) + '.jpg',frame) #存储为图像  
        copyimage = cv2.imread(imgpath +str(c) + '.jpg')
        img_hour = copyimage[80:134,760:838]
        img_min = copyimage[80:134,855:933]
        img_sec = copyimage[80:134,950:1028]
        cv2.imwrite(imgpath +str(c) + '_hour' +'.jpg',img_hour) #存储为图像  
        cv2.imwrite(imgpath +str(c) + '_min' +'.jpg',img_min) #存储为图像  
        cv2.imwrite(imgpath +str(c) + '_sec' +'.jpg',img_sec) #存储为图像  
    c = c + 1  
    cv2.waitKey(1)  
vc.release()  
'''

file_path = r'4.mp4' 
#file_path = 'C:d'
#f = ('_').join(file_path.split('\\')[-2].split('_')[2:])
root = ('\\').join(file_path.split('\\')[0:-2]) 
print os.path.splitext(file_path)

'''
print os.path.dirname(file_path)
print os.path.isdir(file_path)
print os.path.isfile(file_path)
print os.path.normcase(file_path)
print os.path.isabs(file_path)
print os.path.splitdrive(file_path)
print file_path.split('\\')[-1]
print os.path.join(root,f)
print root
print os.path.ismount(file_path)
print os.path.splitunc(file_path)
print os.path.split(file_path)
print os.path.splitext(file_path)
print os.path.splitext(file_path)[0]+'_hour'+os.path.splitext(file_path)[1]
print os.path.basename(file_path)
a = []
a.append(None)
if None:
    print len(a)
#print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))
'''
'''
import urllib2
import urllib
import sys,json

key = "cY2YOwFKwF_c9yu4nnBruTgBvjT_9Tb1"
secret = "iMMYMgYt2cJu25-skaf0oOiRnZpum9rX"
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
    
print recognize_datetime('C:\\Users\\hanmi\\Desktop\\Capture.PNG')
'''

#shutil.move(r'C:\Users\hanmi\eclipse-workspace\fileforfindface\4.mp4',r'C:\Users\hanmi\eclipse-workspace\fileforfindface_done')
#coding:utf8
import time
import math
        
def changeTime(allTime):
    day = 24*60*60
    hour = 60*60
    min = 60
    if allTime <60:        
        return  "%d sec"%math.ceil(allTime)
    elif  allTime > day:
        days = divmod(allTime,day) 
        return "%d days, %s"%(int(days[0]),changeTime(days[1]))
    elif allTime > hour:
        hours = divmod(allTime,hour)
        return '%d hours, %s'%(int(hours[0]),changeTime(hours[1]))
    else:
        mins = divmod(allTime,min)
        return "%d mins, %d sec"%(int(mins[0]),math.ceil(mins[1]))
def CleanFiles(path):
    #CLean empty files and folders under param path           
    for root,dirs,files in os.walk(path,False):
        for dir in dirs:
            tempdir = os.path.join(root,dir)
            if not os.listdir(tempdir):
                os.rmdir(tempdir)
            else:
                CleanFiles(tempdir)
        
stars = '*' * 100
print stars
time_start = time.time()
#os.popen3('C:/ffmpeg/bin/ffmpeg.exe -i C:/Users/hanmi/eclipse-workspace/fileforfindface_results/1-origin.mp4 -y -r 25 C:/Users/hanmi/eclipse-workspace/fileforfindface_results/test-25f.avi')
#os.popen3('C:/ffmpeg/bin/ffmpeg.exe -i C:/Users/hanmi/eclipse-workspace/fileforfindface_results/1-origin.mp4 -r 0.25 c:/test/foo-%03d.jpeg')
#os.popen3('C:/ffmpeg/bin/ffmpeg.exe -i C:/Users/hanmi/eclipse-workspace/fileforfindface_results/4.mp4 -vframes 30 -y -f gif C:/a.gif')
#CleanFiles(r'C:\Users\hanmi\eclipse-workspace\fileforfindface')
time_end = time.time()
print changeTime(time_end-time_start)


class CustomError(Exception):
    def __init__(self,ErrorInfo):
        #super().__init__(self) #初始化父类,python3
        #Exception.__init__(self) #初始化父类,python2.7 方法1
        super(CustomError, self).__init__(); ##初始化父类,python2.7 方法2
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo
    def mytest(self):
        return 'test'
if 1 == 2:
    try:
        raise CustomError('客户异常')
        #raise CustomError.mytest()
    except CustomError as e:
        print(e)


import urllib2 
url='http://www.facebook.com/' 
fails = 0 
while True: 
    try: 
        if fails >= 0: 
            break 
        req = urllib2.Request(url) 
        response = urllib2.urlopen(req, None, 3) 
        print 'test'
        page = response.read() 
    except urllib2.HTTPError as e:
        fails += 1 
        print e
    except urllib2.URLError as e:
        fails += 1 
        print e
        print '网络连接出现问题, 正在尝试再次请求: ', fails 
    else: 
        break
    
if 1 == 2:
    try:
        1 / 0
    except Exception as e:
        '''异常的父类，可以捕获所有的异常'''
        print "0不能被除"
    else:
        '''保护不抛出异常的代码'''
        print "没有异常"
    finally:
        print "最后总是要执行我"
    
    
def try_exception(num):
  try:
    return int(num)
  except ValueError, arg:
    print arg,"is not a number"
  else:
    print "this is a number inputs"
#try_exception('123')


#自定义异常 需要继承Exception
class MyException(Exception):
    def __init__(self, *args):
        self.args = args
#raise MyException('爆出异常吧哈哈')
#常见做法定义异常基类,然后在派生不同类型的异常
class loginError(MyException):
    def __init__(self, code = 100, message = 'message:登录异常', args = ('args:登录异常',)):
        self.args = args
        self.message = message
        self.code = code
class loginoutError(MyException):
    def __init__(self):
        self.args = ('退出异常',)
        self.message = '退出异常'
        self.code = 200
#raise loginError() # 这里突然返现 raise引发的异常将中断程序
#
if 1 ==2 :
    try:
        raise loginError()
    except loginError as e:
        print(e) #输出异常
        print(e.code) #输出错误代码
        print(e.message)#输出错误信息
    

class Cat:
    """定义了一个Cat类"""
    #初始化对象
    def __init__(self, new_name, new_age):
        self.name = new_name
        self.age = new_age
    def __str__(self):
        return "%s的年龄是:%d"%(self.name, self.age)
    #方法
    def eat(self):
        print("猫在吃鱼....")
    def drink(self):
        print("猫正在喝kele.....")
    def introduce(self):
        print("%s的年龄是:%d"%(self.name, self.age))
#创建一个对象
if 1==2:
    tom = Cat("汤姆", 40)
    lanmao = Cat("蓝猫", 10)
    print(tom)
    print(lanmao)
    tom.eat()
    
'''
def deco(func):
    startTime = time.time()
    func()
    endTime = time.time()
    msecs = (endTime - startTime)*1000
    print("time is %d ms" %msecs)
def func():
    print("hello")
    time.sleep(1)
    print("world")
'''
if 1==2:
    f = func
    deco(f)#只有把func()或者f()作为参数执行，新加入功能才会生效
    print("f.__name__ is",f.__name__)#f的name就是func()
    #func()
'''
def deco(func):
    def wrapper():
        startTime = time.time()
        func()
        endTime = time.time()
        msecs = (endTime - startTime)*1000
        print("time is %d ms" %msecs)
    return wrapper
@deco
def func():
    print("hello")
    time.sleep(1)
    print("world")
'''
if 1==2:
    f = func #这里f被赋值为func，执行f()就是执行func()
    f()
'''
#带有参数的装饰器
def deco(func):
    def wrapper(a,b):
        startTime = time.time()
        func(a,b)
        endTime = time.time()
        msecs = (endTime - startTime)*1000
        print("time is %d ms" %msecs)
    return wrapper
@deco
def func(a,b):
    print("hello，here is a func for add :")
    time.sleep(1)
    print("result is %d" %(a+b))
'''
if 1==2:
    f = func
    f(3,4)
    #func()
'''
#带有不定参数的装饰器
def deco(func):
    def wrapper(*args, **kwargs):
        startTime = time.time()
        func(*args, **kwargs)
        endTime = time.time()
        msecs = (endTime - startTime)*1000
        print("time is %d ms" %msecs)
    return wrapper
@deco
def func(a,b):
    print("hello，here is a func for add :")
    time.sleep(1)
    print("result is %d" %(a+b))
@deco
def func2(a,b,c):
    print("hello，here is a func for add :")
    time.sleep(1)
    print("result is %d" %(a+b+c))
'''
if 1==2:
    f = func
    func2(3,4,5)
    f(3,4)
    #func()
    
#多个装饰器
def deco01(func):
    def wrapper(*args, **kwargs):
        print("this is deco01")
        startTime = time.time()
        func(*args, **kwargs)
        endTime = time.time()
        msecs = (endTime - startTime)*1000
        print("time is %d ms" %msecs)
        print("deco01 end here")
    return wrapper
def deco02(func):
    def wrapper(*args, **kwargs):
        print("this is deco02")
        func(*args, **kwargs)
        print("deco02 end here")
    return wrapper
@deco02
@deco01
def func(a,b):
    print("hello，here is a func for add :")
    time.sleep(1)
    print("result is %d" %(a+b))
if 1==2:
    f = func
    f(3,4)
    #func()
    
    
def dec1(func):  
    print("1111")  
    def one():  
        print("2222")  
        func()  
        print("3333")  
    return one  
def dec2(func):  
    print("aaaa")  
    def two():  
        print("bbbb")  
        func()  
        print("cccc")  
    return two  
@dec1  
@dec2  
def test():  
    print("test test")  
if 1==1:
    test()  
    
#d39c095e-2bf2-31b4-8405-997ded2acc54_f00eba05-fd80-4291-8fde-9e4124b05e34
aaa= 'd39c095e-2bf2-31b4-8405-997ded2acc54_f00eba05-fd80-4291-8fde-9e4124b05e34'
print len(aaa)
print aaa[61:73]

def get_y(a,b):
    return lambda x:a*x+b
y1 = get_y(2,1)
print y1(3) # 结果为5