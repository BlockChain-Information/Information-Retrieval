# -*- coding: utf-8 -*-
"""
Created on Tue May 19 07:47:07 2020

@author: Jung Nak Hyun 정낙현
"""
##########################################################################
# 변경이력 
# 2020.11.11 v0.0.1
##########################################################################

import sys

# PYQT5 를 이용하기 위한 모듈갱신
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

import argparse
# Vocabulary 를 import 해야 정상 작동함
from build_vocab import Vocabulary

# 인공지능 학습/예측 라이브러리 가져오기
from show_torch        import Class_Torch
# 번역
from show_translator   import Class_Translate
# sentimental analysis
from show_sentiment   import Class_Sentiment
# logo analysis
from show_logo   import Class_Logo


###############################################################################
# QT Designer 로 만든 UI 파일 QDialog 로 만듬
# 불러오고자 하는 .ui 파일
# .py 파일과 같은 위치에 있어야 한다 *****
###############################################################################
form_class = uic.loadUiType("showntell.ui")[0]


###############################################################################
# User Class 정의 
###############################################################################


# Painter Class 정의                    
class Painter(QWidget):
    ParentLink = 0
    def __init__(self,parent):
        super(Painter, self).__init__()
        self.ParentLink = parent


                
                
###############################################################################
# MyWindow 정의 
###############################################################################
class MdiChild_ShowNTell(object, form_class):
    PaintPanel = 0
    
    Vimage = QImage(QSize(400, 400), QImage.Format_RGB32)
    #Vimage.fill(Qt.white)
    
    
    # 라이브러리 클래스
    lib_torch = Class_Torch()
    lib_trans = Class_Translate()
    lib_senti = Class_Sentiment()
    lib_logo  = Class_Logo()
             
    # 초기 설정해주는 init
    def __init__(self):
        #super().__init__()
        super(MdiChild_ShowNTell, self).__init__()
        
        # 시그널(이벤트루프에서 발생할 이벤트) 선언
        # self.객체명.객체함수.connect(self.슬롯명)

        self.setupUi(self)
        self.setGeometry(100, 100, 830, 450)
        self.resize( QSize(600, 580))
        self.setWindowTitle('Show and Tell')
        
        # QStackedWidget 0 번에는 손글씨용 PaintPanel 을 만듬
        self.PaintPanel = Painter(self)
        self.PaintPanel.close()
        self.DrawingFrame.insertWidget(0,self.PaintPanel)
        self.DrawingFrame.setCurrentWidget(self.PaintPanel)   # 0번활성화

        # QStackedWidget 1 번에는 이미지용  QLabel 을 만듬
        self.Label = QLabel()
        self.DrawingFrame.insertWidget(1,self.Label)

        #self.Vimage.fill(Qt.white)

        # 슬롯 연결
        self.Establish_Connections()

    def closeEvent(self, event):
        self.deleteLater()


    # 학습할 모델 선택
    
    # 시그널을 처리할 슬롯

    def ClearSlate(self):
        # 초기화하자
        #self.DrawingShapes = Shapes()
        self.PaintPanel.repaint()  
        self.Label.clear() 
        self.Label2.clear()
        self.Label3.clear()
        self.Label4.clear()
        self.Label5.clear()
        self.textEdit.setText("")
        
        # QStackedWidget 0번페이지를 활성화한다
        self.DrawingFrame.setCurrentWidget(self.PaintPanel) 
    
    # 이미지를 저장한다
    def SaveImage(self):
        self.Vimage.save('png/image.png')
        self.Vimage.fill(Qt.white)
 

    # 이미지를 불러온다
    def LoadImage(self):
        
        # 일단 초기화부터 하자
        self.ClearSlate()
        
        selection = QMessageBox.question(self,'확인',"파일을 로드 하시겠습니까?",QMessageBox.Yes,QMessageBox.No)
        
        if selection == QMessageBox.Yes: # 파일로드
            try:
                fname = QFileDialog.getOpenFileName(self)
                print("fname=",fname)
                
            except Exception as e:
                self._stateexpression.setText(e)
                QMessageBox.about(self,"경고",e)
                
            else:
                # 보여주기
                self.pixmap = QPixmap(fname[0])
                self.pixmap = self.pixmap.scaled(400,400)
                self.DrawingFrame.setCurrentWidget(self.Label)  
                self.Label.setPixmap(self.pixmap)
               
                self.show()  
               

    
    # 이미지를 예측함
    def PredictImage(self):
        self.pixmap.save("png/image.png")
        # 예측
        self.Predict()

    #  로고읽기
    def LogoImage(self):
        # 예측
        self.pixmap.save("png/image.png")

        self.Logo_detect()

        self.pixmap = QPixmap("png/result1.png")
        self.pixmap = self.pixmap.scaled(400, 400)
        self.DrawingFrame.setCurrentWidget(self.Label)
        self.Label.setPixmap(self.pixmap)

        self.show()

    def Train(self):
        print("Train=")
        pass
        
    def Predict(self):   
        
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

        try :
            pred = self.lib_torch.predict(args)
            #print(pred)
            # <start> <end> 를 제거해줌
            pred_txt = pred[7:len(pred)-5]
            #print(pred_txt)
        except :
            pred_txt =""

        #self.textEdit.setText("Predict : {}".format(pred_txt))
        self.textEdit.setText(pred_txt)

        #if self.Combo2 =='unicode':

        # 번역
        try :
            trans = self.lib_trans.trans(pred_txt)
            print(trans)
        except :
            trans = ""


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

        self.Label2.setText(trans)  # 텍스트
        self.Label2.setFont(QFont("궁서", 12))  # 폰트/크기조절
        self.Label3.setText(senti_pos)      # positive
        self.Label4.setText(senti_neu)      # neutral
        self.Label5.setText(senti_neg)      # negative

        del pred
        del trans
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


###############################################################################
# QApplication 윈도우 띄우기
###############################################################################  
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # myWindow 라는 변수에 GUI 클래스 삽입
    myWindow = MdiChild_ShowNTell()
    # GUI 창 보이기
    myWindow.show()
       
    #########################
    # 이벤트루프 진입전 작업할 부분
    ######################### 
    # 이벤트루프 진입
    app.exec_()
 