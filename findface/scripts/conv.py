# -*- coding: utf-8 -*-

import os,shutil,time,math,sys

VIDEOPATH = r'C:\myworkshop\fileforfindface'
SUPPORTED_FORMATS = ['mp4','m4v','mkv','webm','mov','avi','wmv','mpg','flv',]

def conv(path):
    temp_path = path + '_temp'
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)
    conv_path = path + '_conv'
    if not os.path.exists(conv_path):
        os.mkdir(conv_path)
        
    for root,dirs,files in os.walk(path):
        for dir in dirs:
            tempdir = os.path.join(root,dir)
            if os.listdir(tempdir):
                conv(tempdir)
        for file in files:
            if CheckVideo(file):
                time_start = time.time()
                fullpath = os.path.join(root,file)
                temp_fullpath = os.path.join(temp_path,file)
                temp_fullpath = os.path.splitext(temp_fullpath)[0] + '.avi'
                command_txt = 'C:/ffmpeg/bin/ffmpeg.exe -i ' + fullpath + ' -y -r 25 ' + temp_fullpath
                try:
                    os.popen3(command_txt)
                    des_fullpath = os.path.join(conv_path,file)
                    des_fullpath = os.path.splitext(des_fullpath)[0] + '.avi'
                    shutil.move(temp_fullpath,des_fullpath)
                    os.remove(fullpath)
                    time_end = time.time()
                    print des_fullpath,':',changeTime(time_end-time_start)
                except WindowsError as e:
                    print e
                    sys.exit()
                except IOError as e:
                    print e
                    sys.exit()
                
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

def CheckVideo(f):
    if f.split('.')[-1] not in SUPPORTED_FORMATS:
        return False
    else:
        return True
    
if __name__ == '__main__': 
    conv(VIDEOPATH)