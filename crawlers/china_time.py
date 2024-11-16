
from bs4 import BeautifulSoup
import time
import random
import string
import numpy as np
import pandas as pd
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
def google_search(x,n):
    driver = webdriver.Chrome('chromedriver')
    driver.get(f'https://www.google.com/search?q={x}')
    next_page_times = n
    http=[]
    for _page in range(next_page_times):
    
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

        # Turn to the next page
        try:
            driver.find_element_by_link_text('下一頁').click()
        except:
            print('Search Early Stopping.')
            break
    driver.close()
    return http
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
def chinatime(x):
    if x!='error':
        try:
            china=BeautifulSoup(x.text, 'html.parser')
        except:
            china='error'
        #標題
        try:
            titles=china.find('h1',attrs={'class':'article-title'}).text
        except:
            titles='Error'
        #日期
        try:
            date=china.find('meta', property="article:published_time")['content'][0:10]
        except :
            date='Error'
        #記者
        try:
            author=china.find('div',attrs={'class':'author'}).text
            author=author.replace('\n','')
            author=author.replace(' ','')
        except:
            author='Error'
        #類別
        try:
            sention=china.find('meta',attrs={'property':'article:section'})['content']
        except:
            sention='Error'
        #內文
        try:
            content=china.find('div',attrs={'class':'article-body'}).text
            content=content.replace('\n','')
            k=content.rfind('。')
            content=content[:k+1]
        except:
            content='Error'
        #字數
        try:
            words=count_word(content)
        except:
            words='Error'
        try:
            #圖片數
            n_p=len(china.find_all('div',attrs={'class':'photo-container'}))
            #影片數
            v_p=len(china.find_all('div',attrs={'class':'article-body','class':'video-container'}))
            ##加起來
            if v_p !=0:
                all_p=f'{n_p}（+{v_p}影片）'
            else:
                all_p=n_p
        except:
            all_p='Error'
        if '同' in content :
            return ['','',author,'',sention,date,titles,content,'','','','','',words,'',all_p,'']
        elif content=='錯誤' :
            return ['','',author,'',sention,date,titles,content,'','','','','',words,'',all_p,'']
        if words==1:
            return ['','',author,'',sention,date,titles,content,'','','','','',words,'',all_p,'']
        else:
            return['','','','','','','','','','','','','','','','','']
    else:
        return ['error','','','','','','','','','','','','','','','','']
def new_crawl2(search,start_date,until_date):
    http=[]
    tick=0
    n=1
    while n !=0:
        test=requests.get(f'https://www.chinatimes.com/search/{search}?page={n}&chdtv',headers={'Connection':'close'})
        china2=BeautifulSoup(test.text, 'html.parser')
        time_list=list(map(lambda x:x['datetime'],china2.find_all('time')))
        max_time=max(time_list)
        min_time=min(time_list)
        if max_time<start_date:
            n=0
            break
        if min_time<until_date:
            webs=china2.find('ul',{'class':'vertical-list list-style-none'}).find_all('h3',{'class':'title'})
            for i in webs:
                http.append(i.find('a')['href'])
        tick+=1
        n+=1
        print(f'網頁已完成：{tick}')
        time.sleep(random.uniform(1, 5)) 
    return http
def web_crawl2(keyword,start_time,until_time): 
    http=new_crawl2(keyword,start_time,until_time)
    china_time=[]
    for i in range(0,len(http)):
        try:
            china_time.append(requests.get(http[i],headers={'Connection':'close'}))
            time.sleep(random.uniform(1, 5))
            print(f'總共新聞:{len(http)}  新聞已完成：{i}')
        except:
            china_time.append('error')
            print(f'錯誤網址：{http[i]}')
            pass
        
    china_time_result=list(map(chinatime,china_time))
    chinatime_df=pd.DataFrame(china_time_result)
    chinatime_df=chinatime_df.rename(index=str,columns={0:'',1:'',2:'作者',3:'',4:'記者路線',5:'日期',6:'標題',7:'內文',8:'',9:'',10:'',11:'',12:'',13:'字數',14:'',15:"附圖（幀）",16:''})
    chinatime_df['網址']=http
    chinatime_df=chinatime_df[chinatime_df.標題!='']
    return chinatime_df


df2=web_crawl2('同性婚姻','20100101','20161231')
df2=df2.drop_duplicates()
df2.to_excel('2010-2016中時同婚.xlsx')

