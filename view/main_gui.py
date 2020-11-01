import sys
import os
import logging

from PyQt5.QtCore import Qt,QThread
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QLabel, QPushButton, QListWidget, QListWidgetItem, QTextEdit
from PyQt5.QtGui import QFont, QPainter,QColor,QPen

from rdbms.dbmsManager import DbmsManager
from view.infoManager_gui import InfoDialog

import static.staticValues as staticValues
from camera import ShowVideo, ImageViewer

"""메인 화면"""
class MyApp(QWidget):
    logging.basicConfig(filename=staticValues.logFilePath,level=logging.DEBUG)

    

    def __init__(self):
        logging.info("ANDY를 시작합니다.")
        
        super().__init__()
        self.dbManager = DbmsManager()
        self.initUI()


    def initUI(self):
        self.setWindowTitle('ANDY')
        #메인 화면 색상
        self.setStyleSheet("color: black;"
                        "background-color: white")
        #메인 화면 windows 중앙 배치
        self.center()
        #메인 화면 size
        self.resize(1024, 600)
        self.setMaximumSize(1024, 600)
        self.setMinimumSize(1024, 600)
        '''빠른 개발을 위해 레이아웃은 절대배치로 사용'''


        #Title
        title = QLabel("TITLE", self)
        title.setText("ANDY")
        #Title 스타일
        fontTitle = title.font()
        fontTitle.setPointSize(30)
        fontTitle.setBold(True)
        fontTitle.setFamily("고딕")
        title.setFont(fontTitle)
        #Title 위치
        title.move(20,0)
        
        #검출시작 버튼
        self.runtimeDetectionButton = QPushButton('검출 시작', self)
        self.runtimeDetectionButton.setStyleSheet(staticValues.buttonStyleSheet)
        
        self.runtimeDetectionButton.setFont(staticValues.buttonFont)
        self.runtimeDetectionButton.move(20, 540)
        self.runtimeDetectionButton.resize(staticValues.buttonSize)
        
        self.thread = QThread()
        self.thread.start()
        self.vid = ShowVideo(db=self.dbManager)
        self.vid.moveToThread(self.thread)
        
        #cameraView
        self.image_viewer = ImageViewer(self)
        self.image_viewer.move(20, 50)
        self.image_viewer.resize(480, 480)
        self.vid.VideoSignal.connect(self.image_viewer.setImage)
        #검출 버튼 클릭이벤트
        self.runtimeDetectionButton.clicked.connect(self.runtimeDetectionClickListener)

        #검출 중지 버튼
        self.runtimeDetectionStopButton = QPushButton('검출 중지', self)
        self.runtimeDetectionStopButton.setStyleSheet(staticValues.buttonStyleSheet)
        
        self.runtimeDetectionStopButton.setFont(staticValues.buttonFont)
        self.runtimeDetectionStopButton.move(130, 540)
        self.runtimeDetectionStopButton.resize(staticValues.buttonSize)

        self.runtimeDetectionStopButton.clicked.connect(self.runtimeDetectionStopClickListener)
        #정보관리 버튼
        infomationManagerButton = QPushButton('정보 관리', self)
        infomationManagerButton.setStyleSheet(staticValues.buttonStyleSheet)

        infomationManagerButton.setFont(staticValues.buttonFont)
        infomationManagerButton.move(405, 540)
        infomationManagerButton.resize(staticValues.buttonSize)

        infomationManagerButton.clicked.connect(self.infoManagerClickListener)

        #정보 리스트 뷰
        listLabel = QLabel("result List", self)
        fontList = QFont()
        fontList.setBold(True)
        fontList.setFamily("고딕")
        listLabel.setFont(fontList)
        listLabel.setText("검출 결과 리스트")
        listLabel.move(520, 50)

        self.infoListView = QListWidget(self)
        self.infoListView.setAutoScroll(True)
        self.infoListView.move(520, 70)
        self.infoListView.resize(480,330)

        #self.infoListView.itemClicked.connect(self.printInfo)
        #self.infoListView.change.connect(self.changeElementEvent)
        #tts view
        ttsLabel = QLabel("result List", self)
        fontList = QFont()
        fontList.setBold(True)
        fontList.setFamily("고딕")
        ttsLabel.setFont(fontList)
        ttsLabel.setText("TTS TEXT")
        ttsLabel.move(520, 410)

        self.ttsView = QTextEdit(self)
        self.ttsView.setEnabled(False)
        self.ttsView.move(520, 430)
        self.ttsView.resize(480,150)

        #self.ttsManager = TTSManager()
        #frame을 화면에 뿌리기
        self.show()

    """windows 화면 중앙 배치"""
    def center(self):
        qr = self.frameGeometry() #프로그램 frame
        cp = QDesktopWidget().availableGeometry().center() #화면 중앙값
        qr.moveCenter(cp) #frame의 중앙을 화면 중앙으로
        self.move(qr.topLeft()) #move setting은 좌상단 좌표사용

    #tts print
    def printInfo(self):
        # TODO : 데이터베이스에서 삭제 또는 생성 가능한 데이터로 변환
        splited_info = self.infoListView.currentItem().text().split("\t")
        tts = splited_info[1] + "세 직책" + splited_info[2] + " " + splited_info[0] + "입니다." 
        self.ttsView.setText(tts)
            # self.ttsView.setText()
            

    #정보 관리 클릭 이벤트
    def infoManagerClickListener(self):
        logging.error("clicked infoMana button")
        infoManager = InfoDialog(self.dbManager)
        self.vid.run_video = False
        infoManager.showModal()
        self.vid.load_data()
    
    #검출 시작 버튼 클릭 이벤트
    def runtimeDetectionClickListener(self):
        logging.error("clicked runtime button")
        if not self.vid.run_video:
            self.vid.startVideo(listView=self.infoListView, ttsTextView=self.ttsView)
        

    #검출 중지 버튼 클릭
    def runtimeDetectionStopClickListener(self):
        logging.error("clicked runtime stop button")
        self.vid.run_video = False

    #프로그램 닫으면서 쓰레드 종료
    def closeEvent(self, QCloseEvent):
        logging.error("close Main")
        self.thread.quit()
        self.dbManager.close()
        self.vid.tts.isRunning=False
        self.vid.tts.join()
        
    # """카메라VIEW 임시 영역 표시"""
    # def paintEvent(self, e):
    #     painter = QPainter()
    #     painter.begin(self)
        
    #     painter.setBrush(QColor(200, 200, 200))
    #     #painter.setPen(QPen(QColor(60, 60, 60), 3))
    #     painter.drawRect(20, 50, 480, 480)

    #     painter.end()