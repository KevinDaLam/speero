from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QPixmap, QApplication
import sys
import time
import signal
import requests
import os
import base64
import numpy as np
from random import shuffle

from maki_lib.mic.MicIO import MicIO
from maki_driver.uart_driver import UARTDriver

ENABLE_MAKI = True

GUI_IMG_PATH = "/home/maki/speero/gui/GUI-IMG"
AUDIO_FILE_PATH = "/home/maki/speero/gui/maki_lib/mic/scripts"

SERVER_ENDPOINT = "http://3.89.211.71:3000"
# SERVER_ENDPOINT = "https://my-json-server.typicode.com/KevinDaLam/json-test"

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

ERROR_RESULT = -1
OUTSTANDING_RESULT = 0
EXCELLENT_RESULT = 1
VERY_GOOD_RESULT = 2

OUTSTANDING_THRESHOLD = 80
EXCELLENT_THRESHOLD = 75

class getResultsResponse(QtCore.QThread):
    def __init__(self, parent=None):
        super(getResultsResponse, self).__init__(parent)

    def __del__(self):
        self.wait()

    def run(self):
        print('Waiting for HTTP request for results ...')

        with open(self.parent().wav_file_path, 'rb') as f:
            audio_encoded = base64.b64encode(f.read())

        audio_obj = {
            "content": audio_encoded,
            "sampleRate": 48000,
            "encoding": "WAV",
            "languageCode": "en-US",
            "patient_id": "patient_" + str(self.parent().patient_number),
        }

        print("Sending post request for patient " + str(self.parent().patient_number))
        r = requests.post(SERVER_ENDPOINT + "/audio", data = audio_obj)
        if r.status_code == 201:
            print('Success post request')
            print(r.text)
        else:
            print('Unsuccessful HTTP Post: {}'.format(r.status_code))

        print ("Sending get request for patient " + str(self.parent().patient_number))
        r = requests.get(SERVER_ENDPOINT + "/metric/patient_" + str(self.parent().patient_number))
        if r.status_code == 200:
            response_json = r.json()
            score = int(response_json[str(max(int(k) for k in response_json))]['score'])
            print('Received Score: {}'.format(score))
            if score >= OUTSTANDING_THRESHOLD:
                self.parent().result = OUTSTANDING_RESULT
            elif score >= EXCELLENT_THRESHOLD:
                self.parent().result = EXCELLENT_RESULT
            else:
                self.parent().result = VERY_GOOD_RESULT
        else:
            print('Unsuccessful HTTP Get: {}'.format(r.status_code))
            self.parent().result = ERROR_RESULT


class playAudio(QtCore.QThread):
    def __init__(self, parent=None): #audio_path):
        super(playAudio, self).__init__(parent)
        #self.audio_file = audio_path

    def __del__(self):
        self.wait()

    def run(self):
        print('Playing audio file: ' + self.parent().audio_file)
        os.system("aplay %s" % self.parent().audio_file)

class moveRobot(QtCore.QThread):
    def __init__(self, parent=None):
        super(moveRobot, self).__init__(parent)

    def __del__(self):
        self.wait()

    def run(self):
        print('Moving Robot: ' + str(self.parent().commands))
        time.sleep(self.parent().command_delay)
        for c in self.parent().commands:
            self.parent().uart.transmit(c)
            time.sleep(self.parent().command_delay)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtGui.QStackedWidget()
        self.setGeometry(0,0,800,480)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Speero")
        QApplication.setOverrideCursor(QtCore.Qt.BlankCursor)

        self.micIO = MicIO()
        self.recording = []
        self.wav_file_path = "/home/maki/recording.wav"

        self.audio_device_index = self.micIO.search_audio_devices('USB PnP Audio Device: Audio (hw:1,0)')
        if not self.audio_device_index:
            print('Could not find mic')
        else:
            print('Using audio device index %d' % self.audio_device_index)

        if ENABLE_MAKI:
            self.uart = UARTDriver(UART_PORT_NAME, 57600)
            print ("Waiting for Arbotix to Load...")
            time.sleep(10)
            self.robot_thread = moveRobot(self)
            self.commands = [COMMAND_MOVE_WAVE_HELLO, COMMAND_MOVE_HOME]
            self.command_delay = 3.5
            self.robot_thread.start()

        start_screen = StartScreen(self)
        self.central_widget.addWidget(start_screen)

        # Play demo intro audio
        self.audio_thread = playAudio(self)
        self.audio_file = AUDIO_FILE_PATH + "/start-demo.wav"
        self.audio_thread.start()

        #Variable which carries the result
        self.result = -1
        self.patient_number = None

    def callbackMicIO(self, data):
        audio = np.frombuffer(data, dtype=np.int16).tolist()
        self.recording += audio

    def callbackStartDemoButton(self):
        user_screen = SelectUserScreen(self)
        self.central_widget.addWidget(user_screen)
        self.central_widget.setCurrentWidget(user_screen)

        # Play selecte user audio
        self.audio_file = AUDIO_FILE_PATH + "/select-a-user.wav"
        self.audio_thread.start()

        if ENABLE_MAKI:
            self.uart.transmit(COMMAND_MOVE_HUG)
            self.uart.transmit(COMMAND_MOVE_HOME)

    def callbackUserButton(self, patient_number):

        def callbackUser():
            act_screen = ActivityOneScreen(self)
            self.central_widget.addWidget(act_screen)
            self.central_widget.setCurrentWidget(act_screen)

            # Play activity explination
            self.audio_file = AUDIO_FILE_PATH + "/activity-one.wav"
            self.audio_thread.start()
            self.patient_number = patient_number
            if ENABLE_MAKI:
                self.uart.transmit(COMMAND_MOVE_IDLE)
                self.uart.transmit(COMMAND_MOVE_HOME)

        return callbackUser

    def callbackStartActButton(self):
        act1_screen = PlayActOneScreen(self)
        self.central_widget.addWidget(act1_screen)
        self.central_widget.setCurrentWidget(act1_screen)

        self.micIO.listen(self.callbackMicIO, device_index=self.audio_device_index)

    def callbackFinishActButton(self):
        self.micIO.stop()
        self.recording = np.array(self.recording)
        self.recording = self.recording.astype(np.int16)
        self.micIO.save(self.wav_file_path, self.recording)
        self.recording = []

        process_screen = ProcessingScreen(self)
        self.central_widget.addWidget(process_screen)
        self.central_widget.setCurrentWidget(process_screen)

        self.resp_thread = getResultsResponse(self)
        self.connect(self.resp_thread, QtCore.SIGNAL("finished()"), self.callbackResultsScreen)
        self.resp_thread.start()

        if ENABLE_MAKI:
            self.uart.transmit(COMMAND_MOVE_WOAH)
            self.robot_thread = moveRobot(self)
            self.commands = [COMMAND_MOVE_IDLE, COMMAND_MOVE_HUG, COMMAND_MOVE_HOME]
            shuffle(self.commands)
            self.command_delay = 3
            self.robot_thread.start()

    def callbackResultsScreen(self):

        if self.result == OUTSTANDING_RESULT:
            results_screen_A = ResultsScreenA(self)
            self.central_widget.addWidget(results_screen_A)
            self.central_widget.setCurrentWidget(results_screen_A)

            # Play outstanding clip
            self.audio_file = AUDIO_FILE_PATH + "/results-outstanding.wav"
            self.audio_thread.start()
            if ENABLE_MAKI:
                self.uart.transmit(COMMAND_MOVE_FORTNITE_DANCE)
                self.uart.transmit(COMMAND_MOVE_HOME)

        elif self.result == EXCELLENT_RESULT:
            results_screen_B = ResultsScreenB(self)
            self.central_widget.addWidget(results_screen_B)
            self.central_widget.setCurrentWidget(results_screen_B)

            # Play excellent clip
            self.audio_file = AUDIO_FILE_PATH + "/results-excellent.wav"
            self.audio_thread.start()
            if ENABLE_MAKI:
                self.uart.transmit(COMMAND_MOVE_EXCITED)

        elif self.result == VERY_GOOD_RESULT:
            results_screen_C = ResultsScreenC(self)
            self.central_widget.addWidget(results_screen_C)
            self.central_widget.setCurrentWidget(results_screen_C)

            # Play very good clip
            self.audio_file = AUDIO_FILE_PATH + "/results-very-good.wav"
            self.audio_thread.start()
            if ENABLE_MAKI:
                self.uart.transmit(COMMAND_MOVE_HAPPY)
        else:
            results_screen_error = ResultsScreenError(self)
            self.central_widget.addWidget(results_screen_error)
            self.central_widget.setCurrentWidget(results_screen_error)
            if ENABLE_MAKI:
                self.uart.transmit(COMMAND_MOVE_WOAH)

    def callbackExitButton(self):
        self.resp_thread.exit()
        self.audio_thread.exit()
        self.close()


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

        self.buttonUser1.clicked.connect(self.parent().callbackUserButton(0))
        self.buttonUser2.clicked.connect(self.parent().callbackUserButton(1))
        self.buttonUser3.clicked.connect(self.parent().callbackUserButton(2))



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
        self.act1_text = QtGui.QPixmap("%s/Play-act-1-1.png" % GUI_IMG_PATH)
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

        # Make processing button
        self.buttonExit = QtGui.QPushButton()
        self.buttonExit.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonExit.setStyleSheet("QPushButton {background-image: url(%s/processing.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonExit)

        self.setLayout(layout)

        self.buttonExit.clicked.connect(self.parent().callbackExitButton)


class ResultsScreenA(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ResultsScreenA, self).__init__(parent)


        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);

        # Exit Button
        self.buttonExit = QtGui.QPushButton()
        self.buttonExit.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonExit.setStyleSheet("background-color: rgb(228,230,229);")
        layout.addWidget(self.buttonExit, 2)


        self.results_text = QtGui.QPixmap("%s/resA.png" % GUI_IMG_PATH)

        self.results_text = self.results_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_results_text = QtGui.QLabel()
        self.label_results_text.setPixmap(self.results_text)
        self.label_results_text.setAlignment(QtCore.Qt.AlignCenter);
        self.label_results_text.setStyleSheet("background-color: rgb(250,192,191);")
        layout.addWidget(self.label_results_text, 4)

        # Add return to user screen button
        self.buttonReturnUser = QtGui.QPushButton()
        self.buttonReturnUser.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonReturnUser.setStyleSheet("QPushButton {background-image: url(%s/return.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonReturnUser, 2)

        self.setLayout(layout)

        self.buttonReturnUser.clicked.connect(self.parent().callbackStartDemoButton)
        #self.buttonExit.clicked.connect(self.parent().callbackExitButton)

class ResultsScreenB(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ResultsScreenB, self).__init__(parent)


        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);


       # Exit Button
        self.buttonExit = QtGui.QPushButton()
        self.buttonExit.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonExit.setStyleSheet("background-color: rgb(228,230,229);")
        layout.addWidget(self.buttonExit, 2)


        self.results_text = QtGui.QPixmap("%s/resB.png" % GUI_IMG_PATH)

        self.results_text = self.results_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_results_text = QtGui.QLabel()
        self.label_results_text.setPixmap(self.results_text)
        self.label_results_text.setAlignment(QtCore.Qt.AlignCenter);
        self.label_results_text.setStyleSheet("background-color: rgb(250,192,191);")
        layout.addWidget(self.label_results_text,4)

        # Add return to user screen button
        self.buttonReturnUser = QtGui.QPushButton()
        self.buttonReturnUser.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonReturnUser.setStyleSheet("QPushButton {background-image: url(%s/return.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonReturnUser, 2)

        self.setLayout(layout)

        self.buttonReturnUser.clicked.connect(self.parent().callbackStartDemoButton)
        self.buttonExit.clicked.connect(self.parent().callbackExitButton)

class ResultsScreenC(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ResultsScreenC, self).__init__(parent)


        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);

        # Exit Button
        self.buttonExit = QtGui.QPushButton()
        self.buttonExit.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonExit.setStyleSheet("background-color: rgb(228,230,229);")
        layout.addWidget(self.buttonExit, 2)


        self.results_text = QtGui.QPixmap("%s/resC.png" % GUI_IMG_PATH)

        self.results_text = self.results_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_results_text = QtGui.QLabel()
        self.label_results_text.setPixmap(self.results_text)
        self.label_results_text.setAlignment(QtCore.Qt.AlignCenter);
        self.label_results_text.setStyleSheet("background-color: rgb(250,192,191);")
        layout.addWidget(self.label_results_text,4)

        # Add return to user screen button
        self.buttonReturnUser = QtGui.QPushButton()
        self.buttonReturnUser.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonReturnUser.setStyleSheet("QPushButton {background-image: url(%s/return.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonReturnUser, 2)

        self.setLayout(layout)

        self.buttonReturnUser.clicked.connect(self.parent().callbackStartDemoButton)
        self.buttonExit.clicked.connect(self.parent().callbackExitButton)

class ResultsScreenError(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ResultsScreenError, self).__init__(parent)


        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0);
        layout.setContentsMargins(0, 0, 0, 0);

        # Exit Button
        self.buttonExit = QtGui.QPushButton()
        self.buttonExit.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonExit.setStyleSheet("background-color: rgb(228,230,229);")
        layout.addWidget(self.buttonExit, 2)


        self.results_text = QtGui.QPixmap("%s/resError.png" % GUI_IMG_PATH)

        self.results_text = self.results_text.scaled(800, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_results_text = QtGui.QLabel()
        self.label_results_text.setPixmap(self.results_text)
        self.label_results_text.setAlignment(QtCore.Qt.AlignCenter);
        self.label_results_text.setStyleSheet("background-color: rgb(255,100,100);")
        layout.addWidget(self.label_results_text, 4)

        # Add return to user screen button
        self.buttonReturnUser = QtGui.QPushButton()
        self.buttonReturnUser.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.buttonReturnUser.setStyleSheet("QPushButton {background-image: url(%s/return.png); background-position: center;}" % GUI_IMG_PATH)
        layout.addWidget(self.buttonReturnUser, 2)

        self.setLayout(layout)

        self.buttonReturnUser.clicked.connect(self.parent().callbackStartDemoButton)
        self.buttonExit.clicked.connect(self.parent().callbackExitButton)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app.exec_()
