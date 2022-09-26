from PySide2.QtCore import QThread,Signal,QObject
import serial
import time
import math

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

