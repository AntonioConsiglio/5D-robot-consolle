import sys
from threading import Thread

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtCore import pyqtSignal,pyqtSlot

from .widget_styles import *
from ..utilsLib.class_utils import *
from ..utilsLib.functions_utils import *
from ..cameraLib.calibrationLib import docalibration

# baud_rates = ['None','9600','19200','38400']
serial_port = 1

class MainWindow(QMainWindow):
	movexyz = pyqtSignal([str,float]) # signal to move robot in xyz with virtual joystick [direction, quontity in mm]

	def __init__(self):
		super(MainWindow,self).__init__()
		loadUi("documents\\mainwindow.ui",self)
		self.toggle = PyToggle(parent=self.toggle_frame)
		self.video = None
		self._define_slots()
		self._define_styles()
		self._define_variables()
		self._define_axis_variables()
		self.connection_button.setStyleSheet(self.BStyle.green_button)
		# self.baud_rate.addItems(baud_rates)
		self.trd1 = self.trd2 = self.trd3 = None
		self.thread_list = {'1':self.trd1,'2':self.trd2,'3':self.trd3}

	def start_video(self,size = (640,480),fps = 30):
		self.video = VideoCamera(size,fps,self.nn_box.isChecked())
		self.video.update_image.connect(self.update_screen)
		self.video.start()

	def update_screen(self,image):

		h,w,_ = image.shape
		qimage = QImage(image,w,h,QImage.Format.Format_BGR888)
		qpmap = QPixmap(qimage)
		self.camera.setPixmap(qpmap)

	@pyqtSlot()
	def _start_autocalibration(self):
		if self.video is not None:
			self.video.calibration_state = True
			self.video = VideoCamera((1920,1080),30,False,True)
			self.video.start()
			time.sleep(5)
			intrinsic, extrinsic = self.video.get_intrisic_and_extrinsic()
			docalibration(self.video.camera,intrinsic,extrinsic,[16,9,15],[0,0,1080,1920],shiftcalibration=[0,0,0])
			self.video.calibration_state = True
			time.sleep(4)
			self.start_video()

	def set_connection_socket(self,arduino):
		self.socket_arduino = arduino
		self.socket_arduino.connection_state.connect(lambda stato: self._change_button_color(self.connection_button,stato))
		self.socket_arduino.reader.message_recived.connect(self._update_angles_view)
	
	def calculate_forward_kinematics(self,list_angles):
		list_angles = robot_to_python_angles(list_angles)
		tm  = self.robot_object.compute_forward_kinematics(list_angles)		
		self.x_pos, self.y_pos, self.z_pos = tm[:3,3]
		self.update_xyz_lcd() 

	@pyqtSlot()
	def calculate_inverse_kinematics(self):
		self.x_pos = int(self.x_edit.text().strip())
		self.y_pos = int(self.y_edit.text().strip())
		self.z_pos = int(self.z_edit.text().strip())
		self.update_xyz_lcd()
		target = [self.x_pos,self.y_pos,self.z_pos]
		_,j6,j5,j4,j3,j2,_ = self.robot_object.compute_inverse_kinematics(target)
		self.__send_angles([j6,j5,j4,j3,j2],True)
	
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

	def __send_angles(self,lista_angoli,inv_kine = False):

		angles = self.socket_arduino.send_angles(lista_angoli,inv_kine)
		self.joint6,self.joint5,self.joint4,self.joint3,self.joint2 = angles
		self.update_angle_lcd()
	
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

	def set_robot_object(self,robot_object):
		self.robot_object = robot_object
	@pyqtSlot()
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

	@pyqtSlot()
	def run_thread_task(self,**kwargs):
		if self.trd1 is None:
			self.trd1 = self.TaskThread(name='1',**kwargs)
			self.trd1.start()
		elif self.trd2 is None:
			self.trd2 = self.TaskThread(name='2',**kwargs)
			self.trd2.start()
		elif self.trd3 is None:
			self.trd3 = self.TaskThread(name='3',**kwargs)
			self.trd3.start()
		else:
			print('No threads available')

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
				if self.trd_name == '1':
					self.cls.trd1 = None
				elif self.trd_name == '2':
					self.cls.trd2 = None
				elif self.trd_name == '3':
					self.cls.trd3 = None

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
		self.connection_button.clicked.connect(lambda: self.socket_arduino.connection(self.com_port,self.baud_rate))
		# refresh_button
		self.refresh_button.clicked.connect(lambda: self.run_thread_task(funcion=update_com_port,cls=self))
		# camera activate
		self.toggle.stateChanged.connect(self.video_state)
		# start autocalibration for camera
		self.autocalibration.clicked.connect(self._start_autocalibration)

	def video_state(self):

		stato = self.toggle.isChecked()
		if stato:
			if self.video is None:
				self.start_video()
		else:
			self.video.stop()
			self.video.update_image.disconnect()
			while self.video.isRunning():
				pass
			self.video = None
			self.update_screen(np.zeros((480,640,3)))


if __name__ == '__main__':
	app = QApplication(sys.argv)
	root = MainWindow(app)
	root.show()
	app.exec_()