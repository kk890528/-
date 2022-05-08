
import requests
from bs4 import BeautifulSoup
import time
import random
import string
import numpy as np
import pandas as pd
import datetime
import json
import re
def count_word(x):
    chinese=[]
    english=[]
    number=[]
    en=''
    num=''
    for i in list(x):

        if i in string.ascii_letters:
            en+=i
        elif i.isdigit():
            num+=i
        else:
            if en !='':
                english.append(en)
            if num!='':
                number.append(num)
            en=''
            num=''
            if i !=' ':
                chinese.append(i)
    words=len(english)+len(chinese)+len(number)
    return words

def liberal(x):
    ltn_news=BeautifulSoup(x.text, 'html.parser')
    #標題
    try:
        t=ltn_news.find('title').text
        t2=t.split('-')
        titles=t2[0]
    except:
        titles='錯誤'
    #分類
    try:
        sention=ltn_news.find('script',type="application/ld+json").contents[0].split('\n')[7].split(':')[1][2:-2]
    except:
        sention='錯誤'
    #日期
    try:
        try:
            date=ltn_news.find('meta',property="article:published_time")['content'][0:10]
        except:
            date=ltn_news.find('span',{'class':'time'}).text
            date = re.search(r"(\d{4}/\d{1,2}/\d{1,2})",dates).group()
    except:
        date='錯誤'
    #內文
    try:
        con_list=ltn_news.find_all('p')[3:]

        content=''
        for i  in con_list:
            try:
                if i.text[-1] in ['。','？','?','！'] and i.text!='「武漢肺炎專區」請點此，更多相關訊息，帶您第一手掌握。':
                    content+=i.text
                else:
                    pass
            except:
                pass
    except:
        content='錯誤'
    #字數
    try:
        words=count_word(content)
    except:
        words='錯誤'
    #作者
    try:
        a1=content.find('〔')
        a2=content.find('／')
        author=content[a1+1:a2]
    except:
        author='錯誤'
    if '記者' in author :
        author=author.replace('記者','')
    #圖片數
    try:
        n_p=len(ltn_news.find_all('div',attrs={'class':'photo boxTitle'}))+len(ltn_news.find_all('span',attrs={'class':'ph_b ph_d1'}))
    except:
        n_p='錯誤'
    #影片數
    try:
        v=ltn_news.find_all('iframe')
        v2=[]
        v3=[]
        for i in v:
            try:
                if 'autoplay' in i['allow']:
                    if 'facebook' in i['src']:
                        v3.append(i)
                    else:
                        v2.append(i)
            except:
                pass
        v_p=len(v2)
        if len(v3)!=0:
            all_p='出現fb網址'
        elif v_p !=0:
            all_p=f'{n_p}（+{v_p}影片）'
        else:
            all_p=n_p
    except:
        all_p=0
    #if '同' in content :
    return ['','',author,'',sention,date,titles,content,'','','','','',words,'',all_p,'']
    #else:
        #return ['','','','','','','','','','','','','','','','','']
        
def web_crawl(x,start_time,until_time):
    https=[]
    tick=0
    n=1
    while n!=0:
        try: 
          url=f'https://search.ltn.com.tw/list?keyword={x}&start_time={start_time}&end_time={until_time}&sort=date&type=all&page={n}'
          ltn_news=BeautifulSoup(requests.get(url).text, 'html.parser')
          http_list=ltn_news.find('ul',{'class':'list boxTitle'}).find_all('a',{'class':'http'})
          for i in http_list:
              https.append(i.text)
          time.sleep(random.uniform(1, 5))
          tick+=1
          n+=1
          print(f'網頁完成:{tick}')
        except:
          n=0
          break
    return https
def web_crawl2(x,start_time,until_time):
  """
  x為搜尋關鍵詞
  start_time為開始時間
  until_time為結束時間
  """

  http=web_crawl(x,start_time,until_time)
  ltn=[]
  ticks2=0
  for i in range(0,len(http)):
      ltn.append(requests.get(http[i]))
        #每爬一個休息1-5秒(random抽)，怕被抓
      ticks2+=1
      print(f'全部新聞:{len(http)}  完成新聞:{ticks2}')
      time.sleep(random.uniform(1, 5))
  liberal_news_result=list(map(liberal,ltn))
  liberal_news_df=pd.DataFrame(liberal_news_result)
  liberal_news_df=liberal_news_df.rename(index=str,columns={0:'',1:'',2:'作者',3:'',4:'記者路線',5:'日期',6:'標題',7:'內文',8:'',9:'',10:'',11:'',12:'',13:'字數',14:'',15:"附圖（幀）",16:''})
  liberal_news_df['網址']=http
  liberal_news_df=liberal_news_df[liberal_news_df.標題!='']
  return liberal_news_df
#df=web_crawl2('同性婚姻','2010-01-01','2016-12-31')
#df=df.drop_duplicates()
#df.to_excel('自由時報同婚2010-2016.xlsx')
x=requests.get('https://art.ltn.com.tw/article/paper/794473')
ltn_news=BeautifulSoup(x.text, 'html.parser')
ltn_news
date=ltn_news.find('span',{'class':'time'}).text
date = re.search(r"(\d{4}/\d{1,2}/\d{1,2})",dates).group()
date
