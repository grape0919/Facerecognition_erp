import sys
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QDesktopWidget, QLabel, QPushButton, QListWidget, QListWidgetItem, QTextEdit
import logging
from PyQt5.QtGui import QFont

from view.newInfo_gui import NewInfoDialog
from rdbms.dbmsManager import DbmsManager

import static.staticValues as staticValues



"""정보 관리 페이지"""
class InfoDialog(QDialog):

    logging.basicConfig(filename=staticValues.logFilePath,level=logging.DEBUG)

    def __init__(self, dbmsManager):
        super().__init__()
        logging.info("정보 관리 페이지")
        self.dbManager = dbmsManager
        self.initUI()


    def initUI(self):
        self.setWindowTitle('정보 관리')
        #메인 화면 색상
        self.setStyleSheet("color: black;"
                        "background-color: white")
        #메인 화면 windows 중앙 배치
        self.center()
        #메인 화면 size
        self.resize(660, 400)
        self.setMaximumSize(660, 400)
        self.setMinimumSize(660, 400)
        '''빠른 개발을 위해 레이아웃은 절대배치로 사용'''

        #정보 리스트 뷰
        listLabel = QLabel("result List", self)
        fontList = QFont()
        fontList.setBold(True)
        fontList.setFamily("고딕")
        listLabel.setFont(fontList)
        listLabel.setText("등록 정보 리스트")
        listLabel.move(20, 20)

        self.infoListView = QListWidget(self)
        self.infoListView.setAutoScroll(True)
        self.infoListView.move(20, 40)
        self.infoListView.resize(480,330)
        self.load_info()
        # self.infoListView.addItem("list1")
        # self.infoListView.addItem("list2")
        # self.infoListView.addItem("list3")

        #self.infoListView.itemClicked.connect(self.printInfo)

        #정보신규 등록 버튼
        newInformationButton = QPushButton('신규 등록', self)
        newInformationButton.setStyleSheet(staticValues.buttonStyleSheet)

        newInformationButton.setFont(staticValues.buttonFont)
        newInformationButton.move(540, 40)
        newInformationButton.resize(staticValues.buttonSize)

        newInformationButton.clicked.connect(self.newInfoClickListener)

        #정보신규 등록 버튼
        deleteInformationButton = QPushButton('삭제', self)
        deleteInformationButton.setStyleSheet(staticValues.buttonStyleSheet)

        deleteInformationButton.setFont(staticValues.buttonFont)
        deleteInformationButton.move(540, 140)
        deleteInformationButton.resize(staticValues.buttonSize)

        deleteInformationButton.clicked.connect(self.deleteInfoClickListener)
        #self.show()

    """windows 화면 중앙 배치"""
    def center(self):
        qr = self.frameGeometry() #프로그램 frame
        cp = QDesktopWidget().availableGeometry().center() #화면 중앙값
        qr.moveCenter(cp) #frame의 중앙을 화면 중앙으로
        self.move(qr.topLeft()) #move setting은 좌상단 좌표사용

    def showModal(self):
        return super().exec_()


    def newInfoClickListener(self):
        newInfo = NewInfoDialog(self.dbManager)
        newInfo.showModal()
        logging.error(newInfo.sucess)
        if(newInfo.sucess):
            self.load_info()

    def deleteInfoClickListener(self):
        deleteInfo = self.infoListView.takeItem(self.infoListView.currentRow())
        eid = deleteInfo.text().split()

        try:
            self.dbManager.delete_single_info(eid[0])
        except:
            logging.error(eid[0])
            logging.error("삭제 실패하였습니다")

    def load_info(self):
        self.infoListView.clear()
        try:
            result = self.dbManager.select_all_info()
            for row in result:
                self.infoListView.addItem('\t'.join(map(str, row)))
        except:
            logging.error("데이터가 없습니다.")

"""GUI TEST"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InfoDialog()
    ex.show()
    #ex2 = InfoDialog()
    sys.exit(app.exec_())