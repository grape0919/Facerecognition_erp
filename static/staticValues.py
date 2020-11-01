from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont

#logFilePath = 'log\\andy_error.log'
logFilePath = '.\\log\\andy_error.log'

rdbmsDir = ".\\rdbms"
rdbmsPropFilePath = rdbmsDir + "\\rdbms.properties"

ttsPath = ".\\tts"

dialogSize = QSize(880, 512)
labelSize = QSize(220, 20)
inputTextSize = QSize(220, 40)
buttonSize = QSize(100,40)

#버튼 폰트
buttonFont = QFont()
buttonFont.setBold(True)
#버튼 styleSheet
buttonStyleSheet = "color: white;"
buttonStyleSheet += "background-color: #2F92FA;"
buttonStyleSheet += "border-style: solid;"
buttonStyleSheet += "border-width: 2px;"
buttonStyleSheet += "border-color: #2F92FA;"
buttonStyleSheet += "border-radius: 5px"