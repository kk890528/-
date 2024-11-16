import requests
from bs4 import BeautifulSoup
import time
import random
import string
import numpy as np
import pandas as pd
import datetime
from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
import json
import re
def google_search(x,n):
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--headless')
    driver = webdriver.Chrome(options=chromeOptions)
    driver.get(f'https://www.google.com/search?q={x}')
    next_page_times = n
    http=[]
    for page in range(next_page_times):
    
        soup = BeautifulSoup(driver.page_source,'html.parser')
        items=soup.find_all('div', attrs={'class':'yuRUbf'})

        for i in items:
            # 網址
            h=i.find('a')['href']
            if 'cdc.gov.tw' in h :
                pass
            else:
                http.append(h)
        # Wait
        time.sleep(random.uniform(1, 5))
        print(f'已爬到第{page+1}頁')
        # Turn to the next page
        try:
            driver.find_element_by_link_text('下一頁').click()
        except:
            print('Search Early Stopping.')
            break
    driver.close()
    return http
def apple_daily(x):
    apple_http=requests.get(x)
    time.sleep(random.uniform(1, 5))
    apple2 = BeautifulSoup(apple_http.text, 'html.parser')
    #標題
    title='｜'.join(apple2.find('title').text.split('｜')[:-2])
    try:
        title=title.replace('\u3000',' ')
    except:
        pass
    apple_text=apple2.select('p[class="text--desktop text--mobile article-text-size_md tw-max_width"]')
    
    #內容
    content=get_text(apple2)
    #記者/機構
    try:
        a1=content.rfind('（')+1
        a2=content.rfind('╱')
        a3=content.rfind('／')
        a4=content.find('【')+1
        a5=content.find('╱')
        a6=content.find('／')
        if content[0]=='【':
            if a5>a6:
                author=content[a4:a5]
            else:
                author=content[a4:a6]
        else:
            if a2>a3:
                author=content[a1:a2]
            else:
                author=content[a1:a3]
    except:
        author=''
    #字數
    words=count_word(content)
    try:
        date=apple2.find('script',type="application/ld+json").string
        n=date.find('articleSection')
        #分類
        sention=date[n+17]+date[n+18]
        #日期
        k2=date.find('dateCreated')
        dates=date[k2+14]+date[k2+15]+date[k2+16]+date[k2+17]+date[k2+18]+date[k2+19]+date[k2+20]+date[k2+21]+date[k2+22]+date[k2+23]
    except:
        sention='None'
        dates='None'
    #圖片
    try:
        n_p=len(apple2.find_all('div',attrs={"style":"cursor:pointer"}))+len(apple2.find_all('div',attrs={"class":"promo-image-box"}))
    except:
        n_p='None'
    #影片
    try:
        v_p=len(apple2.find_all('div',attrs={'class':'promoItem'}))
    except:
        v_p='None'
    if v_p !=0:
        all_p=f'{n_p}（+{v_p}影片）'
    else:
        all_p=n_p
    #if '疫苗' in content :
    return ['','',author,'',sention,dates,title,content,'','','','','',words,'',all_p,'']
    #if words==1:
        #return ['','',author,'',sention,dates,title,content,'','','','','',words,'',all_p,'']
    #else:
        #return['','','','','','','','','','','','','','','','','']
def web_crawl(x,n):
    http=google_search(x,n)
    #apple=[]
    #for i in range(0,len(http)):
        #apple.append(requests.get(http[i]))
        #time.sleep(random.uniform(1, 5))
    apple_result=[]
    n=0
    for i in http:
        a=apple_daily(i)
        apple_result.append(a)
        n+=1
        print(f'新聞:{a[6]}已完成\n全部{len(http)}則新聞\n目前已完成：{n}則\n','---'*10)
    apple_df=pd.DataFrame(apple_result)
    apple_df=apple_df.rename(index=str,columns={0:'',1:'',2:'作者',3:'',4:'記者路線',5:'日期',6:'標題',7:'內文',8:'',9:'',10:'',11:'',12:'',13:'字數',14:'',15:"附圖（幀）",16:''})
    apple_df['網址']=http
    apple_df=apple_df[apple_df.標題!='']
    
    return apple_df

df=web_crawl('疫苗 after:2021-07-06 before:2021-07-10 site:tw.appledaily.com',1)
df2=df.drop_duplicates()
df2.to_excel('蘋果新聞.xlsx',index=False)
