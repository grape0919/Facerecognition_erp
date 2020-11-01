import os
from gtts import gTTS
import threading, requests, time
#from static import staticValues
import pygame
from PyQt5.QtWidgets import QListWidget

class TTSManager(threading.Thread):
    isRunning = False
    text =""
    textBuff = ""
    tempFile = ".\\tts\\tts.mp3"
    lock = threading.Lock()
    global tts
    def __init__(self, listView=None):
        threading.Thread.__init__(self)
        self.listView = listView
 
    def run(self):
        self.isRunning = True
        # self.id = self.listView.itemAt(0)
        while(self.isRunning):
            if(self.text == ""):
                continue
            else:
                self.textBuff = self.text
                isWritten = self.generateTTS()
                # if(self.listView != None):
                #     for s in self.listView.items():
                #         if(s.text() == self.text):
                #             self.playSound()
                #             break
                if isWritten:
                    self.playSound()

                self.text=""

    def generateTTS(self):
        print("생성중")
        
        self.lock.acquire()
        try:
            tts = gTTS(text=self.textBuff, lang='ko')
            tts.save(self.tempFile)
            return True
        except:
            print("mp3파일을 쓰는 도중 문제가 발생하였습니다.")
            return False
        finally:
            self.lock.release()
        print("생성끝")

    def playSound(self):
        print("재생중")
        freq = 24000    # sampling rate, 44100(CD), 16000(Naver TTS), 24000(google TTS)
        bitsize = -16   # signed 16 bit. support 8,-8,16,-16
        channels = 1    # 1 is mono, 2 is stereo
        buffer = 2048   # number of samples (experiment to get right sound)

        # default : pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        pygame.mixer.init(freq, bitsize, channels, buffer)
        pygame.mixer.music.load(self.tempFile)
        pygame.mixer.music.play()

        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            clock.tick(30)
        pygame.mixer.quit()
        print("재생끝")

# """TTS TEST"""
# tts = TTSManager("변경된 TTS 파일을 재생 합니다.")
# tts.start()
# tts.playSound()
