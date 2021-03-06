#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Created on 2015-12-8

@author: dannl
'''
import feedparser
from bs4 import BeautifulSoup
import time,logging
from database import dbconfig,table
from common.common import r1, cost_log
from common import timeFormat
from common.toolpit import getMd5

ctable=dbconfig.tableName['techcrunch']

def getRssInfo():
    url='http://techcrunch.cn/feed/'
    d=feedparser.parse(url)
#     print d.feed.title
#     print d.feed.link
#     print d.feed.description 
#     print d.etag
#     print d.modifed
    infoList=[]
    for entry in d.entries:
        info={}
#         print entry
        info['url']=entry.link
        info['newsid']=getMd5(info['url'])
#         print info['newsid'],info['url']
        info['title']=entry.title
        info['ctime']=(long)(time.mktime(entry.published_parsed))
        info['author']=entry.author
#         print timeFormat.getTimeStamp(info['ctime']),info['title']
#         print info['author']
        info['source']=ctable
        tags=entry.tags if 'tags' in entry else None   
        info['keywords']=','.join(tag.term for tag in tags) if tags else ''        
        info['description']=entry.description
        soup = BeautifulSoup(info['description'], "html.parser",from_encoding='utf-8')        
        img=soup.find('img')
        info['thumb']=img.get('src') if img else ''
        info['summary']=' '.join(p.getText().strip() for p in soup.find_all('p'))
#         print info['keywords'],info['thumb']
#         print soup.getText()
#         print info['description']
        infoList.append(info)
    return infoList

@cost_log
def main():
    infoList=getRssInfo()
    for info in infoList:
        try:
            table.InsertItemDict(ctable, info)
            print timeFormat.getTimeStamp(info['ctime']),info['title']
        except:
            logging.error('encoding not supported:%s'%info['url'])
    return ctable,len(infoList)

if __name__=='__main__':
    main()