# -*- coding: utf-8 -*-
"""
Created on Wed May 27 10:48:25 2020

@author: 3337389
"""
# 1 거래소 상장법인목록 크롤링

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import sqlite3
import sqlalchemy


# 거래소 상장법인목록 크롤링 
class Class_CompanyInfo :
    
    def __init__(self):
        return
    
    def stock_master(self):
        url = 'http://kind.krx.co.kr/corpgeneral/corpList.do'
        data = {
            'method':'download',
            'orderMode':'1',           # 정렬컬럼
            'orderStat':'D',           # 정렬 내림차순
            'searchType':'13',         # 검색유형: 상장법인
            'fiscalYearEnd':'all',     # 결산월: 전체
            'location':'all',          # 지역: 전체
        }
    
        r = requests.post(url, data=data)
        f = BytesIO(r.content)
        dfs = pd.read_html(f, header=0, parse_dates=['상장일'])
        df = dfs[0].copy()
    
        # 숫자를 앞자리가 0인 6자리 문자열로 변환
        df['종목코드'] = df['종목코드'].astype(np.str)   
        df['종목코드'] = df['종목코드'].str.zfill(6)
        # 특수문자 제거
        # 참고 http://blog.naver.com/PostView.nhn?blogId=wideeyed&logNo=221605317822 
        df['주요제품'] = df['주요제품'].str.replace(pat=r'[^\w\s]', repl=r' ', regex=True)
    
        return df
    
    def stock_crawling(self):    
        df_master = self.stock_master()
        df_master.head()
        
        
        #print(df_master)
        print(df_master.head())
        
        #print(df_master['회사명','종목코드','업종','주요제품', '상장일', '결산월','대표자명','홈페이지','지역'])
        
        
        from sqlalchemy import create_engine
        
        # echo=True를 선언할 경우 실제 테이블 생성 쿼리문을 보여준다
        engine = create_engine('sqlite:///itm_master.db', echo=True)
        
        #1. SQLite DB에 연결
        #SQLite DB에 저장하기 위해 DB와 연결을 한다
        con = sqlite3.connect("./itm_master.db")
        cursor = con.cursor()
        
        # DB CREAETE
        #
        
        # DB CREAETE
        cursor.execute("drop table company_info ")
        cursor.execute("create table company_info ( 회사명,종목코드,업종,주요제품,상장일,결산월,대표자명,홈페이지,지역)")
        cursor.execute("delete from  company_info ")
        # 지우고 다시 시작하자
        con.commit()    
        
        
        # 2. to_sql함수를 이용해서 DB에 저장    
        
        # sql 문장들
        for ix, r in df_master.iterrows():
            #print( u"(%s, %s, %s,%s, %s, %s,%s, %s, %s)" % (r['회사명'], r['종목코드'], r['업종'], r['주요제품'],r['상장일'], r['결산월'], r['대표자명'], r['홈페이지'], r['지역']))
            values=  u"('%s', '%s', '%s','%s', '%s', '%s','%s', '%s', '%s')" % (r['회사명'], r['종목코드'], r['업종'], r['주요제품'],r['상장일'], r['결산월'], r['대표자명'], r['홈페이지'], r['지역'] )
            #print(values)
            insert_sql = u"insert into company_info( 회사명,종목코드,업종,주요제품,상장일,결산월,대표자명,홈페이지,지역 ) values %s ;" % (u"".join(values))
            print (insert_sql)
            con.execute(insert_sql)
            con.commit()
        
        
        
        #
        #3. DB 연결 종료
        #SQLite에 DB작업이 완료되면, DB를 닫는 작업을 하는 것이 좋다. DB를 닫는 명령은 아래와 같다.
        con.close()