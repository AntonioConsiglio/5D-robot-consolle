from ast import Break
from PySide2.QtCore import QThread,Signal
import numpy as np
import torch
import cv2

from ..cameraLib import DeviceManager
from ..cameraLib.camera_funcion_utils import create_pointcloud_manager,visualise_Axes
from ..cameraLib.calibrationLib import docalibration
from ..utilsLib.functions_utils import write_fps
from .detectormanager import DetectionManager
import config

import time
from multiprocessing import Process,Queue

class VideoHandler(QThread):

	update_image = Signal(np.ndarray)
	camera_state = Signal(bool)
	newcordinates = Signal(list)

	def __init__(self,image_queue,eventstate,cordinatesqueue):
		super(VideoHandler,self).__init__()
		self.runtime_state = eventstate 
		self.image_queue = image_queue
		self.cordinatesqueue = cordinatesqueue
		self.state = True

	def run(self):

		while self.isRunning():
			
			if self.runtime_state.value == 0: # no calibration - running mode
				image = self.image_queue.get()
				self.update_image.emit(image)

			if self.runtime_state.value == 1:
				image = self.image_queue.get()
				self.update_image.emit(image)
				if not self.cordinatesqueue.empty():
					self.newcordinates.emit(self.cordinatesqueue.get())
			
			if not self.state or self.runtime_state.value == 2:
				break

	def stop(self):
		self.state = False     


class VideoCamera():

	def __init__(self,size,fps,nn_activate,running_mode):
		super(VideoCamera,self).__init__()
		self.nn_activate = nn_activate
		self.size = size
		self.fps = fps
		self.camera = None
		self.running_mode = running_mode  #0 normal runtime / 1 calibration  runtime
		self.calibration_info = None
		self.pointcloud_manager = None
		self.imgqueue = Queue()
		self.stoqueue = Queue()
		self.cordinates_queue = Queue()
		self.calibration_state = Queue()
		self.p = Process(name='DeviceManager',target = self.run,args = [self.size,self.fps,self.nn_activate,
																		self.running_mode,self.stoqueue,
																		self.imgqueue,self.calibration_state,
																		self.cordinates_queue])
		self.p.start()
		
	def run(self,size,fps,nn_activate,running_mode,stoqueue,imgqueue,calibrationstate,cordinatesqueue):
		self.oakd_camera = config.OAKD_CAMERA
		try:
			self.camera = DeviceManager(size,fps,nn_mode = nn_activate,calibration_mode=running_mode)
			self.calibration_info = self.camera.enable_device()
			self.pointcloud_manager = create_pointcloud_manager('first_camera',self.calibration_info)
			self.oakd_camera = True
		except Exception as e:
			print(e)
			self.camera = cv2.VideoCapture(config.SOURCE)
		self.detector_manager = DetectionManager()
		self.detector_manager.load_yolor_model()
		self.running_mode = running_mode
		self.calibration_state = calibrationstate
		self.cordinates_queue = cordinatesqueue
		self.cordinates_sended = 0
		start_sending = None
		while stoqueue.empty():
			toc = time.time()
			if self.running_mode.value == 0: # only camera
				stato = False
				if self.oakd_camera:
					stato,frames,_= self.camera.pull_for_frames()
				else:
					frames = {}
					stato,frames['color_image'] = self.camera.read()
				if stato:
					frames['color_image'] = visualise_Axes(frames['color_image'],self.pointcloud_manager.calibration_info)
					self.imgqueue.put(write_fps(toc,frames))
			
			if self.running_mode.value == 1: #external detecion mode
				stato = False
				points_cloud_data = None
				if self.oakd_camera:
					stato,frames,_ = self.camera.pull_for_frames()
				else:
					frames = {}
					stato,frames['color_image'] = self.camera.read()
				if stato:
					frames['color_image'],detections = self.detector_manager.predict(frames['color_image'])
					try:
						points_cloud_data = self.pointcloud_manager.start_calculation(depth_image=frames['depth'],
																	color_image=frames['color_image'],
																	APPLY_ROI=False,
																	Kdecimation=1,
																	ZmmConversion=1,
																	depth_threshold=0.001,
																	viewROI=self.pointcloud_manager.viewROI
																	)
					except Exception as e:
						print(e)
					if points_cloud_data is not None:
						cordinates = self.pointcloud_manager._determinate_object_location(frames['color_image'],
																			 			  points_cloud_data,
																			 			  detections)
						if len(cordinates)>0:
							if self.cordinates_sended == 0:
								self.cordinates_queue.put(cordinates)
								self.cordinates_sended+=1
						frames['color_image'] = visualise_Axes(frames['color_image'],self.pointcloud_manager.calibration_info)																
					self.imgqueue.put(write_fps(toc,frames))
					
			
			if self.running_mode.value == 2: #calibration mode
				intrinsic, extrinsic = self.camera.get_intrisic_and_extrinsic()
				_= docalibration(self.camera,intrinsic,extrinsic,[16,9,15],[0,0,1080,1920],shiftcalibration=[0,0,0])
				self.pointcloud_manager = create_pointcloud_manager(_,self.calibration_info,False,self.pointcloud_manager)
				self.stop()
				self.calibration_state.put(True)
			
			if self.running_mode.value == 3: #Edge detection mode
				pass
			
			if self.running_mode.value == 4: #waiting robot picking objects
				if self.cordinates_sended > 0:
					print('SENDED')
					start_sending = time.time()
					self.cordinates_sended = 0

			if not stoqueue.empty():
				break
	
	def get_intrisic_and_extrinsic(self):
		'''
		return the intrisics [rgb and left] and extrinsic [left to RGB]
		'''
		self.camera.get_intrinsic()
		self.camera.get_extrinsic()
		return self.camera.intrinsic_info,self.camera.extrinsic_info

	def stop(self):
		self.stoqueue.put(False)        

