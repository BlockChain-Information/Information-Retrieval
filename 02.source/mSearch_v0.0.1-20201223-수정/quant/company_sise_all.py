# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 14:41:55 2020

@author: 3337389
"""
# 네이버증시탭에서 모든정보 한꺼번에 가져오기
# https://jsp-dev.tistory.com/entry/PythonBS4-Naver-Finance-%EA%B5%AD%EB%82%B4-%EC%A6%9D%EC%8B%9C-%EA%B8%B0%EC%B4%88-Data-%EC%88%98%EC%A7%91-2?category=808569

import requests 
from bs4 import BeautifulSoup 
import numpy as np 
import pandas as pd 
import sqlite3
import sqlalchemy



class Class_CompanySiseAll :
    BASE_URL='https://finance.naver.com/sise/sise_market_sum.nhn?sosok=' 

    KOSPI_CODE = 0 
    KOSDAK_CODE = 1 
    START_PAGE = 1
    fields = [] 
    
    def crawl(self, code, page):
        global fields 
        data = {'menu': 'market_sum',
                              'fieldIds': fields, 
                              'returnUrl': self.BASE_URL + str(code) + "&page=" + str(page)}     
        # requests.get 요청대신 post 요청 
        res = requests.post('https://finance.naver.com/sise/field_submit.nhn', data=data) 
        
        page_soup = BeautifulSoup(res.text, 'lxml') 
        
        # 크롤링할 table html 가져오기 
        table_html = page_soup.select_one('div.box_type_l') 
        
        # Column명 
        header_data = [item.get_text().strip() for item in table_html.select('thead th')][1:-1] 
        
        # 종목명 + 수치 추출 (a.title = 종목명, td.number = 기타 수치) 
        inner_data = [item.get_text().strip() for item in table_html.find_all(lambda x: (x.name == 'a' and 'tltle' in x.get('class', [])) or (x.name == 'td' and 'number' in x.get('class', [])) )] 
        
        # page마다 있는 종목의 순번 가져오기 
        no_data = [item.get_text().strip() for item in table_html.select('td.no')] 
        number_data = np.array(inner_data) 
        
        # 가로 x 세로 크기에 맞게 행렬화 
        number_data.resize(len(no_data), len(header_data )) 
        
        # 한 페이지에서 얻은 정보를 모아 DataFrame로 만들어 리턴 
        df = pd.DataFrame(data=number_data, columns=header_data ) 
        return df 
    
    def main_crawl  (self,code):
        # total_page을 가져오기 위한 requests 
        res = requests.get(self.BASE_URL + str(code) + "&page=" + str(self.START_PAGE)) 
        page_soup = BeautifulSoup(res.text, 'lxml') 
        
        # total_page 가져오기 
        total_page_num = page_soup.select_one('td.pgRR > a') 
        total_page_num = int(total_page_num.get('href').split('=')[-1]) 
        
        #가져올 수 있는 항목명들을 추출 
        ipt_html = page_soup.select_one('div.subcnt_sise_item_top') 
        
        global fields 
        fields = [item.get('value') for item in ipt_html.select('input')] 
        
        # page마다 정보를 긁어오게끔 하여 result에 저장 
        result = [self.crawl(code,str(page)) for page in range(1,total_page_num+1)] 
      
        
        # page마다 가져온 정보를 df에 하나로 합침 
        df = pd.concat(result, axis=0,ignore_index=True) 
        
        # N/A제거
        df= df.fillna(0)
        # 우선주의 경우 매출액부터 본주를 따라가서 안나옴(제거를 해야 할듯한데 잘 안된다.)
        df = df.dropna(axis=0)
        df = df[df['매출액'] != 'N/A']
        df = df[df['자산총계'] != 'N/A']
        df = df[df['부채총계'] != 'N/A']
        df = df[df['영업이익'] != 'N/A']
        df = df[df['당기순이익'] != 'N/A']
        df = df[df['주당순이익'] != 'N/A']
        df = df[df['보통주배당금'] != 'N/A']
        df = df[df['매출액증가율'] != 'N/A']
        df = df[df['영업이익증가율'] != 'N/A']
        df = df[df['외국인비율'] != 'N/A']
        df = df[df['PER'] != 'N/A']
        df = df[df['ROE'] != 'N/A']
        df = df[df['ROA'] != 'N/A']
        df = df[df['PBR'] != 'N/A']
        df = df[df['유보율'] != 'N/A']
    
        print(df.head)
        
        # DataFrame의 문자열 df.column.str.replace(',', '').astype('int64') 메소드를  이용하여 데이터 형태 및 유형 변환하기
        df['현재가']     = df.현재가.str.replace(',', '').astype('int64')
        df['전일비']     = df.전일비.str.replace(',', '').astype('int64')
    #    df['등락률']     = df.등락률.str.replace(',', '').astype('float64')
    #    df['등락률']     = df.등락률.str.replace('%', '').astype('float64')
        df['액면가']     = df.액면가.str.replace(',', '').astype('int64')
        df['거래량']     = df.거래량.str.replace(',', '').astype('int64')
        df['거래대금']   = df.거래대금.str.replace(',', '').astype('int64')
        df['전일거래량'] = df.전일거래량.str.replace(',', '').astype('int64')
        df['시가']       = df.시가.str.replace(',', '').astype('int64')
        df['고가']       = df.고가.str.replace(',', '').astype('int64')
        df['저가']       = df.저가.str.replace(',', '').astype('int64')
        df['매수호가']   = df.매수호가.str.replace(',', '').astype('int64')
        df['매도호가']   = df.매도호가.str.replace(',', '').astype('int64')
        df['매수총잔량'] = df.매수총잔량.str.replace(',', '').astype('int64')
        df['매도총잔량'] = df.매도총잔량.str.replace(',', '').astype('int64')    
        df['상장주식수']   = df.상장주식수.str.replace(',', '').astype('int64')
        df['시가총액']     = df.시가총액.str.replace(',', '').astype('int64')
        
        # N/A 가 있어서 처리를 해야함
        df['매출액']       = df.매출액.str.replace(',', '').astype('int64')
        df['자산총계']     = df.자산총계.str.replace(',', '').astype('int64')
        df['부채총계']     = df.부채총계.str.replace(',', '').astype('int64')
        df['영업이익']     = df.영업이익.str.replace(',', '').astype('int64')
        df['당기순이익']   = df.당기순이익.str.replace(',', '').astype('int64')
        df['주당순이익']   = df.주당순이익.str.replace(',', '').astype('int64')
        df['보통주배당금'] = df.보통주배당금.str.replace(',', '').astype('int64')
        df['매출액증가율']  = df.매출액증가율.str.replace(',', '').astype('float64')
        df['영업이익증가율']  = df.영업이익증가율.str.replace(',', '').astype('float64')
        df['외국인비율']      = df.외국인비율.str.replace(',', '').astype('float64')
        df['PER']            = df.PER.str.replace(',', '').astype('float64')    
        df['ROE']            = df.ROE.str.replace(',', '').astype('float64')   
        df['ROA']            = df.ROA.str.replace(',', '').astype('float64')  
        df['PBR']            = df.PBR.str.replace(',', '').astype('float64')  
        df['유보율']         = df.유보율.str.replace(',', '').astype('float64')   
        # 엑셀로 내보내기     
        df.to_excel('NaverFinance_all.xlsx') 
            
       # DB저장
        from sqlalchemy import create_engine
        
        # echo=True를 선언할 경우 실제 테이블 생성 쿼리문을 보여준다
        engine = create_engine('sqlite:///itm_master.db', echo=True)
        
        #1. SQLite DB에 연결
        #SQLite DB에 저장하기 위해 DB와 연결을 한다
        con = sqlite3.connect("./itm_master.db")
        cursor = con.cursor()
        
        # DB CREAETE
        cursor.execute("drop table company_sise_all ")
        cursor.execute("create table company_sise_all (영업일,종목명,현재가,전일비,등락률,액면가,거래량,거래대금,전일거래량,시가,고가,저가,매수호가,매도호가,매수총잔량,매도총잔량,상장주식수,시가총액,매출액,자산총계,부채총계,영업이익,당기순이익,주당순이익,보통주배당금,매출액증가율,영업이익증가율,외국인비율,PER,ROE,ROA,PBR,유보율)")
        cursor.execute("delete from  company_sise_all ")
        # 지우고 다시 시작하자
        con.commit()    
    
       
        
        # 2. to_sql함수를 이용해서 DB에 저장    
        
        # sql 문장들
        for ix, r in df.iterrows():
           # print (r)
           values=  u"('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',cast('%s' as float),cast('%s' as float),cast('%s' as float),'%f','%f')" % ( 
               '20200603',r['종목명'], r['현재가'], r['전일비'], r['등락률']
               , r['액면가'], r['거래량'], r['거래대금'], r['전일거래량'], r['시가']
               , r['고가'], r['저가'], r['매수호가'], r['매도호가'], r['매수총잔량']
               , r['매도총잔량'], r['상장주식수'], r['시가총액'], r['매출액'], r['자산총계']
               , r['부채총계'], r['영업이익'], r['당기순이익'], r['주당순이익'] , r['보통주배당금']
               , r['매출액증가율'], r['영업이익증가율'], r['외국인비율'] , r['PER'], r['ROE']
               , r['ROA'], r['PBR'], r['유보율'] )
           
           #values=  u"('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'))"% (
           #        '20200603',r['종목명'], r['현재가'], r['전일비'], r['등락률'], r['액면가'], r['거래량'], r['거래대금'], r['전일거래량'], r['시가'], r['고가'], r['저가'], r['매수호가'], r['매도호가'], r['매수총잔량'], r['매도총잔량'], r['상장주식수'], r['시가총액'],r['매출액'] )
            #print(values)
           insert_sql = u"insert into company_sise_all( 영업일,종목명,현재가,전일비,등락률,액면가,거래량,거래대금,전일거래량,시가,고가,저가,매수호가,매도호가,매수총잔량,매도총잔량,상장주식수,시가총액,매출액,자산총계,부채총계,영업이익,당기순이익,주당순이익,보통주배당금,매출액증가율,영업이익증가율,외국인비율,PER,ROE,ROA,PBR,유보율 ) values %s ;" % (
                    u"".join(values))
           print (insert_sql)
           con.execute(insert_sql)
           con.commit()    
      
    
    def sise_crawling  (self):
        self.main_crawl(self.KOSPI_CODE)