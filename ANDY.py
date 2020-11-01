import sys
from PyQt5.QtWidgets import QApplication
from view.main_gui import MyApp

"""프로그램 시작"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())