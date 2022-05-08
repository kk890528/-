
import requests
from bs4 import BeautifulSoup
import time
import datetime
import random
import string
import numpy as np
import pandas as pd
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import re
def http_search(x,start_date,until_date):
    https_df_list=[]
    #tick=0
    n=1
    min_date=datetime.datetime.now().strftime('%Y-%m-%d')
    while min_date >= start_date :
        url=f'https://udn.com/api/more?page={n}&id=search:{x}&channelId=2&type=searchword&last_page=28'
        soup=requests.get(url)
        udn=BeautifulSoup(soup.text, 'html.parser')
        data=json.loads(re.sub(r'for \(;;\);','',soup.text))
        https=data['lists']
        url_and_time=[]
        date_find= re.compile(r'\d\d\d\d-\d\d-\d\d')
        for i in https:
            url_and_time.append([i['titleLink'],date_find.findall(i['time']['dateTime'])[0]])
        #print(f'網頁完成:{tick}')
        url_df=pd.DataFrame(url_and_time,columns=['網址','日期'])
        try:
            max_date=max(url_df.日期)
            min_date=min(url_df.日期)
        except:
            min_date='2000-01-01'
            max_date='2000-01-01'
        url_df=url_df[url_df.日期<until_date]
        if len(url_df)>0:
            https_df_list.append(url_df)
        print(f'已完成:{n}頁 \n 日期:{max_date}')
        n+=1
        time.sleep(random.uniform(1, 5))
    
    return  https_df_list

def udn_crawl(url):
    soup=requests.get(url)
    udn=BeautifulSoup(soup.text, 'html.parser')
    #標題
    try:
        title=udn.find('title').text
    except:
        title='Error'
    #內文
    try:
        try:
            content=udn.find('div',{'class':'story_body_content'}).text
            try:
                content=udn.find('section',{'class':'article-content__editor'}).text
            except:
                pass
        except:
            content=''
            try:
                try:
                    for i in udn.find('main').find_all('p'):
                        content+=i.text
                except:
                    con=udn.find('section',{'id':'story-main'}).find_all('p')
                    for i in con:
                        content+=i.text
            except:
                try:
                    con= udn.find('div',{'id':'story_body_content'}).find_all('p')
                    for i in con:
                        content+=i.text
                except:
                    for i in udn.find('div',{'class':'article-content article-content-common'}).find_all('p'):
                        content+=i.text
    except:
        content='Error'
    time.sleep(random.uniform(1, 5))
    return [title,content]

def udn_crawler(keyword,start_date,until_date):
    df=http_search(keyword,start_date,until_date)
    df=pd.concat(df)
    tick=0
    n=len(df)
    TITLE=[]
    CONTENT=[]
    for i in df.網址:
        u_list=udn_crawl(i)
        TITLE.append(u_list[0])
        CONTENT.append(u_list[1])
        tick+=1
        print(f'總共{n}篇新聞 -----> 完成{tick}篇新聞')
    df['標題']=TITLE
    df['內文']=CONTENT
    return df
df=udn_crawler('同性婚姻','2010-01-01','2016-12-31')
df=df.drop_duplicates()
df.to_excel('聯合同婚2010-2016.xlsx')

