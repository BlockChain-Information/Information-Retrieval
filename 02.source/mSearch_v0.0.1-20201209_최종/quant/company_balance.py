# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 09:50:21 2020

@author: 3337389
"""

# 참고 https://blog.naver.com/o12486vs2/221904332250
# library import
import pandas as pd
import numpy as np
import requests
from io import BytesIO
import time
import sqlite3
import sqlalchemy


class Class_CompanyBalance :
    ###############################################################################
    # 상장법인목록 크롤링(한국거래소)
    ###############################################################################
    # 지난번엔 함수로 만들어 사용했으나
    # 이번에는 함수로 만들지 않고 그냥 사용하고
    # 마지막에 회사명과 종목코드를 가진 데이터 프레임을 얻고
    # 종목명은 별도로 리스트로 만들어 두겠음
    
    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do' 
    data = {
      'method':'download',
      'orderMode':'1',             #정렬할 컬럼   <== 3에서 1로 변경, 이유는 3으로 했을때 얻어진 종목코드의 재무정보가 없음
      'orderStat':'D',             #내림차순
      'searchType':'13',           #검색유형(상장법인)
      'fiscalYearEnd':'all',       #결산월(전체)
      'location':'all',            #지역(전체)
    }
    
    #데이터 가저오기
    r = requests.post(url, data=data)
    i = BytesIO(r.content)
    df = pd.read_html(i, header=0)
    df_clean = df[0].copy()
    
    #정리하기
    df_clean['종목코드'] = df_clean['종목코드'].astype(np.str) 
    df_clean['종목코드'] = df_clean['종목코드'].str.zfill(6)
    
    
    stocks = df_clean[['종목코드','회사명']]
    stock_lists = stocks['종목코드']
    
    
    # stocks 데이터 프레임은 나중에 수집된 재무정보에 회사명을 넣어줄 때 사용할 예정
    #stocks
    #
    #for문을 돌려 재무정보를 크롤링할때 사용할 상장사 종목코드
    mystock_list = stock_lists[:]
    
    #print(mystock_list)
    
    ###############################################################################
    # 재무정보 크롤링(fnguide) 및 데이터 프레임 변경 함수
    ###############################################################################
    # 재무정보 수집 함수
    def collector(self,stock_list):
      url = 'http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{}&cID=&MenuYn=Y&ReportGB=&NewMenuID=103&stkGb=701'.format(stock_list)
      r = requests.get(url)
      fs = pd.read_html(r.text)  
      fs_is = fs[0]
      fs_is = fs_is[fs_is.columns[:5]]
      fs_bs = fs[2]
      fs_cf = fs[4]
    
      fs_df = pd.concat([fs_is, fs_bs, fs_cf])
      fs_df = fs_df.set_index(fs_df.columns[0])
      fs_df = fs_df.loc[['매출액','매출원가','매출총이익','영업이익','당기순이익','자산','부채','자본','영업활동으로인한현금흐름']]
    
      return fs_df
    
    
    
    # 재무정보 데이터프레임 변환 함수
    
    def change_df(self,stock_list ,fs_df):
      for num, col in enumerate(fs_df.columns):
        temp_df = pd.DataFrame({stock_list : fs_df[col]}) 
        temp_df = temp_df.T
        temp_df.columns = [[col]*len(fs_df), temp_df.columns]
    
        if num == 0:
          change_fs = temp_df
        else:
          change_fs = pd.merge(change_fs, temp_df, how='outer', left_index=True, right_index=True) 
    
      return change_fs
    
    # 재무정보 Crawling
    def balance_crawling(self):   
        # 내가 원하는 재무정보가 없거나, 결산시기가 다르거나, 통신에러, 통신지연 등 발생할수있는
        # 예외를 처리함
        
        for num, stock_list in enumerate(self.mystock_list):
          try:                                                 #시작은 위에서 얻은 stock_lists를 for문으로 하나씩 추출
            print(num,stock_list)                              #실행후 현재 상태 확인용 print문
            #time.sleep(1)                                      #1초간 멈춤(너무 빠르게 요청할경우 에러가 날수있음)
            try:                                               #본문을 시작
              fs_df = self.collector(stock_list)                    #collector함수(재무정보크롤링함수)에 종목코드 전달 하여 수집
            except requests.exceptions.Timeout:                #만약 브라우저에 요청시 예외로 Timeout을 발생시킨다면
              time.sleep(60)                                   #60초간 기다렸다가 
              fs_df = self.collector(stock_list)                    #다시 collector함수로 재무정보크롤링
            fs_change = self.change_df(stock_list,fs_df)            #change_df함수(재무정보데이터프레임변경함수)에 종목코드,재무정보 전달
            if num == 0:                                       #첫번째 재무정보는 그대로 total_fs에 저장(기준이되는 표,여기에 재무정보가 없을경우 이후의 표가 합처지지않음)
              total_fs = fs_change                             
            else:                                              #다른정목부터 total_fs 에 합침
              total_fs = pd.concat([total_fs, fs_change])
          except ValueError:                                   #예외로 ValueError가 발생하면 제외하고 다음 진행 continue
            continue
          except KeyError:                                     #예외로 ValueError가 발생하면 제외하고 다음 진행 continue
            continue
        
        
        #print(total_fs)
        
        
        
        # 필요한컬럼만 가저오기
        fs = total_fs.copy()
        fs = fs[['2019/12']]
        
        # 종목명 넣기
        #name = stocks.set_index('종목코드')  
        #name.columns = [['회사명'],['회사명']]
        #fs_total = pd.merge(name ,fs, how = 'left', left_index=True, right_index=True)
        fs.columns = fs.columns.droplevel()
        fs = fs.reset_index()
        fs.rename(columns={'index':'종목코드'},inplace=True)
        
        #print("fs=", fs)
        
        # 엑셀로 저장하기
        #fs_total.to_excel('파일명.xlsx')
        
        
        from sqlalchemy import create_engine
        
        # echo=True를 선언할 경우 실제 테이블 생성 쿼리문을 보여준다
        engine = create_engine('sqlite:///itm_master.db', echo=True)
        
        #1. SQLite DB에 연결
        #SQLite DB에 저장하기 위해 DB와 연결을 한다
        con = sqlite3.connect("./itm_master.db")
        cursor = con.cursor()
        
        # DB CREAETE
        cursor.execute("drop table company_balance ")
        cursor.execute("create table company_balance ( 종목코드 ,연도 , 월 , 매출액,매출원가,매출총이익,영업이익,당기순이익,자산,부채,자본,현금흐름)")
        cursor.execute("delete from  company_balance ")
        # 지우고 다시 시작하자
        con.commit()          
        
        
        # 2. to_sql함수를 이용해서 DB에 저장    
        
        # sql 문장들
        for ix, r in fs.iterrows():
           # print (r)
            #print( u"(%s, %s, %s,%s, %s, %s,%s, %s, %s)" % (r['종목코드'], r['회사명'], r['업종'], r['주요제품'],r['상장일'], r['결산월'], r['대표자명'], r['홈페이지'], r['지역']))
           values=  u"('%s', '%s','%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (r['종목코드'], '2019', '12',r['매출액'],r['매출원가'],r['매출총이익'],r['영업이익'],r['당기순이익'],r['자산'],r['부채'],r['자본'],r['영업활동으로인한현금흐름'] )
            #print(values)
           insert_sql = u"insert into company_balance( 종목코드 ,연도 , 월 , 매출액,매출원가,매출총이익,영업이익,당기순이익,자산,부채,자본,현금흐름 ) values %s ;" % (u"".join(values))
           print (insert_sql)
           con.execute(insert_sql)
           con.commit()
