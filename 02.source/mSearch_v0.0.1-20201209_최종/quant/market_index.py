# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 14:32:19 2020

@author: 3337389
"""


import pandas as pd
from pandas import DataFrame, Series
import requests as re
from bs4 import BeautifulSoup
import sqlite3
import sqlalchemy


class Class_MarketIndex:
    ###############################################################################
    # 마켓인덱스 가져오기  CD91일,콜 금리,국고채 3년,회사채 3년
    ###############################################################################

    
    def crawling_interest_rates(self):
        
        url = 'http://finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_CD91&page=1'
        
        crawling_list = ['IRR_CALL',]
        
        #폴더 위치를 입력해주세요
        folder_adress = '.'
        
        data_dict = {'IRR_CD91':[],
                     'IRR_CALL':[],
                     'IRR_GOVT03Y':[],
                     'IRR_CORP03Y':[]}
    
        label_list = ['IRR_CD91','IRR_CALL','IRR_GOVT03Y','IRR_CORP03Y']
    
        Data = DataFrame()
        
        for label in label_list:
        
            date_list = []
            
            try:
                for i in range(1,700):
                    url = re.get('http://finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=%s&page=%s'%(label,i))
                    url = url.content
            
                    soup = BeautifulSoup(url,'html.parser')
            
                    # 날짜 가져오기
                    dates = soup.select('tr > td.date')
                
                
                    # 빈테이지인지 테스트
                    try:
                        test = soup.find('tbody').find('tr').find('td',{'class':'num'}).text # .text가 에러를 반환하는가?
                    except:
                        break
                
                
                    # 처음 한번만 가져오자
                    for date in dates:
                        date_list.append(date.text.strip())
                        
                                            
            
                    rates = soup.find('tbody').find_all('tr')
            
                    for rate in rates:
                        data_dict[label].append(rate.find('td',{'class':'num'}).text.strip())
                
            except:
                print('Error')
            
            temp_dataframe = DataFrame(data_dict[label], index = date_list)
            Data = pd.merge(Data,temp_dataframe,how = 'outer', left_index = True, right_index = True)
            
            print(label + '의 자료를 성공적으로 가져왔습니다')
        
        Data.columns = ['CD_91일', '콜_금리', '국고채_3년', '회사채_3년']
        
        
        print(Data.head)
        
        # 데이터프레임의 인덱스를 일자컬럼으로 레벨을 변환시켜준다.
        #Data.columns = Data.columns.droplevel()
        Data = Data.reset_index()
        Data.rename(columns={'index':'일자'},inplace=True)
        print(Data.head)

        Data.to_csv('%s/interest_rate.csv'%folder_adress)
        
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
        cursor.execute("drop table market_index ")
        cursor.execute("create table market_index (일자,CD_91일,콜_금리,국고채_3년,회사채_3년)")
        cursor.execute("delete from  market_index ")
        # 지우고 다시 시작하자
        con.commit()    
    
       
        
        # 2. to_sql함수를 이용해서 DB에 저장    
        
        # sql 문장들
        for ix, r in Data.iterrows():
           # print (r)
           values=  u"('%s','%s','%s','%s','%s')" % ( 
               r['일자'], r['CD_91일'], r['콜_금리'], r['국고채_3년'],r['회사채_3년'] )
           
           insert_sql = u"insert into market_index( 일자,CD_91일,콜_금리,국고채_3년,회사채_3년 ) values %s ;" % (
                    u"".join(values))
           print (insert_sql)
           con.execute(insert_sql)
           con.commit()    
              
        
        return Data


    # Market Index 가져오기
    def index_crawling  (self):
        self.crawling_interest_rates()

