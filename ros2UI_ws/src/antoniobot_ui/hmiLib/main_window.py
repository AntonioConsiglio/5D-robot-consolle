from queue import Queue
import sys
import multiprocessing
from threading import Thread
import time
import os,signal

import subprocess

from PySide2.QtWidgets import QApplication,QMainWindow
from PySide2.QtGui import QImage,QPixmap
from PySide2.QtCore import Signal,QThread

from .widget_styles import *
from .class_utils import PyToggle,loadUi
# from ..utilsLib.videomanager import VideoCamera,VideoHandler
# from ..utilsLib.functions_utils import *
import numpy as np
from PIL import Image

# baud_rates = ['None','9600','19200','38400']
serial_port = 1

class VideoHandler(QThread):

	update_image = Signal(np.ndarray)
	camera_state = Signal(bool)
	newcordinates = Signal(list)

	def __init__(self,image_queue,eventstate,image_size=(640,640)):
		super(VideoHandler,self).__init__()
		self.runtime_state = eventstate 
		self.image_queue = image_queue
		self.image_size = image_size
		self.state = True

	def run(self):

		while self.isRunning():
			
			if self.runtime_state.value == 0: # no calibration - running mode
				if self.image_queue.qsize() > 0:
					image = self.image_queue.get()
					image = Image.fromarray(image).resize(self.image_size)
					image = {"color_image":np.array(image)}
					self.update_image.emit(image)

			if self.runtime_state.value == 1:
				if self.image_queue.qsize() > 0:
					image = self.image_queue.get()
					self.update_image.emit(image)
					if not self.cordinatesqueue.empty():
						self.newcordinates.emit(self.cordinatesqueue.get())
			
			if not self.state or self.runtime_state.value == 2:
				break

	def stop(self):
		self.state = False    

class MainWindow(QMainWindow):
	movexyz = Signal([str,float]) # signal to move robot in xyz with virtual joystick [direction, quontity in mm]

	def __init__(self):
		super(MainWindow,self).__init__()
		loadUi("/home/aconsiglio/5D-robot-consolle/documents/mainwindow.ui",self)
		self.toggle = PyToggle(parent=self.toggle_frame)
		self.image_queue = Queue(maxsize=1)
		self.videohandler = None
		self._define_slots()
		self._define_styles()
		self._define_variables()
		self._define_axis_variables()
		self.detection_mode = multiprocessing.Value('i',0)
		self.running_mode = multiprocessing.Value('i',0) #0 normal mode / 1 detection mode
		self.answarequeue = Queue()
		self.donequeue = Queue()
		self.connection_button.setStyleSheet(self.BStyle.green_button)
		self.hasStartedOnce = False
		# self.baud_rate.addItems(baud_rates)
		self.trd1 = self.trd2 = self.trd3 = None
		self.thread_list = {'1':self.trd1,'2':self.trd2,'3':self.trd3}

	def assing_logger(self,logger):
		self.logger = logger

	def assing_action_client(self,action_client):
		self.action_client = action_client

	def start_video(self,size = (640,640),fps = 30):
		# if self.nn_box.isChecked():
		# 	self.detection_mode.value = 2
		self.running_mode.value = 0
		self.videohandler = VideoHandler(self.image_queue,self.running_mode,size)
		self.videohandler.update_image.connect(self.update_screen)
		self.videohandler.start()

	def _start_external_detection(self):
		if self.running_mode.value != 1:
			self.running_mode.value = 1
		else:
			self.running_mode.value = 0

	def update_screen(self,images):

		for key,image in images.items():
			if key == 'depth':
				continue
			h,w,_ = image.shape
			qimage = QImage(image,w,h,QImage.Format.Format_BGR888)
			qpmap = QPixmap(qimage)
			if key == "color_image":
				self.color_frames.setPixmap(qpmap)
			elif "disparity" in key:
				self.depth_frames.setPixmap(qpmap)

	def _start_autocalibration(self):
		if self.video is not None:
			self.video.stop()
			time.sleep(0.3)
			self.video = None
			self.running_mode.value = 2
			self.video = VideoCamera((1920,1080),30,self.detection_mode,self.running_mode)
			_ = self.video.calibration_state.get()
			time.sleep(1)
			self.start_video()
	
	def inrange(self,cordinate):
		xrange = [-100,100]
		yrange = [50,200]
		zrange = [45,150]
		x,y,z = cordinate
		if x < xrange[0] or x > xrange[1]:
			return False
		if y < yrange[0] or y > yrange[1]:
			return False
		if z < zrange[0] or z > zrange[1]:
			return False
		return True

	def calculate_forward_kinematics(self,list_angles):
		list_angles = robot_to_python_angles(list_angles)
		tm  = self.robot_object.compute_forward_kinematics(list_angles)		
		self.x_pos, self.y_pos, self.z_pos = tm[:3,3]
		self.update_xyz_lcd() 

	def calculate_inverse_kinematics(self,cordinate=None,start_byte=None):

		if cordinate is None:
			self.x_pos = int(self.x_edit.text().strip())
			self.y_pos = int(self.y_edit.text().strip())
			self.z_pos = int(self.z_edit.text().strip())
		else:
			x,y,z = cordinate
			self.x_pos = int(x)
			self.y_pos = int(y)
			self.z_pos = int(z)
		self.update_xyz_lcd()
		target = [self.x_pos/100,self.y_pos/100,self.z_pos/100]
		self.action_client.send_goal(*target)
		# _,j6,j5,j4,j3,j2,_ = self.robot_object.compute_inverse_kinematics(target)
		# if start_byte is None:
		# 	self.__send_angles([j6,j5,j4,j3,j2],True)
		# else:
		# 	self.__send_angles([j6,j5,j4,j3,j2],True,start_byte)
	
	def calculate_inverse_kinematics_joystic(self,direction,qnt):

		if direction == 'x':
			self.x_pos += qnt
		elif direction == 'y':
			self.y_pos += qnt
		elif direction == 'z':
			self.z_pos += qnt
		self.update_xyz_lcd()
		target = [self.x_pos,self.y_pos,self.z_pos]
		_,j6,j5,j4,j3,j2,_ = self.robot_object.compute_inverse_kinematics(target)
		self.__send_angles([j6,j5,j4,j3,j2],True)
	
	def update_angle_lcd(self):

		self.lcd_joint1.display(int(self.joint1))
		self.lcd_joint2.display(int(self.joint2))
		self.lcd_joint3.display(int(self.joint3))
		self.lcd_joint4.display(int(self.joint4))
		self.lcd_joint5.display(int(self.joint5))
		self.lcd_joint6.display(int(self.joint6))
	
	def update_xyz_lcd(self):
		
		self.lcd_x.display(int(self.x_pos))
		self.lcd_y.display(int(self.y_pos))
		self.lcd_z.display(int(self.z_pos))
	
	def is_relesed(self):
		self.socket_arduino.send_data(b'0')

	def sto_premendo(self,data):
		self.socket_arduino.send_data(data)
		print(data)

	def _define_styles(self):
		self.BStyle = ButtonStyle()

	def _update_angles_view(self,data):
		print(f'[RECIVING DATA]: {data}')
		if not self.reciving_current_angles:
			if data == b'1':
				self.joint1 -=1
				self.lcd_joint1.display(self.joint1)
			elif data == b'2':
				self.joint1 +=1
				self.lcd_joint1.display(self.joint1)
			elif data == b'3':
				self.joint2 -=1
				self.lcd_joint2.display(self.joint2)
			elif data == b'4':
				self.joint2 +=1
				self.lcd_joint2.display(self.joint2)
			elif data == b'5':
				self.joint3 -=1
				self.lcd_joint3.display(self.joint3)
			elif data == b'6':
				self.joint3 +=1
				self.lcd_joint3.display(self.joint3)
			elif data == b'7':
				self.joint4 -=1
				self.lcd_joint4.display(self.joint4)
			elif data == b'8':
				self.joint4 +=1
				self.lcd_joint4.display(self.joint4)
			elif data == b'9':
				self.joint5 -=1
				self.lcd_joint5.display(self.joint5)
			elif data == b'10':
				self.joint5 +=1
				self.lcd_joint5.display(self.joint5)
			elif data == b'11':
				self.joint6 -=1
				self.lcd_joint6.display(self.joint6)
			elif data == b'12':
				self.joint6 +=1
				self.lcd_joint6.display(self.joint6)
			elif data == b'35':
				self.reciving_current_angles = True
			elif data == b'54':
				if self.running_mode.value == 4:
					self.answarequeue.put('go_next')
		else:
			if self.number_angle == 0:
				self.joint6 = int(data.decode('utf-8'))
				self.lcd_joint6.display(self.joint6)
				self.number_angle+=1
			elif self.number_angle == 1:
				self.joint5 = int(data.decode('utf-8'))
				self.lcd_joint5.display(self.joint5)
				self.number_angle+=1
			elif self.number_angle == 2:
				self.joint4 = int(data.decode('utf-8'))
				self.lcd_joint4.display(self.joint4)
				self.number_angle+=1
			elif self.number_angle == 3:
				self.joint3 = int(data.decode('utf-8'))
				self.lcd_joint3.display(self.joint3)
				self.number_angle+=1
			elif self.number_angle == 4:
				self.joint2 = int(data.decode('utf-8'))
				self.lcd_joint2.display(self.joint2)
				self.number_angle+=1
			elif self.number_angle == 5:
				self.joint1 = int(data.decode('utf-8'))
				self.lcd_joint1.display(self.joint1)
				self.number_angle = 0
				self.reciving_current_angles = False
				self.calculate_forward_kinematics([self.joint6,self.joint5,self.joint4,
													self.joint3,self.joint2,self.joint1])

	def _change_button_color(self,button,stato):
		if stato=='connected':
			button.setStyleSheet(self.BStyle.red_button)
			button.setText('DISCONNECT')
		elif stato == 'disconnected':
			button.setStyleSheet(self.BStyle.green_button)
			button.setText('CONNECT')

	def run_thread_task(self,**kwargs):
		if self.trd1 is None:
			self.trd1 = self.TaskThread(name='1',**kwargs)
			self.trd1.finished.connect(lambda : self._delete_thread('1'))
			self.trd1.start()
		elif self.trd2 is None:
			self.trd2 = self.TaskThread(name='2',**kwargs)
			self.trd2.finished.connect(lambda : self._delete_thread('2'))
			self.trd2.start()
		elif self.trd3 is None:
			self.trd3 = self.TaskThread(name='3',**kwargs)
			self.trd3.finished.connect(lambda : self._delete_thread('3'))
			self.trd3.start()
		else:
			print('No threads available')

	def _delete_thread(self,name):

		if name == '1':
			print(self.trd1.isRunning())
			self.trd1.exit()
			del self.trd1
			self.trd1 = None
		elif name == '2':
			self.trd2 = None
		elif name == '3':
			self.trd3 = None

	class TaskThread(QThread):
		
		def __init__(self,name=None,funcion=None,cls=None,args=None):
			QThread.__init__(self)
			self.cls = cls
			self.func = funcion
			self.trd_name = name
			self.args = args

		def run(self):
			if self.args is not None:
				state = self.func(self.args)
			elif self.cls is not None and self.args is None:
				state = self.func(self.cls)
			if state:
				self.finished.emit()
			
	def _define_variables(self):
		# angles variables
		self.joint1 = 0
		self.joint2 = 0
		self.joint3 = 0
		self.joint4 = 0
		self.joint5 = 0
		self.joint6 = 0
		self.reciving_current_angles = False
		self.number_angle = 0

	def _define_axis_variables(self):
		self.x_pos = 0
		self.y_pos = 0
		self.z_pos = 0
	
	def _define_slots(self):
		# Join1
		self.menos1.pressed.connect(lambda: self.sto_premendo(b"1"))
		self.menos1.released.connect(self.is_relesed)
		self.plus1.pressed.connect(lambda: self.sto_premendo(b"2"))
		self.plus1.released.connect(self.is_relesed)
		# Joint2
		self.menos2.pressed.connect(lambda: self.sto_premendo(b"3"))
		self.menos2.released.connect(self.is_relesed)
		self.plus2.pressed.connect(lambda: self.sto_premendo(b"4"))
		self.plus2.released.connect(self.is_relesed)
		 # Join3
		self.menos3.pressed.connect(lambda: self.sto_premendo(b"5"))
		self.menos3.released.connect(self.is_relesed)
		self.plus3.pressed.connect(lambda: self.sto_premendo(b"6"))
		self.plus3.released.connect(self.is_relesed)
		# Joint4
		self.menos4.pressed.connect(lambda: self.sto_premendo(b"7"))
		self.menos4.released.connect(self.is_relesed)
		self.plus4.pressed.connect(lambda: self.sto_premendo(b"8"))
		self.plus4.released.connect(self.is_relesed)
		 # Join5
		self.menos5.pressed.connect(lambda: self.sto_premendo(b"9"))
		self.menos5.released.connect(self.is_relesed)
		self.plus5.pressed.connect(lambda: self.sto_premendo(b"10"))
		self.plus5.released.connect(self.is_relesed)
		# Joint6
		self.menos6.pressed.connect(lambda: self.sto_premendo(b"11"))
		self.menos6.released.connect(self.is_relesed)
		self.plus6.pressed.connect(lambda: self.sto_premendo(b"12"))
		self.plus6.released.connect(self.is_relesed)
		# Move robot in xyz with joystick
		self.plusX.clicked.connect(lambda: self.movexyz.emit('x',10.0))
		self.menosX.clicked.connect(lambda: self.movexyz.emit('x',-10.0))
		self.plusY.clicked.connect(lambda: self.movexyz.emit('y',10.0))
		self.menosY.clicked.connect(lambda: self.movexyz.emit('y',-10.0))
		self.plusZ.clicked.connect(lambda: self.movexyz.emit('z',10.0))
		self.menosZ.clicked.connect(lambda: self.movexyz.emit('z',-10.0))
		self.movexyz.connect(self.calculate_inverse_kinematics_joystic)
		# inverse_kinematics
		self.start_invers_kinematic.clicked.connect(self.calculate_inverse_kinematics)
		# Connection button
		self.connection_button.clicked.connect(self.launch_task_server)
		# refresh_button
		#self.refresh_button.clicked.connect(lambda: self.run_thread_task(funcion=update_com_port,cls=self))
		# camera activate
		self.toggle.stateChanged.connect(self.video_state)
		# start autocalibration for camera
		self.autocalibration.clicked.connect(self._start_autocalibration)
		# start external detection 
		self.startdetection.clicked.connect(self._start_external_detection)

	def launch_task_server(self):
		if not self.hasStartedOnce:
			print(f"Launching the Task Server !")
			command = "source ~/5D-robot-consolle/ros2humb_ws/install/setup.bash && ros2 run antoniobot_actions task_server_node"
			self.process = subprocess.Popen(command, shell=True, executable="/bin/bash", preexec_fn=os.setsid)
			self.hasStartedOnce = True
			self._change_button_color(self.connection_button,stato="connected")
			return self.process.poll() is None  # return True if process is running
		else:
			# Implement logic to stop the process here
			if self.process is not None:
				print(f"Killing the process pid: {self.process.pid}")
				os.killpg(os.getpgid(self.process.pid), signal.SIGINT)  # Send the signal to all the process in the group
				self.process = None
				self.hasStartedOnce = False
				self._change_button_color(self.connection_button,stato="disconnected")
			return False



	def video_state(self):

		stato = self.toggle.isChecked()
		self.logger.info(f"Toggler Checked: {stato}")
		if stato:
			if self.videohandler is None:
				self.start_video()
				self.logger.info(f"Video handler activated!")
		else:
			self.videohandler.stop()
			self.videohandler.update_image.disconnect()
			while self.videohandler.isRunning():
				pass
			self.videohandler = None
			self.update_screen({'color_image': np.zeros((480,640,3))})
	
	def closeEvent(self,e):
		if self.videohandler is not None:
			self.videohandler.stop()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	root = MainWindow(app)
	root.show()
	app.exec_()