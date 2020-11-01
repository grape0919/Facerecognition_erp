
import cv2
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import dlib
import face_recognition
import numpy as np
from rdbms.dbmsManager import DbmsManager
from PyQt5.QtWidgets import QListWidget
from tts.TTSManager import TTSManager

import static.staticValues as staticValues
import logging
"""camera module"""

"""video module"""
class ShowVideo(QtCore.QObject):

    logging.basicConfig(filename=staticValues.logFilePath,level=logging.DEBUG)
    flag = 0
    run_video = False
    camera = cv2.VideoCapture(0)

    tts = TTSManager()
    ret, image = camera.read()
    if(type(image) == type(None)) :
        logging.error("사용 가능한 카메라가 없습니다.")

    else :
        height, width = image.shape[:2]

    VideoSignal = QtCore.pyqtSignal(QtGui.QImage)


    known_face_encodings = []
    known_face_names = []


    def __init__(self, parent=None, db=None):
        self.db = db
        self.load_data()
        
        if not self.tts.isAlive():
            self.tts = TTSManager()
            self.tts.start()
        self.tts.isRunning = True
        super(ShowVideo, self).__init__(parent)

    def load_data(self):
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_age = []
        self.known_face_position = []
        try:
            result = self.db.select_all_info()
            if result :
                for row in result:
                    
                    self.known_face_names.append(row[1])
                    self.known_face_age.append(row[2])
                    self.known_face_position.append(row[3])
                    encoding = np.fromstring(row[4], dtype=np.float64)
                    self.known_face_encodings.append(encoding)
        except Exception as e:
            logging.error(e)
            logging.error("데이터가 없습니다.")

    @QtCore.pyqtSlot()
    def startVideo(self, listView=None, ttsTextView=None):
        logging.error("clicked startVideo")
        global image
        self.run_video = True
        self.listView = listView
        self.ttsTextView = ttsTextView
        if(self.listView == None):
            self.tts.isRunning = False
        while self.run_video:
            ret, image = self.camera.read()
            if(type(image) == type(None)) :
                logging.error("사용 가능한 카메라가 없습니다.")
                self.run_video = False
                break
            self.face_recog()

            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            qt_image = QtGui.QImage(color_swapped_image.data,
                                    480,
                                    480,
                                    color_swapped_image.strides[0],
                                    QtGui.QImage.Format_RGB888)
            self.VideoSignal.emit(qt_image)
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(25, loop.quit) #25 ms
            loop.exec_()

        # if not self.run_video:
        #     self.tts.text = ""

    def captureVideo(self):
        logging.error("captureVideo")
        # TODO : ractangle 표시
        
        self.run_video = False
        self.tts.text = ""
        ret, image = self.camera.read()
        if(type(image) == type(None)) :
            logging.error("사용 가능한 카메라가 없습니다.")
            return 0
        else:
            rgb_frame = image[:, :, ::-1]
            face_location = face_recognition.face_locations(rgb_frame)
            face_encoding = face_recognition.face_encodings(rgb_frame, face_location)

            if face_encoding:
                if not self.known_face_encodings:
                    return face_encoding[0]
                else:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding[0])
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding[0])
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        return name
                    else :
                        return face_encoding[0] # face_encoding
            else :
                return 0

    @QtCore.pyqtSlot()       
    def face_recog(self):
        if(self.run_video == True):
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_frame = image[:, :, ::-1]

            # Find all the faces and face enqcodings in the frame of video
            self.face_locations = face_recognition.face_locations(rgb_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_frame, self.face_locations)

            if self.listView != None:
                self.listView.clear()
                self.ttsTextView.setText("")
                
            for (top, right, bottom, left), face_encoding in zip(self.face_locations, self.face_encodings):
                name = "Unknown"
                if not self.known_face_encodings:
                    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
                    # Draw a box around the face
                    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(image, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
                    continue
                # # See if the face is a match for the known face(s)
                # print(self.known_face_encodings)
                # print(face_encoding)
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)



                # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    age = self.known_face_age[best_match_index]
                    position = self.known_face_position[best_match_index]
                    if self.listView != None:
                        self.listView.addItem('\t'.join(map(str,(name, age, position))))
                        self.tts.text = "나이 " + str(age) + "세 " + str(name) + " " + str(position) + "입니다."
                        self.ttsTextView.setText(self.tts.text)
                # Draw a box around the face
                cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX#cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(image, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

"""Image View 카메라 frame을 출력하는 UI"""
class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()

    def initUI(self):
        self.setWindowTitle('Test')

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if(type(image) == type(None)) :
            logging.error("Viewer Dropped frame!")
        else:
            self.image = image
            if image.size() != self.size():
                self.setFixedSize(image.size())
            self.update()

"""module test"""
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    thread = QtCore.QThread()
    thread.start()
    vid = ShowVideo()
    vid.moveToThread(thread)

    image_viewer = ImageViewer()

    vid.VideoSignal.connect(image_viewer.setImage)

    push_button = QtWidgets.QPushButton('Start')
    push_button.clicked.connect(vid.startVideo)
    
    vertical_layout = QtWidgets.QVBoxLayout()
    horizontal_layout = QtWidgets.QHBoxLayout()
    horizontal_layout.addWidget(image_viewer)
    vertical_layout.addLayout(horizontal_layout)
    vertical_layout.addWidget(push_button)

    layout_widget = QtWidgets.QWidget()
    layout_widget.setLayout(vertical_layout)

    main_window = QtWidgets.QMainWindow()
    main_window.setCentralWidget(layout_widget)
    main_window.show()
    sys.exit(app.exec_())