#import ptvsd
import PySide2
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QThread,Signal,QObject,Property,Qt,QMetaObject
from PySide2.QtWidgets import QCheckBox
import numpy as np
import config

from ..cameraLib import DeviceManager

import serial
import time
from multiprocessing import Queue
from threading import Thread
import math

class VideoCamera(QThread):
    update_image = Signal(np.ndarray)
    camera_state = Signal(bool)

    def __init__(self,size,fps,nn_activate,calibration_mode = False):
        super(VideoCamera,self).__init__()
        self.nn_activate = nn_activate
        self.camera = DeviceManager(size,fps,nn_mode = nn_activate,calibration_mode=calibration_mode)
        self.state = True
        self.calibration_state = False
        self.calibration_mode = calibration_mode
        
    def run(self):
        self.camera.enable_device()
        while self.isRunning():
            if not self.calibration_mode:
                stato,frames = self.camera.poll_for_frames()
                if stato:
                    self.update_image.emit(frames['color_image'])
            if not self.state or self.calibration_state:
                break
    
    def get_intrisic_and_extrinsic(self):
        '''
        return the intrisics [rgb and left] and extrinsic [left to RGB]
        '''
        self.camera.get_intrinsic()
        self.camera.get_extrinsic()
        return self.camera.intrinsic_info,self.camera.extrinsic_info

    def stop(self):
        self.state = False        


class ArduinoConnection(QObject):

    connection_state = Signal(str)

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
    message_recived =Signal(bytes)
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
                animation_curve = PySide2.QtCore.QEasingCurve.OutBounce,
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
        self.animation = PySide2.QtCore.QPropertyAnimation(self,b"circle_position",self)
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(500)

        # CONNECT STATE CHANGED

        self.stateChanged.connect(self.start_transition)

    @Property(float)
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
    
    def hitButton(self, pos: PySide2.QtCore.QPoint):
        return self.contentsRect().contains(pos)

    
    def paintEvent(self,e):
        # SET PAINTER

        p = PySide2.QtGui.QPainter(self)
        p.setRenderHint(PySide2.QtGui.QPainter.Antialiasing)

        # SET AS NO PEN
        p.setPen(Qt.NoPen)

        rect = PySide2.QtCore.QRect(0,0,self.width(),self.height())
        
        if not self.isChecked():
            # DRAW BG
            p.setBrush(PySide2.QtGui.QColor(self._bg_color))
            p.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)

            # DRAW CIRCLE
            p.setBrush(PySide2.QtGui.QColor(self._circle_color))
            p.drawEllipse(3,3,21,21)
        else:
            # DRAW BG
            p.setBrush(PySide2.QtGui.QColor(self._active_color))
            p.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)

            # DRAW CIRCLE
            p.setBrush(PySide2.QtGui.QColor(self._circle_color))
            p.drawEllipse(self.width() -26 ,3,21,21)

        p.end()


class UiLoader(QUiLoader):
	"""
	Subclass :class:`~PySide.QtUiTools.QUiLoader` to create the user interface
	in a base instance.
	Unlike :class:`~PySide.QtUiTools.QUiLoader` itself this class does not
	create a new instance of the top-level widget, but creates the user
	interface in an existing instance of the top-level class.
	This mimics the behaviour of :func:`PyQt4.uic.loadUi`.
	"""

	def __init__(self, baseinstance, customWidgets=None):
		"""
		Create a loader for the given ``baseinstance``.
		The user interface is created in ``baseinstance``, which must be an
		instance of the top-level class in the user interface to load, or a
		subclass thereof.
		``customWidgets`` is a dictionary mapping from class name to class object
		for widgets that you've promoted in the Qt Designer interface. Usually,
		this should be done by calling registerCustomWidget on the QUiLoader, but
		with PySide 1.1.2 on Ubuntu 12.04 x86_64 this causes a segfault.
		``parent`` is the parent object of this loader.
		"""

		QUiLoader.__init__(self, baseinstance)
		self.baseinstance = baseinstance
		self.customWidgets = customWidgets

	def createWidget(self, class_name, parent=None, name=''):
		"""
		Function that is called for each widget defined in ui file,
		overridden here to populate baseinstance instead.
		"""

		if parent is None and self.baseinstance:
			# supposed to create the top-level widget, return the base instance
			# instead
			return self.baseinstance

		else:
			if class_name in self.availableWidgets():
				# create a new widget for child widgets
				widget = QUiLoader.createWidget(self, class_name, parent, name)

			else:
				# if not in the list of availableWidgets, must be a custom widget
				# this will raise KeyError if the user has not supplied the
				# relevant class_name in the dictionary, or TypeError, if
				# customWidgets is None
				try:
					widget = self.customWidgets[class_name](parent)

				except (TypeError, KeyError) as e:
					raise Exception('No custom widget ' + class_name + ' found in customWidgets param of UiLoader __init__.')

			if self.baseinstance:
				# set an attribute for the new child widget on the base
				# instance, just like PyQt4.uic.loadUi does.
				setattr(self.baseinstance, name, widget)

				# this outputs the various widget names, e.g.
				# sampleGraphicsView, dockWidget, samplesTableView etc.
				#print(name)

			return widget

def loadUi(ui_file,parent):
	loader = UiLoader(parent)
	loader.setWorkingDirectory(config.HOME_PATH)
	widget = loader.load(ui_file)
	QMetaObject.connectSlotsByName(widget)
	return widget


    

