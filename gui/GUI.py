from PyQt4 import QtCore, QtGui
#from PyQt4.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel
import sys
from PyQt4.QtGui import QPixmap
import time
from maki_lib.mic.Mic import MicTransmitter
import signal

GUI_IMG_PATH = "/home/maki/speero/gui/GUI-IMG"

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtGui.QStackedWidget()
        self.setGeometry(0,0,800,480)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Speero")  
        self.micTX = MicTransmitter()

        self.audio_device_index = self.micTX.micIO.search_audio_devices('USB PnP Audio Device: Audio (hw:1,0)')
        if not self.audio_device_index:
            print('Could not find mic')
        else:
            print('Using audio device index %d' % self.audio_device_index)

        self.micTX.connect('localhost', 900, 901)
        start_screen = StartScreen(self)
        self.central_widget.addWidget(start_screen)

    def callbackStartDemoButton(self):
        act_screen = ActivityOneScreen(self)
        self.central_widget.addWidget(act_screen)
        self.central_widget.setCurrentWidget(act_screen)
    
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

        # HTTP Request -- using sync_wait() for now
        print('Waiting for HTTP request for results ...')
        self.micTX.sync_wait()

        # Add code here to wait for results
        # Based on results initlizie the proper screen  

        results_screen_A = ResultsScreenA(self)
        self.central_widget.addWidget(results_screen_A)
        self.central_widget.setCurrentWidget(results_screen_A)



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


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app.exec_()
