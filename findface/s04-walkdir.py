# -*- coding: utf-8 -*-
#两种方法
#!/usr/bin/env python
import os

dir=r'C:\Users\hanmi\eclipse-workspace'
'''
def fr(dir):
    filelist=os.listdir(dir)
    for i in filelist:
        fullfile=os.path.join(dir,i)
        if not os.path.isdir(fullfile):
            if i == "1.txt":
                print (fullfile)
                os.remove(fullfile)
        else:
            fr(fullfile)
fr(dir)
'''


def fw(dir):
    n = 0
    for root,dirs,files in os.walk(dir):
        for f in files:
            if f == "s04-walkdir.py":
                #os.remove(os.path.join(root,f))
                fullfile = os.path.join(root,f)
                print  os.path.join(root,'adsfasf') + f
                #print os.path.pardir(root)
                print n
                #os.remove(fullfile)
                break
        for d in dirs:
            #print d
            n += 1
            #fullfile = os.path.join(root,d)
            fw(d)
            
fw(dir)

