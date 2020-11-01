from PyQt5.QtCore import Qt, QThread
import sys
from PyQt5.QtWidgets import QApplication,QDesktopWidget, QDialog, QWidget, QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit, QMessageBox
from PyQt5.QtGui import QFont, QPainter,QColor,QPen, QIntValidator
import logging
import static.staticValues as staticValues

from rdbms.dbmsManager import DbmsManager
from camera import ShowVideo, ImageViewer

"""신규 등록 페이지"""
class NewInfoDialog(QDialog):
    
    logging.basicConfig(filename=staticValues.logFilePath,level=logging.DEBUG)
    
    def __init__(self, dbManager):
        super().__init__()
        logging.info("신규 등록 페이지")
        self.sucess=False
        self.new_face_encoding=0
        self.dbManager = dbManager
        self.initUI()

    def initUI(self):
        self.setWindowTitle('신규 등록')
        #메인 화면 색상
        self.setStyleSheet("color: black;"
                        "background-color: white")
        #메인 화면 windows 중앙 배치
        self.center()
        #메인 화면 size
        self.resize(staticValues.dialogSize)
        self.setMaximumSize(staticValues.dialogSize)
        self.setMinimumSize(staticValues.dialogSize)
        '''빠른 개발을 위해 레이아웃은 절대배치로 사용'''
        logging.error("newInformationDialog show")

        font = QFont()
        font.setBold(True)
        font.setFamily("고딕")

        nameLabel = QLabel("이름", self)
        nameLabel.setFont(font)
        nameLabel.resize(staticValues.labelSize)
        nameLabel.move(520, 40)
        
        self.nameInput = QLineEdit(self)
        self.nameInput.resize(staticValues.labelSize)
        self.nameInput.move(620, 40)
        
        ageLabel = QLabel("나이", self)
        ageLabel.setFont(font)
        ageLabel.resize(staticValues.labelSize)
        ageLabel.move(520, 80)

        self.ageInput = QLineEdit(self)
        self.ageInput.resize(staticValues.labelSize)
        self.ageInput.move(620, 80)
        self.ageInput.setValidator(QIntValidator(0, 100, self))
        positionLabel = QLabel("직책", self)
        positionLabel.setFont(font)
        positionLabel.resize(staticValues.labelSize)
        positionLabel.move(520, 120)

        self.positionInput = QLineEdit(self)
        self.positionInput.resize(staticValues.labelSize)
        self.positionInput.move(620, 120)

        #카메라 작동 버튼
        cameraStartButton = QPushButton('카메라 작동', self)
        cameraStartButton.setStyleSheet(staticValues.buttonStyleSheet)

        cameraStartButton.setFont(staticValues.buttonFont)
        cameraStartButton.move(520, 280)
        cameraStartButton.resize(staticValues.buttonSize)

        self.thread = QThread()
        self.thread.start()
        self.vid = ShowVideo(db=self.dbManager)
        self.vid.moveToThread(self.thread)
        
        self.image_viewer = ImageViewer(self)
        self.image_viewer.move(20, 20)
        self.image_viewer.resize(480, 480)
        self.vid.VideoSignal.connect(self.image_viewer.setImage)
        cameraStartButton.clicked.connect(self.cameraStartClickListener)
        
        #캡처 버튼
        captureButton = QPushButton('캡처', self)
        captureButton.setStyleSheet(staticValues.buttonStyleSheet)

        captureButton.setFont(staticValues.buttonFont)
        captureButton.move(640, 280)
        captureButton.resize(staticValues.buttonSize)

        captureButton.clicked.connect(self.captureClickListener)

        #등록 버튼
        newInformationButton = QPushButton('신규 등록', self)
        newInformationButton.setStyleSheet(staticValues.buttonStyleSheet)

        newInformationButton.setFont(staticValues.buttonFont)
        newInformationButton.move(760, 280)
        newInformationButton.resize(staticValues.buttonSize)

        newInformationButton.clicked.connect(self.newInfoClickListener)
        
        #TODO INFORMATION INSERT!

        #self.show()

    """windows 화면 중앙 배치"""
    def center(self):
        qr = self.frameGeometry() #프로그램 frame
        cp = QDesktopWidget().availableGeometry().center() #화면 중앙값
        qr.moveCenter(cp) #frame의 중앙을 화면 중앙으로
        self.move(qr.topLeft()) #move setting은 좌상단 좌표사용

    def showModal(self):
        logging.error("showModal")
        
        return super().exec_()

    def newInfoClickListener(self):
        if((type(self.new_face_encoding)==type(0))):
            self.sucess=False
            alert = QMessageBox.information(
            self, '에러', "검출된 얼굴이 없어 데이터를 저장 할 수 없습니다.", 
                QMessageBox.Ok
            )
        elif (type(self.new_face_encoding)==type('')):
            self.sucess=False
            alert = QMessageBox.information(
            self, '에러', "이미 등록된 얼굴입니다.", 
                QMessageBox.Ok
            )
        else :
            data = (self.new_face_encoding.tostring(), self.nameInput.text().strip(), self.ageInput.text().strip(), self.positionInput.text().strip())
                
            try:
                self.dbManager.insert_single_info(data)
                self.sucess=True
                self.close()
            except Exception as e:
                self.sucess=False
                alert = QMessageBox.information(
                self, '에러', str(e)+"\n정보를 insert 할 수 없습니다.", 
                    QMessageBox.Ok
                )
            
            #alert.show()

    def cameraStartClickListener(self):
        logging.error("Clicked camera start")
        self.vid.startVideo()
        logging.error("start face recogni")
        self.vid.face_recog()

    def captureClickListener(self):
        #TODO:카메라 캡처
        logging.error("Clicked capture")
        self.vid.run_video = False
        self.new_face_encoding = self.vid.captureVideo()
        if (type(self.new_face_encoding)==type(int) and self.new_face_encoding==0):
            logging.error("검출된 결과가 없습니다.")
        elif (type(self.new_face_encoding)==type(str)):
            logging.error("이미 등록된 얼굴입니다.")
        
    def closeEvent(self, QCloseEvent):
        logging.error("close newInfo")
        self.vid.run_video = False
        self.thread.quit()
        
"""GUI TEST"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NewInfoDialog()
    ex.show()
    #ex2 = InfoDialog()
    sys.exit(app.exec_())