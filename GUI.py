from PyQt4 import QtCore, QtGui
#from PyQt4.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel
import sys
from PyQt4.QtGui import QPixmap
import time

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtGui.QStackedWidget()
        self.setGeometry(0,0,800,480)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Speero")  
           

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

    def callbackFinishActButton(self):
        process_screen = ProcessingScreen(self)
        self.central_widget.addWidget(process_screen)
        self.central_widget.setCurrentWidget(process_screen)

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
        self.logo = QtGui.QPixmap("/home/harminder/fydp/GUI-IMG/Logo-tshirt-pt1-cp.png")
        self.logo = self.logo.scaled(500, 400, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_logo = QtGui.QLabel()
        #self.label_logo.setGeometry(20,20,10,10)
        self.label_logo.setPixmap(self.logo) 
        self.label_logo.setStyleSheet("background-color: rgb(250,192,191);")
        layout.addWidget(self.label_logo, 2)


        # Add start demo button
        self.buttonStartDemo = QtGui.QPushButton()
        self.buttonStartDemo.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonStartDemo.setStyleSheet("QPushButton {background-image: url(/home/harminder/fydp/GUI-IMG/start_dem.png); background-position: center;}")
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
        self.act1 = QtGui.QPixmap("/home/harminder/fydp/GUI-IMG/activity1.png")
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
        self.buttonStartAct.setStyleSheet("QPushButton {background-image: url(/home/harminder/fydp/GUI-IMG/start-acitivty.png); background-position: center;}")
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
        self.act1_text = QtGui.QPixmap("/home/harminder/fydp/GUI-IMG/Play-act-1.png")
        self.act1_text = self.act1_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_act1_text = QtGui.QLabel()
        self.label_act1_text.setPixmap(self.act1_text) 
        self.label_act1_text.setAlignment(QtCore.Qt.AlignCenter);
        layout.addWidget(self.label_act1_text, 3)

        # Add finish acitivty button
        self.buttonFinishAct = QtGui.QPushButton()
        self.buttonFinishAct.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonFinishAct.setStyleSheet("QPushButton {background-image: url(/home/harminder/fydp/GUI-IMG/finish-acitivty.png); background-position: center;}")
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
        self.process_text = QtGui.QPixmap("/home/harminder/fydp/GUI-IMG/processing.png")
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
        
        
        self.results_text = QtGui.QPixmap("/home/harminder/fydp/GUI-IMG/resA.png")
                
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
        
        
        self.results_text = QtGui.QPixmap("/home/harminder/fydp/GUI-IMG/resB.png")
                
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
    app.exec_()