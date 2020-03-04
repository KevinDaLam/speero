from PyQt4 import QtCore, QtGui
#from PyQt4.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel
from PyQt4.QtGui import QPixmap
import sys
import time
import signal


from maki_lib.mic.Mic import MicTransmitter
from maki_driver.uart_driver import UARTDriver

GUI_IMG_PATH = "/home/maki/speero/gui/GUI-IMG"
AUDIO_FILE_PATH = "/home/maki/speero/gui/maki_lib/mic/scripts"

UART_PORT_NAME = "/dev/ttyUSB0"
COMMAND_MOVE_HOME = b'\x01'
COMMAND_MOVE_HAPPY = b'\x02'
COMMAND_MOVE_EXCITED = b'\x03'
COMMAND_MOVE_IDLE = b'\x04'
COMMAND_MOVE_WAVE_HELLO = b'\x05'
COMMAND_MOVE_HUG = b'\x06'
COMMAND_MOVE_WOAH = b'\x07'
COMMAND_MOVE_FORTNITE_DANCE = b'\x08'
COMMAND_RESET_TORQUE_ENABLE = b'\xaa'

class getResulsResponse(QtCore.QThread):
    def __init__(self, parent=None):
        super(getResulsResponse, self).__init__(parent)
        #QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        # HTTP Request -- using sync_wait() for now
        print('Waiting for HTTP request for results ...')
        #self.sleep(5)
        self.parent().micTX.sync_wait()

        # Modify this depending on the result you get 
        # 0 - Outstanding
        # 1 - Excellent 
        # 2 - Very Good  
        self.parent().result = 1

class playAudio(QtCore.QThread):
    def __init__(self, parent=None) #audio_path):
        super(playAudio, self).__init__(parent)
        #self.audio_file = audio_path

    def __del__(self):
        self.wait()

    def run(self):
        # HTTP Request -- using sync_wait() for now
        print('Playing audio file: ' + self.parent().audio_file)
        self.sleep(2)
        self.parent().micTX.play(self.parent().audio_file)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtGui.QStackedWidget()
        self.setGeometry(0,0,800,480)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Speero")  

        self.micTX = MicTransmitter()
        self.uart = UARTDriver(UART_PORT_NAME, 57600)
        print ("Waiting for Arbotix to Load...")
        time.sleep(10)

        self.audio_device_index = self.micTX.micIO.search_audio_devices('USB PnP Audio Device: Audio (hw:1,0)')
        if not self.audio_device_index:
            print('Could not find mic')
        else:
            print('Using audio device index %d' % self.audio_device_index)

        self.micTX.connect('localhost', 900, 901)
        start_screen = StartScreen(self)
        self.central_widget.addWidget(start_screen)



        self.uart.transmit(COMMAND_MOVE_WAVE_HELLO)
        self.uart.transmit(COMMAND_MOVE_HOME)

        # Play demo intro audio
        self.audio_thread = playAudio(self)
        self.audio_file = AUDIO_FILE_PATH + "/start-demo.wav"
        self.audio_thread.start()

        #Variable which carries the result
        self.result = 0

    def callbackStartDemoButton(self):
        user_screen = SelectUserScreen(self)
        self.central_widget.addWidget(user_screen)
        self.central_widget.setCurrentWidget(user_screen)

        # Play selecte user audio
        self.audio_file = AUDIO_FILE_PATH + "/select-a-user.wav"
        self.audio_thread.start()

        self.uart.transmit(COMMAND_MOVE_IDLE)
        self.uart.transmit(COMMAND_MOVE_HOME)
    
    def callbackUserButton(self):
        act_screen = ActivityOneScreen(self)
        self.central_widget.addWidget(act_screen)
        self.central_widget.setCurrentWidget(act_screen)

        # Play activity explination
        self.audio_file = AUDIO_FILE_PATH + "/acitivty-one.wav"
        self.audio_thread.start()

    def callbackStartActButton(self):
        act1_screen = PlayActOneScreen(self)
        self.central_widget.addWidget(act1_screen)
        self.central_widget.setCurrentWidget(act1_screen)

        self.micTX.start(device_index=self.audio_device_index)

    def callbackFinishActButton(self):
        self.micTX.stop()

        process_screen = ProcessingScreen(self)
        self.central_widget.addWidget(process_screen)
        self.central_widget.setCurrentWidget(process_screen) 

        self.resp_thread = getResulsResponse(self)
        self.connect(self.resp_thread, QtCore.SIGNAL("finished()"), self.callbackResultsScreen)
        self.resp_thread.start()

    def callbackResultsScreen(self):
        
        if self.result == 0:
            results_screen_A = ResultsScreenA(self)
            self.central_widget.addWidget(results_screen_A)
            self.central_widget.setCurrentWidget(results_screen_A) 

            # Play outstanding clip
            self.audio_file = AUDIO_FILE_PATH + "/results-outstanding.wav"
            self.audio_thread.start()

        elif self.result == 1:
            results_screen_B = ResultsScreenB(self)
            self.central_widget.addWidget(results_screen_B)
            self.central_widget.setCurrentWidget(results_screen_B) 

            # Play excellent clip
            self.audio_file = AUDIO_FILE_PATH + "/results-excellent.wav"
            self.audio_thread.start()

        else: # result = 2
            results_screen_C = ResultsScreenC(self)
            self.central_widget.addWidget(results_screen_C)
            self.central_widget.setCurrentWidget(results_screen_C)

            # Play very good clip
            self.audio_file = AUDIO_FILE_PATH + "/results-very-good.wav"
            self.audio_thread.start()



class StartScreen(QtGui.QWidget):
    def __init__(self, parent=None):
        super(StartScreen, self).__init__(parent)
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);
        

        # Add logo 
        self.logo = QtGui.QPixmap("%s/Logo-tshirt-pt1-cp.png" % GUI_IMG_PATH)
        self.logo = self.logo.scaled(500, 400, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_logo = QtGui.QLabel()
        #self.label_logo.setGeometry(20,20,10,10)
        self.label_logo.setPixmap(self.logo) 
        self.label_logo.setStyleSheet("background-color: rgb(250,192,191);")
        layout.addWidget(self.label_logo, 2)


        # Add start demo button
        self.buttonStartDemo = QtGui.QPushButton()
        self.buttonStartDemo.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonStartDemo.setStyleSheet("QPushButton {background-image: url(%s/start_dem.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonStartDemo, 1)


        self.setLayout(layout)

        self.buttonStartDemo.clicked.connect(self.parent().callbackStartDemoButton)


class SelectUserScreen(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SelectUserScreen, self).__init__(parent)
        

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);
        
        # Add user buttons 
        self.buttonUser1 = QtGui.QPushButton()
        self.buttonUser1.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonUser1.setStyleSheet("QPushButton {background-image: url(%s/User1_but.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonUser1,1)

        self.buttonUser2 = QtGui.QPushButton()
        self.buttonUser2.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonUser2.setStyleSheet("QPushButton {background-image: url(%s/User2_but.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonUser2,1)

        self.buttonUser3 = QtGui.QPushButton()
        self.buttonUser3.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonUser3.setStyleSheet("QPushButton {background-image: url(%s/User3_but); background-position: center;}"  % GUI_IMG_PATH)
        layout.addWidget(self.buttonUser3,1)

        self.setLayout(layout)

        self.buttonUser1.clicked.connect(self.parent().callbackUserButton)
        self.buttonUser2.clicked.connect(self.parent().callbackUserButton)
        self.buttonUser3.clicked.connect(self.parent().callbackUserButton)



class ActivityOneScreen(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ActivityOneScreen, self).__init__(parent)
        

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);
        
        # Add activity banner 
        self.act1 = QtGui.QPixmap("%s/activity1.png" % GUI_IMG_PATH)
        self.act1 = self.act1.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_act1 = QtGui.QLabel()
        #self.label_logo.setGeometry(20,20,10,10)
        self.label_act1.setPixmap(self.act1) 
        self.label_act1.setAlignment(QtCore.Qt.AlignCenter);
        #self.label_act1.resize(400, 160)
        layout.addWidget(self.label_act1, 2)

        # Add start acitivty button
        self.buttonStartAct = QtGui.QPushButton()
        self.buttonStartAct.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonStartAct.setStyleSheet("QPushButton {background-image: url(%s/start-acitivty.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonStartAct,1)

        self.setLayout(layout)

        self.buttonStartAct.clicked.connect(self.parent().callbackStartActButton)

class PlayActOneScreen(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PlayActOneScreen, self).__init__(parent)
        

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);
        
        # Add activity text 
        self.act1_text = QtGui.QPixmap("%s/Play-act-1.png" % GUI_IMG_PATH)
        self.act1_text = self.act1_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_act1_text = QtGui.QLabel()
        self.label_act1_text.setPixmap(self.act1_text) 
        self.label_act1_text.setAlignment(QtCore.Qt.AlignCenter);
        layout.addWidget(self.label_act1_text, 3)

        # Add finish acitivty button
        self.buttonFinishAct = QtGui.QPushButton()
        self.buttonFinishAct.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonFinishAct.setStyleSheet("QPushButton {background-image: url(%s/finish-acitivty.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonFinishAct, 1)

        self.setLayout(layout)     

        self.buttonFinishAct.clicked.connect(self.parent().callbackFinishActButton)

class ProcessingScreen(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ProcessingScreen, self).__init__(parent)
        

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);
        
        # Add activity text 
        self.process_text = QtGui.QPixmap("%s/processing.png" % GUI_IMG_PATH)
        self.process_text = self.process_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_process_text = QtGui.QLabel()
        self.label_process_text.setPixmap(self.process_text) 
        self.label_process_text.setAlignment(QtCore.Qt.AlignCenter);
        self.label_process_text.setStyleSheet("background-color: rgb(250,192,191);")
        layout.addWidget(self.label_process_text)

        self.setLayout(layout)   


class ResultsScreenA(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ResultsScreenA, self).__init__(parent)
        

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);
        
        
        self.results_text = QtGui.QPixmap("%s/resA.png" % GUI_IMG_PATH)
                
        self.results_text = self.results_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_results_text = QtGui.QLabel()
        self.label_results_text.setPixmap(self.results_text) 
        self.label_results_text.setAlignment(QtCore.Qt.AlignCenter);
        self.label_results_text.setStyleSheet("background-color: rgb(250,192,191);")
        layout.addWidget(self.label_results_text)

        self.setLayout(layout) 

class ResultsScreenB(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ResultsScreenB, self).__init__(parent)
        

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);
        
        
        self.results_text = QtGui.QPixmap("%s/resB.png" % GUI_IMG_PATH)
                
        self.results_text = self.results_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_results_text = QtGui.QLabel()
        self.label_results_text.setPixmap(self.results_text) 
        self.label_results_text.setAlignment(QtCore.Qt.AlignCenter);
        self.label_results_text.setStyleSheet("background-color: rgb(250,192,191);")
        layout.addWidget(self.label_results_text)

        self.setLayout(layout) 

class ResultsScreenC(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ResultsScreenC, self).__init__(parent)
        

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);
        
        
        self.results_text = QtGui.QPixmap("%s/resC.png" % GUI_IMG_PATH)
                
        self.results_text = self.results_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_results_text = QtGui.QLabel()
        self.label_results_text.setPixmap(self.results_text) 
        self.label_results_text.setAlignment(QtCore.Qt.AlignCenter);
        self.label_results_text.setStyleSheet("background-color: rgb(250,192,191);")
        layout.addWidget(self.label_results_text)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app.exec_()
