# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:32:59 2020

@author: 정낙현
"""
# 참조 
# https://kin.naver.com/qna/detail.nhn?d1id=1&dirId=10402&docId=351159645&qb=cHl0aG9uIHB5UVQgbWRp&enc=utf8&section=kin&rank=1&search_sort=0&spq=0

# =============================================================================
# 관련모듈 import
# =============================================================================

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper,
        QSize, QTextStream, Qt)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas_datareader.data as web
import pandas_datareader as pdr
import pandas as pd
from pandas import Series, DataFrame
import sqlite3
import backtrader as bt
from datetime import datetime

import backtrader as bt
# 백트레이딩 전략 클래스 정의
import quant.myquant_bt_strategy as BT_st

# 크롤링 라이브러리 가져오기
from quant.company_info            import Class_CompanyInfo
#from company_balance         import Class_CompanyBalance
from quant.company_sise_all        import Class_CompanySiseAll
from quant.market_index            import Class_MarketIndex
from quant.market_world_index      import Class_MarketWorldIndex
from quant.naver_realtime          import Class_NaverRealtime
from TextRank.TextRank             import Class_TextRank
from showntell               import MdiChild_ShowNTell

import argparse
# Vocabulary 를 import 해야 정상 작동함
from build_vocab import Vocabulary
# 인공지능 학습/예측 라이브러리 가져오기
from show_torch        import Class_Torch
# sentimental analysis
from show_sentiment   import Class_Sentiment
# logo analysis
from show_logo   import Class_Logo
# =============================================================================
# MDI Child  Class 정의부분
# =============================================================================
# 그래프 테스트
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(600, 200, 1200, 600)  # setGeometry(int x, int y, int w, int h)
        self.setWindowTitle("주식차트")
        self.setWindowIcon(QIcon('icon.png'))

        self.lineEdit = QLineEdit()
        self.pushButton = QPushButton("차트그리기")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.canvas)

        # Right Layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.pushButton)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def pushButtonClicked(self):
        code = self.lineEdit.text()
        # https://wendys.tistory.com/174 여기 예제를 참고해서 종목명으로도 가능하게 하자
        #web.DataReader(code + ".ks", "yahoo")
        code = code + '.KS'
        # get_data_yahoo API를 통해서 yahho finance의 주식 종목 데이터를 가져온다.
        df = pdr.get_data_yahoo(code)
        df['MA5'] = df['Adj Close'].rolling(window=5).mean()
        df['MA20'] = df['Adj Close'].rolling(window=20).mean()
        df['MA60'] = df['Adj Close'].rolling(window=60).mean()
        #df['MA100'] = df['Adj Close'].rolling(window=100).mean()
        #df['MA200'] = df['Adj Close'].rolling(window=200).mean()

        ax = self.fig.add_subplot(111)
        ax.plot(df.index, df['Adj Close'], label='Adj Close')
        ax.plot(df.index, df['MA5'], label='MA5')
        ax.plot(df.index, df['MA20'], label='MA20')
        ax.plot(df.index, df['MA60'], label='MA60')
        #ax.plot(df.index, df['MA100'], label='MA100')
        #ax.plot(df.index, df['MA200'], label='MA200')
        ax.legend(loc='upper right')
        ax.grid()

        self.canvas.draw()


class MyTable(QWidget):

    kospi_top5 = {
            'code': ['005930', '0006600', '005380', '035420', '033780'],
            'name': ['삼성전자', 'SK하이닉스', '현대차', 'NAVER', 'KT&G'],
            'cprice': ['52,300', '85,200', '103,500', '242,000', '83,200']
        } 
    column_idx_lookup = {'code': 0, 'name': 1, 'cprice': 2}
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self._mainwin = parent

        self.__make_table()
        self.__make_layout()

    def __make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)

        grid = QGridLayout()
        vbox.addLayout(grid)
        # grid.setSpacing(20)

        self.setLayout(vbox)

##        self.setGeometry(200, 200, 1000, 1000)
        self.setWindowTitle("My Fortfolio")


    def __make_table(self):
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        #self.table.resize(290, 290)
        self.table.setRowCount(5)
        self.table.setColumnCount(3)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

        # column header 명 설정.
        column_headers = ['종목코드', '종목명', '종가']
        self.table.setHorizontalHeaderLabels(column_headers)
        #self.table.setHorizontalHeaderLabels(["코드", "종목명"])
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)  # header 정렬 방식

    def setTableWidgetData(self):
        column_headers = ['종목코드', '종목명', '종가']
        self.table.setHorizontalHeaderLabels(column_headers)

        for k, v in self.kospi_top5.items():
            col = self.column_idx_lookup[k]
            for row, val in enumerate(v):
                item = QTableWidgetItem(val)
                if col == 2:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

# 상장종목 데이터 조회
class ListItmTable(QWidget):

    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self._mainwin = parent

        self.__make_table()
        self.__make_layout()

    def __make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)

        grid = QGridLayout()
        vbox.addLayout(grid)
        # grid.setSpacing(20)

        self.setLayout(vbox)

        self.setGeometry(600, 200, 1200, 600)
        self.setWindowTitle("상장종목리스트")


    def __make_table(self):
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        #self.table.resize(500, 500)
        self.table.setRowCount(5000)
        self.table.setColumnCount(9)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

        #column_headers = ['종목코드', '종목명', '종가']
        #self.table.setHorizontalHeaderLabels(column_headers)
        #self.table.setHorizontalHeaderLabels(["코드", "종목명"])
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)  # header 정렬 방식

    def setTableWidgetData(self):
        # https://stackoverflow.com/questions/22941184/how-to-display-data-from-mysql-database-in-table-using-pyqt 참고
        # column header 명 설정.
        column_headers1 = ['회사명','종목코드','업종','주요제품', '상장일', '결산월','대표자명','홈페이지','지역']
        self.table.setHorizontalHeaderLabels(column_headers1)

        con = sqlite3.connect("./itm_master.db")
        cur = con.cursor()
        cur.execute("SELECT  * FROM company_info order by 종목코드 ")
        allSQLRows= cur.fetchall()
        self.table.setRowCount(len(allSQLRows)) ##set number of rows
        self.table.setColumnCount(9) ##this is fixed for myTableWidget, ensure that both of your tables, sql and qtablewidged have the same number of columns
        #print("allSQLRows=",allSQLRows)
        print("grid...start")
        row = 0
        #while True:
        #    sqlRow = cur.fetchall()
        for sqlRow in allSQLRows:
            if sqlRow == None:
                break ##stops while loop if there is no more lines in sql table
            for col in range(0, 9): ##otherwise add row into tableWidget
                #print("sqlRow[",col,"]=",sqlRow[col])
                self.table.setItem(row, col, QTableWidgetItem(sqlRow[col]))
            row += 1

        print("grid...end")       
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()    
        # 창크기 고정
        self.table.setFixedSize(650, 500)
        con.close()
        
# 마법공식
class MagicListtable(QWidget):

    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self._mainwin = parent

        self.__make_table()
        self.__make_layout()

    def __make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)

        grid = QGridLayout()
        vbox.addLayout(grid)
        # grid.setSpacing(20)

        self.setLayout(vbox)

        #setGeometry(int x, int y, int w, int h)
        self.setGeometry(600, 200, 1200, 600) 
        self.setWindowTitle("마법공식( by Joel Greenblatt)")


    def __make_table(self):
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.resize(1200, 800)
        self.table.setRowCount(2000)
        self.table.setColumnCount(9)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

        
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)  # header 정렬 방식

    def setTableWidgetData(self):
        # https://stackoverflow.com/questions/22941184/how-to-display-data-from-mysql-database-in-table-using-pyqt 참고
        # column header 명 설정.
        column_headers = ['종목명','현재가','상장주식수','시가총액', 'PER', 'ROE','ROA','PBR']
        self.table.setHorizontalHeaderLabels(column_headers)

        con = sqlite3.connect("./itm_master.db")
        cur = con.cursor()
        cur.execute("SELECT 종목명,현재가,상장주식수,시가총액, cast(PER as char) PER , cast(ROE as char) ROE , cast(ROA as char ) ROA ,PBR FROM company_sise_all where PER  >= 1   ORDER BY PER asc , roa desc ")
        allSQLRows= cur.fetchall()
        self.table.setRowCount(len(allSQLRows)) ##set number of rows
        self.table.setColumnCount(8) ##this is fixed for myTableWidget, ensure that both of your tables, sql and qtablewidged have the same number of columns
        #print("allSQLRows=",allSQLRows)
        print("grid...start")
        row = 0
        #while True:
        #    sqlRow = cur.fetchall()
        for sqlRow in allSQLRows:
            if sqlRow == None:
                break ##stops while loop if there is no more lines in sql table
            for col in range(0, 8): ##otherwise add row into tableWidget
                #print("sqlRow[",col,"]=",sqlRow[col])
                self.table.setItem(row, col, QTableWidgetItem(sqlRow[col]))
            row += 1

        print("grid...end")       
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()      
        # 창크기 고정
        self.table.setFixedSize(600, 500)
        con.close()    
        
# 가치투자 (Benjamin Graham )
class BenjaminListtable(QWidget):

    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self._mainwin = parent

        self.__make_table()
        self.__make_layout()

    def __make_layout(self):
        #vbox = QVBoxLayout()
        #vbox.addWidget(self.table)

        #grid = QGridLayout()
        #vbox.addLayout(grid)
        # grid.setSpacing(20)

        #self.setLayout(vbox)

        #setGeometry(int x, int y, int w, int h)
        self.setGeometry(600, 200, 1200, 600) 
        self.setWindowTitle("가치투자 (by Benjamin Graham )")
                
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.table)
        grid = QGridLayout()
        leftLayout.addLayout(grid)
        #self.setLayout(leftLayout)

        # Right Layout
        rightLayout = QVBoxLayout()
        rightLayout.addStretch(1)
        
        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)        


    def __make_table(self):
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.resize(1200, 800)
        self.table.setRowCount(2000)
        self.table.setColumnCount(9)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

        
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)  # header 정렬 방식

    def setTableWidgetData(self):
        # https://stackoverflow.com/questions/22941184/how-to-display-data-from-mysql-database-in-table-using-pyqt 참고
        # column header 명 설정.
        column_headers = ['종목명','현재가','상장주식수','시가총액', 'PER', 'ROE','ROA','PBR']
        self.table.setHorizontalHeaderLabels(column_headers)

        con = sqlite3.connect("./itm_master.db")
        cur = con.cursor()
        cur.execute("SELECT 종목명,현재가,상장주식수,시가총액, cast(PER as char) PER , cast(ROE as char) ROE , cast(ROA as char ) ROA ,PBR FROM company_sise_all where PER  >= 1  and PER < 15 and cast(PBR as float ) < 1.5 and PER * cast(PBR as float )  < 22 ORDER BY  PBR asc , PER asc  ")
        allSQLRows= cur.fetchall()
        self.table.setRowCount(len(allSQLRows)) ##set number of rows
        self.table.setColumnCount(8) ##this is fixed for myTableWidget, ensure that both of your tables, sql and qtablewidged have the same number of columns
        #print("allSQLRows=",allSQLRows)
        print("grid...start")
        row = 0
        #while True:
        #    sqlRow = cur.fetchall()
        for sqlRow in allSQLRows:
            if sqlRow == None:
                break ##stops while loop if there is no more lines in sql table
            for col in range(0, 8): ##otherwise add row into tableWidget
                #print("sqlRow[",col,"]=",sqlRow[col])
                self.table.setItem(row, col, QTableWidgetItem(sqlRow[col]))
            row += 1

        print("grid...end")       
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        # 창크기 고정
        self.table.setFixedSize(540, 500)
        con.close()   
        
         
# 이기는투자 (Peter Lynch)
class PeterListtable(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self._mainwin = parent

        self.__make_table()
        self.__make_layout()

    def __make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)

        grid = QGridLayout()
        vbox.addLayout(grid)
        # grid.setSpacing(20)

        self.setLayout(vbox)

        #setGeometry(int x, int y, int w, int h)
        self.setGeometry(600, 200, 1200, 600) 
        self.setWindowTitle("이기는투자 (by Peter Lynch )")


    def __make_table(self):
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.resize(1200, 800)
        self.table.setRowCount(2000)
        self.table.setColumnCount(9)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

        
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)  # header 정렬 방식

    def setTableWidgetData(self):
        # https://stackoverflow.com/questions/22941184/how-to-display-data-from-mysql-database-in-table-using-pyqt 참고
        # column header 명 설정.
        column_headers = ['종목명','현재가','상장주식수','시가총액', 'PER', 'ROE','ROA','PBR','PER/ROE']
        self.table.setHorizontalHeaderLabels(column_headers)

        con = sqlite3.connect("./itm_master.db")
        cur = con.cursor()
        cur.execute("SELECT 종목명,현재가,상장주식수,시가총액, cast(PER as char) PER , cast(ROE as char) ROE , cast(ROA as char ) ROA ,PBR ,  cast ((PER/ ROE)as char) FROM company_sise_all where PER  >= 1 and ROE > 0  ORDER BY (PER/ ROE)  asc ")
        allSQLRows= cur.fetchall()
        self.table.setRowCount(len(allSQLRows)) ##set number of rows
        self.table.setColumnCount(9) ##this is fixed for myTableWidget, ensure that both of your tables, sql and qtablewidged have the same number of columns
        #print("allSQLRows=",allSQLRows)
        print("grid...start")
        row = 0
        #while True:
        #    sqlRow = cur.fetchall()
        for sqlRow in allSQLRows:
            if sqlRow == None:
                break ##stops while loop if there is no more lines in sql table
            for col in range(0, 9): ##otherwise add row into tableWidget
                #print("sqlRow[",col,"]=",sqlRow[col])
                self.table.setItem(row, col, QTableWidgetItem(sqlRow[col]))
            row += 1

        print("grid...end")       
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()        
        # 창크기 고정
        self.table.setFixedSize(650, 500)
        con.close()            
                
# Back Testing
class BackTesting(QWidget):
    BTchart_view=False
    BTStrategy  = 'Momentum'
    
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(600, 200, 1200, 600)
        self.setWindowTitle("BackTesting")
        self.setWindowIcon(QIcon('icon.png'))

   
        
        #try:
        #    %matplotlib 
        #except Exception:
        #    pass
        import matplotlib.pyplot as plt
        
        self.textLabel1 = QLabel("종목코드 ", self)
        self.lineEdit   = QLineEdit("005930",self)
        #self.lineEdit.textChanged.connect(self.lineEditChanged)
        #self.textLabel2 = QLabel("시작일 ", self)
        #self.textLabel3 = QLabel("종료일 ", self)        
        self.textLabel5 = QLabel("초기자금 ", self)        
        self.lineEdit2  = QLineEdit("10000000", self)
        #self.lineEdit.textChanged.connect(self.lineEditChanged)
        self.pushButton = QPushButton("Back Testing")
        self.pushButton.clicked.connect(self.pushButtonClicked)  
        
        # Chart 를 보여줄 Label        
        self.lbl_picture = QLabel()        
        self.lbl_picture.setFixedSize(600, 400) 
        self.qPixmapFileVar = QPixmap()
        self.lbl_picture.setPixmap(self.qPixmapFileVar)
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.lbl_picture)
        
        # BackTrader Chart 를볼꺼면 체크
        self.BTchart_view=False
        self.checkBox1 = QCheckBox("BTChart View", self)
        self.checkBox1.stateChanged.connect(self.checkBoxState)

        # 전략 선택 Radio 버튼
        self.BTStrategy  = 'Momentum'
        #self.groupBox = QGroupBox("백테스트 전략", self)
        #self.groupBox.resize(280, 80)
        self.textLabel4 = QLabel("전략선택 ", self)                
        self.radio1 = QRadioButton("Momentum", self)
        self.radio1.setChecked(True)
        self.radio2 = QRadioButton("SmaCross", self)
        self.radio3 = QRadioButton("firstStrategy", self)
        self.radio1.clicked.connect(self.radioButtonClicked)
        self.radio2.clicked.connect(self.radioButtonClicked)
        self.radio3.clicked.connect(self.radioButtonClicked)

        # Right Layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.textLabel1)
        rightLayout.addWidget(self.lineEdit)
        #rightLayout.addWidget(self.textLabel2)
        #rightLayout.addWidget(self.textLabel3)
        rightLayout.addWidget(self.textLabel5)
        rightLayout.addWidget(self.lineEdit2)
        rightLayout.addWidget(self.pushButton)
        rightLayout.addWidget(self.checkBox1)
        #rightLayout.addWidget(self.groupBox)
        rightLayout.addWidget(self.textLabel4)
        rightLayout.addWidget(self.radio1)
        rightLayout.addWidget(self.radio2)
        rightLayout.addWidget(self.radio3)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)
        
    def radioButtonClicked(self):
            if self.radio1.isChecked():
                self.BTStrategy = "Momentum"
            elif self.radio2.isChecked():
                self.BTStrategy = "SmaCross"
            elif self.radio3.isChecked():
                self.BTStrategy = "firstStrategy"
            else:
                pass
        
    def checkBoxState(self):
        if self.checkBox1.isChecked() == True:
            self.BTchart_view = True
        else:
            self.BTchart_view = False

    def pushButtonClicked(self):
        code = self.lineEdit.text()
        # BackTesting https://jsp-dev.tistory.com/category/Python/Stock
        # https://wendys.tistory.com/174 여기 예제를 참고해서 종목명으로도 가능하게 하자
        #web.DataReader(code + ".ks", "yahoo")
        code = code + '.KS' # '005930.KS'
        # get_data_yahoo API를 통해서 yahho finance의 주식 종목 데이터를 가져온다.
        #df = pdr.get_data_yahoo(code)
        
        money = self.lineEdit2.text()
        
        realmoney = 10000000
        print ('code=',code)
        print ('money=',money)
        print ('realmoney=',realmoney)
        
        cerebro = bt.Cerebro() # create a "Cerebro" engine instance
        
        data = bt.feeds.YahooFinanceData(dataname=code,
                                         fromdate=datetime(2019, 1, 1),
                                         todate=datetime(2020, 6, 12))
        
        print(data)

        cerebro.adddata(data) #데이터삽입
        #cerebro.broker.setcash(1000000) # 초기 자본 설정
        cerebro.broker.setcash(realmoney) # 초기 자본 설정
        cerebro.broker.setcommission(commission=0.00015) # 매매 수수료는 0.015% 설정

        # 전략 선택
        if self.BTStrategy == "Momentum":
            cerebro.addstrategy(BT_st.Momentum)         
        elif self.BTStrategy == "SmaCross":
            cerebro.addstrategy(BT_st.SmaCross)   
        elif self.BTStrategy == "firstStrategy":
            cerebro.addstrategy(BT_st.firstStrategy)     
        else :
            pass

       
        
        print('Starting Portfolio Value: %.2f'%cerebro.broker.getvalue())
        cerebro.run() # 수행
        print('Final Portfolio Value:%2f'%cerebro.broker.getvalue())
        
        
        result =cerebro.run() # 백테스팅 시작
        
        if self.BTchart_view ==False :
            figure = cerebro.plot(style = 'candlebars') [0] [0]    
        else:
            # backtrader 자체 chart 보여줌
            figure = cerebro.plot(iplot=False,style = 'candlebars') [0] [0]       
   
        
        # print('a=',type(a))
        print('cerebro=',type(cerebro))
        print('result=',result)
        print('result=',type(result))
        
        figure.savefig ( 'backtesting.png')
        
        #QPixmap 객체 생성 후 이미지 파일을 이용하여 QPixmap에 사진 데이터 Load하고, Label을 이용하여 화면에 표시
        self.qPixmapFileVar.load("backtesting.png")
        self.qPixmapFileVar = self.qPixmapFileVar.scaledToWidth(600)
        self.lbl_picture.setPixmap(self.qPixmapFileVar)   
        
        
# 주가예측
class StockPredict(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(600, 200, 1400, 600)
        self.setWindowTitle("주가예측")
        self.setWindowIcon(QIcon('icon.png'))

        self.lineEdit = QLineEdit()
        self.pushButton = QPushButton("주가예측")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.canvas)

        # Right Layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.pushButton)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def pushButtonClicked(self):
        code = self.lineEdit.text()
        # https://wendys.tistory.com/174 여기 예제를 참고해서 종목명으로도 가능하게 하자
        #web.DataReader(code + ".ks", "yahoo")
        code = code + '.KS'
        
        #import fix_yahoo_finance as yf
        import yfinance as yf 
        yf.pdr_override()
        
        from pandas_datareader import data
        import datetime
        
        start_date = '2008-01-01'
        name = code
        nc = data.get_data_yahoo(name, start_date)
        nc_trunc = nc[:'2020-06-05']
        
        df = pd.DataFrame({'ds':nc_trunc.index, 'y':nc_trunc['Close']})
        df.reset_index(inplace=True)
        del df['Date']
        
        from fbprophet import Prophet
        
        m = Prophet()
        m.fit(df);
        future = m.make_future_dataframe(periods=365*2)
        forecast = m.predict(future)
        
        plt.figure(figsize=(12, 6))

        
        ax = self.fig.add_subplot(111)
        ax.plot(nc.index, nc['Close'], label='real')
        ax.plot(forecast['ds'], forecast['yhat'], label='forecast')
        ax.grid()
        ax.legend()  
        
        #ax.legend(loc='upper right')
        
        ax.grid()

        self.canvas.draw()

# 실시간검색어
class NaverReal(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(600, 200, 1400, 600)
        self.setWindowTitle("실시간검색어")
        self.setWindowIcon(QIcon('icon.png'))

        #self.lineEdit = QLineEdit()
        self.pushButton = QPushButton("실시간검색어")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        #self.fig = plt.Figure()
        #self.canvas = FigureCanvas(self.fig)
        self.textEdit = QTextEdit()

        leftLayout = QVBoxLayout()
        #leftLayout.addWidget(self.canvas)
        leftLayout.addWidget(self.textEdit)

        # Right Layout
        rightLayout = QVBoxLayout()
        #rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.pushButton)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def pushButtonClicked(self):
        rank_text = Class_NaverRealtime()
        realtext = rank_text.realtimetext_crawling()
        self.textEdit.setText(realtext)

# 뉴스요약
class NewsRankText(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(600, 200, 1400, 600)
        self.setWindowTitle("뉴스요약")
        self.setWindowIcon(QIcon('icon.png'))

        #self.lineEdit = QLineEdit()
        self.pushButton = QPushButton("뉴스요약")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        #self.fig = plt.Figure()
        #self.canvas = FigureCanvas(self.fig)
        self.lineEdit = QLineEdit()
        #self.textEdit1 = QTextEdit()
        self.textEdit2 = QTextEdit()

        leftLayout = QVBoxLayout()
        #leftLayout.addWidget(self.canvas)
        leftLayout.addWidget(self.lineEdit)
        #leftLayout.addWidget(self.textEdit1)
        leftLayout.addWidget(self.textEdit2)

        # Right Layout
        rightLayout = QVBoxLayout()
        #rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.pushButton)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def pushButtonClicked(self):
        article = self.lineEdit.text()
        #article = "금융계열사를 거느린 삼성, 현대차, 미래에셋 등 7개 그룹의 자본 적정성을 깐깐하게 보는 금융그룹 통합감독제도가 이달부터 시범 운영에 들어간 가운데, 특정 기업의 지배구조를 압박하는 수단이 될 수 있다는 우려가 나온다. 현재는 금융당국이 자본 적정성 기준선을 100%로 정했지만 향후 상향할 가능성이 있기 때문이다. 새로운 기준이 도입되면 대다수 금융그룹의 자본 적정성이 100%대로 떨어져, 향후 기준선을 상향할 경우 이들 금융그룹엔 큰 부담이 될 수밖에 없다.금융당국 관계자는 2일 문화일보와의 통화에서 “지금 당장은 시범 운영 기간이라 기준선인 100% 이외의 숫자를 제시하지 않았지만 향후 다른 숫자를 제시할 가능성도 있다”면서 “하반기 현장실사와 자본 규제안 세부 기준을 확정하면서 숫자가 달라질 수 있다”고 말했다. 금융당국은 집중위험과 전이위험 산출 기준을 올해 말까지 확정하고 내년 6월까지 모범규준을 수정·보완 계획인데 이 과정에서 자본 적정성 비율을 상향할 가능성을 시사한 셈이다.금융당국은 100%는 최소기준일 뿐 충분한 수준으로는 생각하고 있지 않다. 실제 보험업법의 지급여력비율(RBC) 기준은 100%지만 금융당국은 보험사의 RBC 비율이 150% 밑으로 떨어지면 자본확충을 유도한다.은행권도 국제결제은행(BIS) 기준 자기자본비율 기준치는 8%지만 금융당국의 추가자본확충 요구에 평균 15%대의 비율을 유지하고 있다.만약 금융당국이 금융그룹에 대한 자본 적정성 비율을 현행 100%에서 상향하면 삼성, 현대차, 미래에셋 등 대다수 금융그룹은 이를 맞추기 위해 자본을 확충하거나 비금융 계열사 주식을 매각해야 한다.특히 삼성의 경우 삼성생명이 보유한 삼성전자의 주식을 ‘시가’로 계산한 집중위험 항목을 반영하면 자본 적정성 비율은 110%대로 떨어지는 것으로 나타났다. 20조 원에 달하는 자본을 확충하긴 쉽지 않은 만큼 삼성생명은 삼성전자 주식을 매각하는 방식으로 자본 적정성을 맞출 가능성이 커지는 셈이다.일각에선 금융그룹통합감독제도가 보험업법을 대신해 삼성의 지배구조 개편을 압박하는 데 활용될 것이란 전망도 나온다. 현재 국회에는 보험사가 보유한 계열사 주식을 취득원가 아닌 시가로 평가하는 보험업법 개정안이 발의돼 있는데 야당의 반대로 통과는 어려운 상황이다.국회 정무위 관계자는 “현재 보험업법 통과가 어려워 보이기는 하지만, 이 법이 개정되면 삼성생명은 자산의 3%가 넘는 20조 원가량의 삼성전자 주식을 팔아야 한다”고 말했다.황혜진 기자 best@munhwa.com[Copyrightⓒmunhwa.com '대한민국 오후를 여는 유일석간 문화일보' 무단 전재 및 재배포 금지( 구독신청:02)3701-5555 )]"
        try :
            textrank = Class_TextRank(article)
            keyword = textrank.keywords()

            #self.textEdit.setText(keyword)
            row_text =''
            for row in textrank.summarize(3):
                print(row)
                row_text += row


            self.textEdit2.setText(row_text)

        except:
            pass

# 이미지캡셔닝
class ImageCaption(QWidget):
    def __init__(self):
        super().__init__()
        self.Label = QLabel()
        self.setupUI()


    def setupUI(self):
        self.setGeometry(600, 200, 1400, 600)
        self.setWindowTitle("이미지캡셔닝")
        self.setWindowIcon(QIcon('icon.png'))

        #self.lineEdit = QLineEdit()
        self.pushButton = QPushButton("이미지 로드")
        self.pushButton2 = QPushButton("이미지 읽어줘")
        self.pushButton3 = QPushButton("로고 읽어줘")

        self.pushButton.clicked.connect(self.LoadImage)
        self.pushButton2.clicked.connect(self.pushButtonClicked)
        self.pushButton3.clicked.connect(self.LogoImage)

        # Create widget
        self.Label = QLabel(self)
        self.pixmap = QPixmap("png/image.png")
        self.Label.setPixmap(self.pixmap)
        self.resize(self.pixmap.width(), self.pixmap.height())

        # TextEdit
        self.textEdit = QTextEdit()
        self.textLabel1 = QLabel("positive ", self)
        self.textEdit3 = QLineEdit()
        self.textLabel2 = QLabel("neutral ", self)
        self.textEdit4 = QLineEdit()
        self.textLabel3 = QLabel("negative ", self)
        self.textEdit5 = QLineEdit()

        leftLayout = QVBoxLayout()
        #leftLayout.addWidget(self.canvas)
        leftLayout.addWidget(self.Label)
        leftLayout.addWidget(self.textEdit)

        # Right Layout
        rightLayout = QVBoxLayout()
        #rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.pushButton)
        rightLayout.addWidget(self.pushButton2)
        rightLayout.addWidget(self.pushButton3)
        rightLayout.addWidget(self.textLabel1)
        rightLayout.addWidget(self.textEdit3)
        rightLayout.addWidget(self.textLabel2)
        rightLayout.addWidget(self.textEdit4)
        rightLayout.addWidget(self.textLabel3)
        rightLayout.addWidget(self.textEdit5)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def pushButtonClicked(self):
        self.pixmap.save("png/image.png")
        # 예측
        self.Predict()


    # 이미지를 불러온다
    def LoadImage(self):
        # 일단 초기화부터 하자
        #self.Label = QLabel()
        self.Label.clear()
        self.textEdit3.clear()
        self.textEdit4.clear()
        self.textEdit5.clear()

        selection = QMessageBox.question(self, '확인', "파일을 로드 하시겠습니까?", QMessageBox.Yes, QMessageBox.No)

        if selection == QMessageBox.Yes:  # 파일로드
            try:
                fname = QFileDialog.getOpenFileName(self)
                print("fname=", fname)

            except Exception as e:
                self._stateexpression.setText(e)
                QMessageBox.about(self, "경고", e)

            else:
                # 보여주기
                self.pixmap = QPixmap(fname[0])
                self.pixmap = self.pixmap.scaled(400, 400)
                #self.DrawingFrame.setCurrentWidget(self.Label)
                self.Label.setPixmap(self.pixmap)
                self.resize(self.pixmap.width(), self.pixmap.height())

                #self.canvas.setPixmap(self.pixmap)

                self.Label.show()

    #  로고읽기
    def LogoImage(self):
        # 예측
        self.pixmap.save("png/image.png")

        self.Logo_detect()

        self.pixmap = QPixmap("png/result1.png")
        self.pixmap = self.pixmap.scaled(400, 400)
        self.DrawingFrame.setCurrentWidget(self.Label)
        self.Label.setPixmap(self.pixmap)

        self.Label.show()

    # 로고검출
    def Logo_detect(self):

        print("Logo_detect")
        self.lib_logo = Class_Logo()
        try:
            self.lib_logo.load_file("png/image.png")
            self.lib_logo.set_img("png/result1.png")
        except:
            pass

    def Predict(self):

        self.lib_torch = Class_Torch()
        self.lib_senti = Class_Sentiment()

        print("Predict")
        parser = argparse.ArgumentParser()
        parser.add_argument('--image', type=str, default='png/image.png', help='input image for generating caption')
        parser.add_argument('--encoder_path', type=str, default='models/encoder-10-3000.ckpt',
                            help='path for trained encoder')
        parser.add_argument('--decoder_path', type=str, default='models/decoder-10-3000.ckpt',
                            help='path for trained decoder')
        parser.add_argument('--vocab_path', type=str, default='data/vocab.pkl', help='path for vocabulary wrapper')

        # Model parameters (should be same as paramters in train.py)
        parser.add_argument('--embed_size', type=int, default=256, help='dimension of word embedding vectors')
        parser.add_argument('--hidden_size', type=int, default=512, help='dimension of lstm hidden states')
        parser.add_argument('--num_layers', type=int, default=1, help='number of layers in lstm')
        args = parser.parse_args()

        # 이미지캡셔닝
        try:
            pred = self.lib_torch.predict(args)
            # print(pred)
            # <start> <end> 를 제거해줌
            pred_txt = pred[7:len(pred) - 5]
            # print(pred_txt)
        except:
            pred_txt = ""

        # self.textEdit.setText("Predict : {}".format(pred_txt))
        self.textEdit.setText(pred_txt)

        # sentimental analysis
        try:
            senti = self.lib_senti.sentiment(pred_txt)
            print(senti)
            senti_pos = str(senti['pos'] * 100) + " %"
            senti_neu = str(senti['neu'] * 100) + " %"
            senti_neg = str(senti['neg'] * 100) + " %"
        except:
            senti = ""
            senti_pos = ""
            senti_neu = ""
            senti_neg = ""

        self.textEdit3.setText(senti_pos)      # positive
        self.textEdit4.setText(senti_neu)      # neutral
        self.textEdit5.setText(senti_neg)      # negative

        del pred
        del senti

    def Logo_detect(self):

        print("Logo_detect")

        try:
            self.lib_logo.load_file("png/image.png")
            self.lib_logo.set_img("png/result1.png")
        except:
            pass

    def Establish_Connections(self):

        # push button
        self.pushButton5.clicked.connect(self.LoadImage)
        self.pushButton6.clicked.connect(self.PredictImage)
        self.pushButton7.clicked.connect(self.LogoImage)


        # 데이터가져오기
class StockDataCrawling(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()


    def setupUI(self):
        self.setGeometry(600, 200, 1400, 600)
        self.setWindowTitle("Finance Data Crawling")
        self.setWindowIcon(QIcon('icon.png'))

        self.calendar = QCalendarWidget()
        #self.lineEdit = QLineEdit()
        self.pushButton1 = QPushButton("상장종목 회사정보 가져오기(거래소)")
        self.pushButton1.clicked.connect(self.pushButton1Clicked)
        self.pushButton2 = QPushButton("상장종목 재무제표 가져오기(네이버)")
        self.pushButton2.clicked.connect(self.pushButton2Clicked)        
        self.pushButton3 = QPushButton("상장종목 시세정보 가져오기(네이버)")
        self.pushButton3.clicked.connect(self.pushButton3Clicked)
        self.pushButton4 = QPushButton("Market Index 가져오기(네이버)")
        self.pushButton4.clicked.connect(self.pushButton4Clicked)
        self.pushButton5 = QPushButton("Market World Index 가져오기(네이버)")
        self.pushButton5.clicked.connect(self.pushButton5Clicked)
        #self.fig = plt.Figure()
        #self.canvas = FigureCanvas(self.fig)

        #leftLayout = QVBoxLayout()
        #leftLayout.addWidget(self.canvas)

        # Right Layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.calendar)
        #rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.pushButton1)
        rightLayout.addWidget(self.pushButton2)
        rightLayout.addWidget(self.pushButton3)
        rightLayout.addWidget(self.pushButton4)
        rightLayout.addWidget(self.pushButton5)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        #layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        #layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def pushButton1Clicked(self):
        # 상장종목 회사정보 가져오기(거래소)
        Company_Info = Class_CompanyInfo() 
        Company_Info.stock_crawling()
            
    def pushButton2Clicked(self):
       # Company_Balance = Class_CompanyBalance()
       # Company_Balance.balance_crawling()
        pass
    
    def pushButton3Clicked(self):
        Company_Sise_all = Class_CompanySiseAll()
        Company_Sise_all.sise_crawling()     
        
    def pushButton4Clicked(self):
        Market_Index = Class_MarketIndex()
        Market_Index.index_crawling()

    def pushButton5Clicked(self):
        Market_World_Index = Class_MarketWorldIndex()
        Market_World_Index.index_crawling()
        
# 종목별 재무제표 보기
class BalanceTable(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self._mainwin = parent

        self.__make_table()
        self.__make_layout()

    def __make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)

        grid = QGridLayout()
        vbox.addLayout(grid)
        # grid.setSpacing(20)

        self.setLayout(vbox)

        #setGeometry(int x, int y, int w, int h)
        self.setGeometry(600, 200, 1200, 600) 
        self.setWindowTitle("종목별 재무제표 ")


    def __make_table(self):
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.resize(1200, 800)
        self.table.setRowCount(2000)
        self.table.setColumnCount(12)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

        
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)  # header 정렬 방식

    def setTableWidgetData(self):
        # https://stackoverflow.com/questions/22941184/how-to-display-data-from-mysql-database-in-table-using-pyqt 참고
        # column header 명 설정.
        column_headers = ['종목코드','종목명','결산월','매출액', '매출원가', '매출총이익','영업이익','당기순이익','자산','부채','자본','현금흐름' ]
        self.table.setHorizontalHeaderLabels(column_headers)

        con = sqlite3.connect("./itm_master.db")
        cur = con.cursor()
        cur.execute("select b.종목코드,a.회사명 종목명, b.연도||'-'||b.월 결산월 , 매출액,매출원가,매출총이익,영업이익,당기순이익,자산,부채,자본,현금흐름 from company_balance b , company_info a where a.종목코드 = b.종목코드 order by b.종목코드")
        allSQLRows= cur.fetchall()
        self.table.setRowCount(len(allSQLRows)) ##set number of rows
        self.table.setColumnCount(12) ##this is fixed for myTableWidget, ensure that both of your tables, sql and qtablewidged have the same number of columns
        #print("allSQLRows=",allSQLRows)
        print("grid...start")
        row = 0
        #while True:
        #    sqlRow = cur.fetchall()
        for sqlRow in allSQLRows:
            if sqlRow == None:
                break ##stops while loop if there is no more lines in sql table
            for col in range(0, 12): ##otherwise add row into tableWidget
                #print("sqlRow[",col,"]=",sqlRow[col])
                self.table.setItem(row, col, QTableWidgetItem(sqlRow[col]))
            row += 1

        print("grid...end")       
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()        
        # 창크기 고정
        self.table.setFixedSize(800, 500)
        con.close()             
        
        
# Market Index 보기
class MaketIndex(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self._mainwin = parent

        self.__make_table()
        self.__make_layout()

    def __make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)

        grid = QGridLayout()
        vbox.addLayout(grid)
        # grid.setSpacing(20)

        self.setLayout(vbox)

        #setGeometry(int x, int y, int w, int h)
        self.setGeometry(600, 200, 1200, 600) 
        self.setWindowTitle("Maket Index ")


    def __make_table(self):
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.resize(1200, 800)
        self.table.setRowCount(2000)
        self.table.setColumnCount(5)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

        
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)  # header 정렬 방식

    def setTableWidgetData(self):
        # https://stackoverflow.com/questions/22941184/how-to-display-data-from-mysql-database-in-table-using-pyqt 참고
        # column header 명 설정.
        column_headers = ['일자','CD_91일', '콜_금리', '국고채_3년', '회사채_3년' ]
        self.table.setHorizontalHeaderLabels(column_headers)

        con = sqlite3.connect("./itm_master.db")
        cur = con.cursor()
        cur.execute("select 일자,CD_91일, 콜_금리 , 국고채_3년,회사채_3년 from market_index  order by 일자 desc")
        allSQLRows= cur.fetchall()
        self.table.setRowCount(len(allSQLRows)) ##set number of rows
        self.table.setColumnCount(5) ##this is fixed for myTableWidget, ensure that both of your tables, sql and qtablewidged have the same number of columns
        #print("allSQLRows=",allSQLRows)
        print("grid...start")
        row = 0
        #while True:
        #    sqlRow = cur.fetchall()
        for sqlRow in allSQLRows:
            if sqlRow == None:
                break ##stops while loop if there is no more lines in sql table
            for col in range(0, 5): ##otherwise add row into tableWidget
                #print("sqlRow[",col,"]=",sqlRow[col])
                self.table.setItem(row, col, QTableWidgetItem(sqlRow[col]))
            row += 1

        print("grid...end")       
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()        
        # 창크기 고정
        self.table.setFixedSize(400, 500)
        con.close()             
                
# Market World Index 보기
class MaketWorldIndex(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self._mainwin = parent

        self.__make_table()
        self.__make_layout()

    def __make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)

        grid = QGridLayout()
        vbox.addLayout(grid)
        # grid.setSpacing(20)

        self.setLayout(vbox)

        #setGeometry(int x, int y, int w, int h)
        self.setGeometry(600, 200, 1200, 600) 
        self.setWindowTitle("Maket Index ")


    def __make_table(self):
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.resize(1200, 800)
        self.table.setRowCount(2000)
        self.table.setColumnCount(7)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

        
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)  # header 정렬 방식

    def setTableWidgetData(self):
        # https://stackoverflow.com/questions/22941184/how-to-display-data-from-mysql-database-in-table-using-pyqt 참고
        # column header 명 설정.
        column_headers = ['일자','미국_USD', '일본_JPY', '유럽연합_EUR', '중국_CNY','WTI','국제_금']
        self.table.setHorizontalHeaderLabels(column_headers)

        con = sqlite3.connect("./itm_master.db")
        cur = con.cursor()
        cur.execute("select 일자,미국_USD, 일본_JPY , 유럽연합_EUR,중국_CNY,WTI,국제_금 from market_world_index  order by 일자 desc")
        allSQLRows= cur.fetchall()
        self.table.setRowCount(len(allSQLRows)) ##set number of rows
        self.table.setColumnCount(7) ##this is fixed for myTableWidget, ensure that both of your tables, sql and qtablewidged have the same number of columns
        #print("allSQLRows=",allSQLRows)
        print("grid...start")
        row = 0
        #while True:
        #    sqlRow = cur.fetchall()
        for sqlRow in allSQLRows:
            if sqlRow == None:
                break ##stops while loop if there is no more lines in sql table
            for col in range(0, 7): ##otherwise add row into tableWidget
                #print("sqlRow[",col,"]=",sqlRow[col])
                self.table.setItem(row, col, QTableWidgetItem(sqlRow[col]))
            row += 1

        print("grid...end")       
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()        
        # 창크기 고정
        self.table.setFixedSize(500, 500)
        con.close()    
        
        
# 모멘텀투자 전략보기
class Momentum_Graph(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(600, 200, 1400, 600)
        self.setWindowTitle("모멘텀 전략투자")
        self.setWindowIcon(QIcon('icon.png'))

        #self.lineEdit = QLineEdit()
        self.pushButton = QPushButton("모멘텀 전략투자")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.canvas)

        # Right Layout
        rightLayout = QVBoxLayout()
        #rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.pushButton)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def pushButtonClicked(self):
        
        import numpy as np
        import FinanceDataReader as fdr
        fdr.__version__
        
        # 한국거래소 상장종목 전체
        #df_krx = fdr.StockListing('KRX')
        #print(df_krx.head())
        
        # 10개의 종목을 추출한다.
        #tickers = df_krx.Symbol[:10]
        # 원하는 종목을 셋팅할 수도 있다.
        tickers = ['005930', '000660', '005380', '035420', '033780']
        #print(tickers)
        
        stocks = pd.DataFrame()
        
        for ticker in tickers:
            # 종가데이터를 가져온다.
            data_temp = fdr.DataReader(ticker, '20140101','20200612')
            data_temp = data_temp[['Close']]
        
            # 항목명을 종목명으로 교체
            # list형태로 전환
            stock_nm = []
            stock_nm.append(ticker)
            data_temp.columns = stock_nm
        
            # concat 옆으로 이어 붙이기
            stocks = pd.concat([stocks,data_temp],axis=1)
        
        print(stocks.head())
        
        # 과거 데이터순으로 정렬한다(날짜 오름차순(DataReader default))
        stocks = stocks.sort_index(ascending=True)
        
        
        from scipy.stats import linregress
        def momentum(closes):
            returns = np.log(closes)
            x = np.arange(len(returns))
            slope, _, rvalue, _, _ = linregress(x, returns)
            return ((1 + slope) ** 252) * (rvalue ** 2)  # annualize slope and multiply by R^2
        
        
        momentums = stocks.copy(deep=True)
        for ticker in tickers:
            momentums[ticker] = stocks[ticker].rolling(90).apply(momentum, raw=False)
        
        #plt.figure(figsize=(12, 9)) 
        plt.xlabel('Days') 
        plt.ylabel('Stock Price')
        #plt.show()
 
        plt.figure(figsize=(12, 6))
        ax = self.fig.add_subplot(111)        
            
        bests = momentums.max().sort_values(ascending=False).index[:5]    
        
        
        for best in bests:
            end = momentums[best].index.get_loc(momentums[best].idxmax()) # 모멘텀이 최고인 시점
            rets = np.log(stocks[best].iloc[end - 90 : end]) # 모멘텀이 최고시점 이전 90일간의 log 종가
            x = np.arange(len(rets))
            slope, intercept, r_value, p_value, std_err = linregress(x, rets) # 회귀함수
        
            try:
                # 주가 그래프
                ax.plot(np.arange(180), stocks[best][end-90:end+90]) # 모멘텀 최고 시점 전후 90일 총 180일의 주가
                # 모멘텀 그래프
                ax.plot(x, np.e ** (intercept + slope*x)) # 회귀함수 결과
            except:
                # 모멘텀 최고 시점의 전후 90 데이터가 부제하여 그래프 오류 날 수 있음.-> 그릴수 없는 종목은 skip
                # 5개가 모두 그려지지 않았다면 수집 데이터 기간을 늘려보기
                continue            

        
        #ax.plot(nc.index, nc['Close'], label='real')
        #ax.plot(forecast['ds'], forecast['yhat'], label='forecast')
        #ax.grid()
        #ax.legend()  
        
        #ax.legend(loc='upper right')
        
        ax.grid()

        self.canvas.draw()        
                
        
class MyTable2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(self)
        self._mainwin = parent

        self.__make_table()
        self.__make_layout()

    def __make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)

        grid = QGridLayout()
        vbox.addLayout(grid)
        # grid.setSpacing(20)

        self.setLayout(vbox)

##        self.setGeometry(200, 200, 1000, 1000)
        self.setWindowTitle("tablewidget example")


    def __make_table(self):
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setColumnCount(3)
        self.table.setRowCount(1)

        # column header 명 설정.
        self.table.setHorizontalHeaderLabels(["계좌번호", "잔고금액"])
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)  # header 정렬 방식


# =============================================================================
# MDI Child Window Class 정의부분
# =============================================================================

class MdiChild(MyTable):
    def __init__(self):
        super(MdiChild, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)
        
    def closeEvent(self, event):
        event.accept()
        
class MdiChild2(MyTable2):
    def __init__(self):
        super(MdiChild2, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)
        
    def closeEvent(self, event):
        event.accept()        
# 그래프 테스트
class MdiChild3(MyWindow):
    def __init__(self):
        super(MdiChild3, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)
        
    def closeEvent(self, event):
        event.accept()    
# 상장종목리스트        
class MdiChild4(ListItmTable):
    def __init__(self):
        super(MdiChild4, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)
        
    def closeEvent(self, event):
        event.accept()    
     
# BackTesting      
class MdiChild5(BackTesting):
    def __init__(self):
        super(MdiChild5, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)
        
# 마법공식      
class MdiChild6(MagicListtable):
    def __init__(self):
        super(MdiChild6, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)        
        
    def closeEvent(self, event):
        event.accept()    
        
# 주가예측      
class MdiChild7(StockPredict):
    def __init__(self):
        super(MdiChild7, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)        
        
    def closeEvent(self, event):
        event.accept()

        # 주가예측


        # 데이터 가져오기
class MdiChild8(StockDataCrawling):
    def __init__(self):
        super(MdiChild8, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)        
        
    def closeEvent(self, event):
        event.accept()          

# 가치투자 (Benjamin Graham ) 
class MdiChild9(BenjaminListtable):
    def __init__(self):
        super(MdiChild9, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)        
        
    def closeEvent(self, event):
        event.accept()         
        
# 이기는투자 (Peter Lynch) 
class MdiChild10(PeterListtable):
    def __init__(self):
        super(MdiChild10, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)        
        
    def closeEvent(self, event):
        event.accept()   
        
# 종목별재무제표
class MdiChild11(BalanceTable):
    def __init__(self):
        super(MdiChild11, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)        
        
    def closeEvent(self, event):
        event.accept()   
        
# MaketIndex 보기
class MdiChild12(MaketIndex):
    def __init__(self):
        super(MdiChild12, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)        
        
    def closeEvent(self, event):
        event.accept()          
        
# MaketWorldIndex 보기
class MdiChild13(MaketWorldIndex):
    def __init__(self):
        super(MdiChild13, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)        
        
    def closeEvent(self, event):
        event.accept()          
        
        
# 모멘텀투자 그래프 Momentum_Graph  
class MdiChild14(Momentum_Graph):
    def __init__(self):
        super(MdiChild14, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)        
        
    def closeEvent(self, event):
        event.accept()

# Showntell
class MdiChild15(NaverReal):
    def __init__(self):
        super(MdiChild15, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)

    def closeEvent(self, event):
        event.accept()

# NaverRealText
class MdiChild16(NaverReal):
    def __init__(self):
        super(MdiChild16, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)

    def closeEvent(self, event):
        event.accept()

#NewsRankText
class MdiChild17(NewsRankText):
    def __init__(self):
        super(MdiChild17, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)

    def closeEvent(self, event):
        event.accept()

#이미지캡셔닝
class MdiChild18(ImageCaption):
    def __init__(self):
        super(MdiChild18, self).__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)

    def closeEvent(self, event):
        event.accept()


# =============================================================================
# MainWindow Class 정의부분
# =============================================================================    
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        # self.createToolBars()
        self.createStatusBar()
        self.updateMenus()
        self.readSettings()

        self.setWindowTitle("m.Search v0.0.1")

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def newFile(self):
        child = self.createMdiChild()
        child.show()

    def open(self):
        child = self.createMdiChild2()
        child.show()
        
    # 그래프 테스트    
    def graph(self):
        child = self.createMdiChild3()
        child.show()
        
    # 상장종목리스트    
    def itmlist(self):
        child = self.createMdiChild4()
        child.show()

    # BackTesting
    def backtestlist(self):
        child = self.createMdiChild5()
        child.show()
        
    # 마법공식
    def Magiclist(self):
        child = self.createMdiChild6()
        child.show()
        
        
    # 주가예측
    def StockPredictGraph(self):
        child = self.createMdiChild7()
        child.show()       
        
    # 데이터 가저오기 
    def DataCrawling(self):
        child = self.createMdiChild8()
        child.show() 
        
    # 가치투자 
    def BanjaminList(self):
        child = self.createMdiChild9()
        child.show()         

     # 이기는 투자 Peter Lynch
    def PeterList(self):
        child = self.createMdiChild10()
        child.show()    
        
     # 이기는 투자 Peter Lynch
    def BalanceList(self):
        child = self.createMdiChild11()
        child.show()           
        
     # 이기는 투자 Peter Lynch
    def MarketIndexList(self):
        child = self.createMdiChild12()
        child.show()       
            
     # 이기는 투자 Peter Lynch
    def MarketWorldIndexList(self):
        child = self.createMdiChild13()
        child.show()

    # Momentum_Graph
    def MomentumGraphView(self):
        child = self.createMdiChild14()
        child.show()

    # showntell
    def ShowNTellView(self):
        child = MdiChild_ShowNTell()
        showntell = self.createMdiChild15()
        showntell.show()

    # NaverReal
    def NaverRealText(self):
        child = self.createMdiChild16()
        child.show()

    # NewsRankText
    def NewsRankText(self):
        child = self.createMdiChild17()
        child.show()

    # 이미지캡셔닝
    def ImageCaptionView(self):
        child = self.createMdiChild18()
        child.show()

    def about(self):
        sMsg = """My Quant ver0.0.1"""
        QMessageBox.about(self, "About .......", sMsg)

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.userFriendlyCurrentFile())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def createMdiChild(self):
        child = MdiChild()
        self.mdiArea.addSubWindow(child)

        return child
    
    def createMdiChild2(self):
        child = MdiChild2()
        self.mdiArea.addSubWindow(child)

        return child   
    
    # 그래프 테스트    
    def createMdiChild3(self):
        child = MdiChild3()
        self.mdiArea.addSubWindow(child)

        return child      

    # 상장종목리스트   
    def createMdiChild4(self):
        child = MdiChild4()
        self.mdiArea.addSubWindow(child)

        return child   
    
    # BackTesting
    def createMdiChild5(self):
        child = MdiChild5()
        self.mdiArea.addSubWindow(child)

        return child      
    
    # 마법공식
    def createMdiChild6(self):
        child = MdiChild6()
        self.mdiArea.addSubWindow(child)

        return child     
    
    # 주가예측
    def createMdiChild7(self):
        child = MdiChild7()
        self.mdiArea.addSubWindow(child)

        return child      

    # 데이터가져오기
    def createMdiChild8(self):
        child = MdiChild8()
        self.mdiArea.addSubWindow(child)

        return child   

    # 가치투자 (Benjamin Graham )
    def createMdiChild9(self):
        child = MdiChild9()
        self.mdiArea.addSubWindow(child)

        return child   
    
    # 이기는투자 (Peter Lynch)
    def createMdiChild10(self):
        child = MdiChild10()
        self.mdiArea.addSubWindow(child)

        return child      
    
    
    # 종목별 재무제표
    def createMdiChild11(self):
        child = MdiChild11()
        self.mdiArea.addSubWindow(child)

        return child      
    
    # Maket Index
    def createMdiChild12(self):
        child = MdiChild12()
        self.mdiArea.addSubWindow(child)

        return child  

    # Maket World Index
    def createMdiChild13(self):
        child = MdiChild13()
        self.mdiArea.addSubWindow(child)

        return child

    # Momentum_Graph
    def createMdiChild14(self):
        child = MdiChild14()
        self.mdiArea.addSubWindow(child)

        return child

    # showntell
    def createMdiChild15(self):
        child = MdiChild15()
        self.mdiArea.addSubWindow(child)
        return child

    # NaverRealText
    def createMdiChild16(self):
        child = MdiChild16()
        self.mdiArea.addSubWindow(child)
        return child

    # NewsRankText
    def createMdiChild17(self):
        child = MdiChild17()
        self.mdiArea.addSubWindow(child)
        return child

    # ImageCaptionVeiw
    def createMdiChild18(self):
        child = MdiChild18()
        self.mdiArea.addSubWindow(child)
        return child

    def createActions(self):
        self.openSS001 = QAction("메뉴1", self,
                                 statusTip = "힌트1",
                                 triggered=self.open)

        self.openSS002 = QAction("메뉴2", self,
                                 statusTip = "힌트2",
                                 triggered=self.open)

        self.newAct = QAction("&My Fortfolio", self,
                shortcut=QKeySequence.New, statusTip="Create a new file",
                triggered=self.newFile)
        
        self.openAct = QAction("&Open...", self,
                shortcut=QKeySequence.Open, statusTip="Open an existing file",
                triggered=self.open)
        
        # 그래프 테스트    
        self.graphAct = QAction("&차트 ", self,
                 statusTip="Graph&Chart View",
                triggered=self.graph)
        
        #  상장종목리스트ㅡ    
        self.itmlistAct = QAction("&상장 종목정보", self,
                 statusTip="상장종목정보",
                triggered=self.itmlist)
        
        #  BackTesting   
        self.BackTestAct = QAction("&BackTesting", self,
                statusTip="BackTesting",
                triggered=self.backtestlist)        
        
        # 마법공식                
        self.MagicListAct = QAction("&마법 공식", self,
                 statusTip="마법공식",
                triggered=self.Magiclist)  
        
        # 가치투자 BanjaminList
        self.BanjaminListAct = QAction("&가치 투자", self,
                 statusTip="가치투자",
                triggered=self.BanjaminList)         
        
        # 이기는 투자 Peter Lynch
        self.PeterListAct = QAction("&이기는 투자", self,
                statusTip="이기는투자",
                triggered=self.PeterList)

        # Momentum_Graph      
        self.MomentumGraphViewAct = QAction("&모멘텀 투자", self,
                statusTip="모멘텀 투자",
                triggered=self.MomentumGraphView)

        # NaverRealText
        self.NaverRealTextViewAct = QAction("&실시간검색어", self,
                statusTip="실시간검색어",
                triggered=self.NaverRealText)

        # NewsRankText
        self.NewsRankTextViewAct = QAction("&뉴스요약", self,
                statusTip="뉴스요약",
                triggered=self.NewsRankText)

        # 이미지캡셔닝
        self.ImageCaptionViewAct = QAction("&이미지캡셔닝", self,
                statusTip="이미지캡셔닝",
                triggered=self.ImageCaptionView)

        # Momentum_Graph
        self.ShowNTellViewAct = QAction("&Show N Tell", self,
                statusTip="Show N Tell",
                triggered=self.ShowNTellView)

        # 종목별 재무제표
        self.BalanceListAct = QAction("&종목별 재무제표", self,
                statusTip="종목별 재무제표",
                triggered=self.BalanceList)
        
        
        # 주가예측                
        self.StockPredictAct = QAction("&주가예측", self,
                statusTip="주가예측",
                triggered=self.StockPredictGraph)        
        
        
        # Market Index                
        self.MarketIndexListAct = QAction("&Maket Index", self,
                statusTip="Maket Index",
                triggered=self.MarketIndexList)       

        #  Market World Index            
        self.MarketWorldIndexListAct = QAction("&Market World Index", self,
                statusTip="Market World Index",
                triggered=self.MarketWorldIndexList)        
        
       
        #기초데이터 가져오기
        self.DataCrawlingAct = QAction("&기초데이터", self,
                statusTip="데이터 크롤링",
                triggered=self.DataCrawling)       
        
        self.exitAct = QAction("E&xit", self, shortcut=QKeySequence.Quit,
                statusTip="Exit the application",
                triggered=QApplication.instance().closeAllWindows)

        self.closeAct = QAction("Cl&ose", self,
                statusTip="Close the active window",
                triggered=self.mdiArea.closeActiveSubWindow)

        self.closeAllAct = QAction("Close &All", self,
                statusTip="Close all the windows",
                triggered=self.mdiArea.closeAllSubWindows)

        self.tileAct = QAction("&Tile", self, statusTip="Tile the windows",
                triggered=self.mdiArea.tileSubWindows)

        self.cascadeAct = QAction("&Cascade", self,
                statusTip="Cascade the windows",
                triggered=self.mdiArea.cascadeSubWindows)

        self.nextAct = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild,
                statusTip="Move the focus to the next window",
                triggered=self.mdiArea.activateNextSubWindow)

        self.previousAct = QAction("Pre&vious", self,
                shortcut=QKeySequence.PreviousChild,
                statusTip="Move the focus to the previous window",
                triggered=self.mdiArea.activatePreviousSubWindow)

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("기초관리")
        self.fileMenu.addAction(self.openAct)     
        self.fileMenu.addAction(self.newAct) 
        self.fileMenu.addSeparator() 
        self.fileMenu.addAction(self.DataCrawlingAct)          # 데이터크롤링
        self.fileMenu.addSeparator() 
        self.fileMenu.addAction(self.graphAct)                 # 그래프 테스트
        self.fileMenu.addAction(self.itmlistAct)               # 상장종목리스트
        self.fileMenu.addAction(self.BalanceListAct)           # 종목별재무제표
        self.fileMenu.addSeparator() 
        self.fileMenu.addAction(self.MarketIndexListAct)       # Market Index
        self.fileMenu.addAction(self.MarketWorldIndexListAct)  # Market World Index
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.NaverRealTextViewAct)     # 실시간검색어
        self.fileMenu.addAction(self.NewsRankTextViewAct)      # 뉴스요약

        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.SaleMenu = self.menuBar().addMenu("이미지분석")
        self.SaleMenu.addAction(self.ImageCaptionViewAct)      # 이미지캡셔닝
        self.SaleMenu.addAction(self.ShowNTellViewAct)         # Showntell

        self.SaleMenu = self.menuBar().addMenu("전략")
        self.SaleMenu.addAction(self.MagicListAct)             # 마법공식
        self.SaleMenu.addAction(self.BanjaminListAct)          # 가치투자
        self.SaleMenu.addAction(self.PeterListAct)             # 이기는투자
        self.SaleMenu.addAction(self.MomentumGraphViewAct)     # 모멘텀투자

        self.SaleMenu = self.menuBar().addMenu("BackTesting")
        self.SaleMenu.addAction(self.BackTestAct)         # 백테스팅
        #self.SaleMenu.addAction(self.openSS002)         # 메뉴2

        self.SaleMenu = self.menuBar().addMenu("예측")
        self.SaleMenu.addAction(self.StockPredictAct)         # 주가예측
        #self.SaleMenu.addAction(self.openSS002)         # 메뉴2

        #self.SaleMenu = self.menuBar().addMenu("메뉴선택")
        #self.SaleMenu.addAction(self.openSS001)         # 메뉴1
        #self.SaleMenu.addAction(self.openSS002)         # 메뉴2

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
 
    def createStatusBar(self):
        self.statusBar().showMessage("Copyright by Jung Nak Hyun v0.0.1")

    def readSettings(self):
        return

    def writeSettings(self):
        return

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def findMdiChild(self, fileName):
        canonicalFilePath = QFileInfo(fileName).canonicalFilePath()

        for window in self.mdiArea.subWindowList():
            if window.widget().currentFile() == canonicalFilePath:
                return window
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)


# =============================================================================
# QApplication
# =============================================================================    
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())        