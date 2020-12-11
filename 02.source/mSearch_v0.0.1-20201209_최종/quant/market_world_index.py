# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 14:36:29 2020

@author: 3337389
"""
# https://blog.naver.com/koko8624/221288761509 참고

import pandas as pd
from pandas import DataFrame, Series
import requests as re
from bs4 import BeautifulSoup
import datetime as date
import time
import sqlite3
import sqlalchemy


class Class_MarketWorldIndex:
    ###############################################################################
    # 마켓인덱스 가져오기  네이버 금융 시장지표 크롤링 소스코드 (환율, WTI, 국제 금)
    ###############################################################################    
    
    def market_index_crawling(self):        
        
        folder_adress = '.'
        
        Data = DataFrame()
        
        url_dict = {'미국 USD':'http://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW',
                    '일본 JPY':'http://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_JPYKRW',
                    '유럽연합 EUR':'http://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_EURKRW',
                    '중국 CNY':'http://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_CNYKRW',
                    'WTI':'http://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=OIL_CL&fdtc=2',
                    '국제 금':'http://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=CMDT_GC&fdtc=2'}
    
        for key in url_dict.keys():
        
            date = []
            value = []
    
            for i in range(1,1000):
                url = re.get(url_dict[key] + '&page=%s'%i)
                url = url.content
    
                html = BeautifulSoup(url,'html.parser')
    
                tbody = html.find('tbody')
                tr = tbody.find_all('tr')
                
                
                '''마지막 페이지 까지 받기'''
                if len(tbody.text.strip()) > 3:
                    
                    for r in tr:
                        temp_date = r.find('td',{'class':'date'}).text.replace('.','-').strip()
                        temp_value = r.find('td',{'class':'num'}).text.strip()
                
                        date.append(temp_date)
                        value.append(temp_value)
                else:
    
                    temp = DataFrame(value, index = date, columns = [key])
                    
                    Data = pd.merge(Data,temp, how='outer', left_index=True, right_index=True)        
                    
                    print(key + '자료 수집 완료')
                    time.sleep(10)
                    break
                
        Data.columns = ['미국_USD', '일본_JPY', '유럽연합_EUR', '중국_CNY','WTI','국제_금']
        
        # 데이터프레임의 인덱스를 일자컬럼으로 레벨을 변환시켜준다.
        #Data.columns = Data.columns.droplevel()
        Data = Data.reset_index()
        Data.rename(columns={'index':'일자'},inplace=True)
        
        Data.to_csv('%s/market_world_index.csv'%folder_adress)      
        # 
       # DB저장
        from sqlalchemy import create_engine
        
        # echo=True를 선언할 경우 실제 테이블 생성 쿼리문을 보여준다
        engine = create_engine('sqlite:///itm_master.db', echo=True)
        
        #1. SQLite DB에 연결
        #SQLite DB에 저장하기 위해 DB와 연결을 한다
        con = sqlite3.connect("./itm_master.db")
        cursor = con.cursor()
        
        # DB CREAETE
        cursor.execute("drop table market_world_index ")
        cursor.execute("create table market_world_index (일자,미국_USD,일본_JPY,유럽연합_EUR,중국_CNY,WTI,국제_금)")
        cursor.execute("delete from  market_world_index ")
        # 지우고 다시 시작하자
        con.commit()    
    
       
        
        # 2. to_sql함수를 이용해서 DB에 저장    
        
        # sql 문장들
        for ix, r in Data.iterrows():
           # print (r)
           values=  u"('%s','%s','%s','%s','%s','%s','%s')" % ( 
               r['일자'], r['미국_USD'], r['일본_JPY'], r['유럽연합_EUR'],r['중국_CNY'],r['WTI'],r['국제_금'] )
           
           insert_sql = u"insert into market_world_index( 일자,미국_USD,일본_JPY,유럽연합_EUR,중국_CNY,WTI,국제_금 ) values %s ;" % (
                    u"".join(values))
           print (insert_sql)
           con.execute(insert_sql)
           con.commit()                 
    

        return Data
    

    # Market Index 가져오기
    def index_crawling  (self):
        self.market_index_crawling()