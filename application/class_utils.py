#import ptvsd
import PyQt5
from PyQt5.QtCore import QThread,pyqtSignal,QObject,pyqtProperty,Qt
from PyQt5.QtWidgets import QCheckBox
import cv2
import numpy as np

from .telecamera import DeviceManager

import serial
import time
from multiprocessing import Queue
from threading import Thread
import math

class VideoCamera(QThread):
    update_image = pyqtSignal(np.ndarray)
    camera_state = pyqtSignal(bool)

    def __init__(self,size,fps,nn_activate):
        super(VideoCamera,self).__init__()
        self.nn_activate = nn_activate
        self.camera = DeviceManager(size,fps,nn_mode = nn_activate)
        self.state = True
        
    def run(self):
        self.camera.enable_device()
        while self.isRunning():
            stato,frames = self.camera.poll_for_frames()
            if stato:
                self.update_image.emit(frames['color_image'])
            if not self.state:
                break

    def stop(self):
        self.state = False        


class ArduinoConnection(QObject):

    connection_state = pyqtSignal(str)

    def __init__(self):
        super(ArduinoConnection,self).__init__()
        self.arduino = None
        self.data = None
        self.reader = ArduinoReader()
    
    def set_connection_variable(self,porta,baud_rate):
        porta = str(porta.currentText())
        try:
            baud_rate = int(baud_rate.currentText())
        except:
            baud_rate = None
        self.porta = porta
        self.baud_rate = baud_rate

    def send_angles(self,angles_list,inverse_kinematics = False):
        
        if inverse_kinematics:
            angles_list = [math.degrees(i) for i in angles_list]
            angles_list_int = [int(i+90) for i in angles_list]
            angles_list = [str(i) for i in angles_list_int]
        else:
            angles_list = [i.get().strip() for i in angles_list]
            angles_int_list = [math.radians(int(i)-90) for i in angles_list]
            
        self.arduino.write(b'17')
        time.sleep(0.05)
        message = ','.join(angles_list)
        self.arduino.write(message.encode('UTF-8'))

        return angles_list_int

        # if not inverse_kinematics:    
        #     angles_int_list.insert(0,0)
        #     angles_int_list.append(0)
        #     t_matrix = self.robot_obj.forward_kinematics(angles_int_list)
        #     position = np.round(t_matrix[:3,3],0)
        #     print(f'x: {position[0]} mm y: {position[1]} mm z: {position[2]} mm')
       
    def send_data(self,data):
        if self.arduino is not None:
            self.arduino.write(data)

    def connection(self,porta,baud_rate):
        if self.arduino is None:
            self.set_connection_variable(porta,baud_rate)
            if self.porta != 'None' and self.baud_rate is not None:
                print(self.porta,self.baud_rate)
                try:
                    self.arduino = serial.Serial(port=self.porta,baudrate=self.baud_rate)
                    print('Connesso !')
                    self.connection_state.emit('connected')
                    self.reader.set_serial(self.arduino)
                    self.reader.connection_state = True
                    self.reader.start()
                    self.arduino.write(b'35')
                except:
                    print('no connection available')
                    self.connection_state.emit('no_connection')
            else:
                print("select better the baud rate and com port")
        else:
            self.disconnet()
    
    def disconnet(self):
        self.reader.connection_state = False
        while self.reader.isRunning(): pass
        self.arduino.close()
        self.arduino = None
        self.connection_state.emit('disconnected')
        print('Disconnesso !')
    

class ArduinoReader(QThread):
    message_recived =pyqtSignal(bytes)
    def __init__(self,):
        super(ArduinoReader,self).__init__()
        self.socket = None
        self.connection_state=None
        self.first_send = True

    def set_serial(self,arduino):
        self.socket = arduino
    
    def set_first_send(self,condition):
        self.first_send = condition

    def run(self):
        #ptvsd.debug_this_thread()
        while self.connection_state:
            message = b''
            while self.socket.in_waiting:
                if  self.first_send:
                    time.sleep(0.01)
                    self.set_first_send(False)
                lettera = self.socket.read(1)#.decode('utf-8')
                if lettera != b'\r':
                    if lettera != b'\n':
                        message+=lettera  
                    else:
                        self.message_recived.emit(message)
                        message =b''                

class PyToggle(QCheckBox):
    
    def __init__(self,
                parent = None,
                width=60,
                bg_color = "#777",
                circle_color = "#000",
                active_color = "#00BCff",
                animation_curve = PyQt5.QtCore.QEasingCurve.OutBounce,
                ):

        super().__init__(parent)
        self.setFixedSize(width,26)
        self.setCursor(Qt.PointingHandCursor)

        # COLORS

        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color

        # ANIMATION

        self._circle_position = 3
        self.animation = PyQt5.QtCore.QPropertyAnimation(self,b"circle_position",self)
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(500)

        # CONNECT STATE CHANGED

        self.stateChanged.connect(self.start_transition)

    @pyqtProperty(float)
    def circle_position(self):
        return self._circle_position
    
    @circle_position.setter
    def circle_position(self,pos):
        self._circle_position = pos
        self.update()
    
    def start_transition(self,value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(self.width() - 26)
        else:
            self.animation.setEndValue(3)
        
        self.animation.start()
    
    def hitButton(self, pos: PyQt5.QtCore.QPoint):
        return self.contentsRect().contains(pos)

    
    def paintEvent(self,e):
        # SET PAINTER

        p = PyQt5.QtGui.QPainter(self)
        p.setRenderHint(PyQt5.QtGui.QPainter.Antialiasing)

        # SET AS NO PEN
        p.setPen(Qt.NoPen)

        rect = PyQt5.QtCore.QRect(0,0,self.width(),self.height())
        
        if not self.isChecked():
            # DRAW BG
            p.setBrush(PyQt5.QtGui.QColor(self._bg_color))
            p.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)

            # DRAW CIRCLE
            p.setBrush(PyQt5.QtGui.QColor(self._circle_color))
            p.drawEllipse(3,3,21,21)
        else:
            # DRAW BG
            p.setBrush(PyQt5.QtGui.QColor(self._active_color))
            p.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)

            # DRAW CIRCLE
            p.setBrush(PyQt5.QtGui.QColor(self._circle_color))
            p.drawEllipse(self.width() -26 ,3,21,21)

        p.end()




    

