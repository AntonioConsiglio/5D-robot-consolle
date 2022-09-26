from PySide2.QtCore import QThread,Signal
import numpy as np
import torch

from ..cameraLib import DeviceManager
from ..cameraLib.calibrationLib import docalibration
from ..utilsLib.functions_utils import write_fps
from .detectormanager import DetectionManager
import cv2

import time
from multiprocessing import Process,Queue

class VideoHandler(QThread):

	update_image = Signal(np.ndarray)
	camera_state = Signal(bool)

	def __init__(self,image_queue,eventstate):
		super(VideoHandler,self).__init__()
		self.runtime_state = eventstate 
		self.image_queue = image_queue
		self.state = True

	def run(self):

		while self.isRunning():
			
			if self.runtime_state.value == 0: # no calibration - running mode
				image = self.image_queue.get()
				self.update_image.emit(image)

			if not self.state or self.runtime_state == 1:
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
		self.imgqueue = Queue()
		self.stoqueue = Queue()
		self.calibration_state = Queue()
		self.p = Process(name='DeviceManager',target = self.run,args = [self.size,self.fps,self.nn_activate,
																		self.running_mode,self.stoqueue,
																		self.imgqueue,self.calibration_state])
		self.p.start()
		
	def run(self,size,fps,nn_activate,running_mode,stoqueue,imgqueue,calibrationstate):
		self.oakd_camera = False
		try:
			self.camera = DeviceManager(size,fps,nn_mode = nn_activate,calibration_mode=running_mode)
			self.camera.enable_device()
			self.oakd_camera = True
		except:
			self.camera = cv2.VideoCapture(0)
		self.detector_manager = DetectionManager()
		self.detector_manager.load_yolor_model()
		self.running_mode = running_mode
		self.calibration_state = calibrationstate
		
		while stoqueue.empty():
			toc = time.time()
			if self.running_mode.value == 1:
				stato = False
				if self.oakd_camera:
					stato,frames = self.camera.pull_for_frames()
				else:
					frames = {}
					stato,frames['color_image'] = self.camera.read()
				if stato:
					self.imgqueue.put(write_fps(toc,frames))
					
			
			if self.running_mode.value == 2:
				intrinsic, extrinsic = self.camera.get_intrisic_and_extrinsic()
				_ = docalibration(self.camera,intrinsic,extrinsic,[16,9,15],[0,0,1080,1920],shiftcalibration=[0,0,0])
				self.stop()
				self.calibration_state.put(True)
			
			if self.running_mode.value == 0:
				stato = False
				if self.oakd_camera:
					stato,frames = self.camera.pull_for_frames()
				else:
					frames = {}
					stato,frames['color_image'] = self.camera.read()
				if stato:
					image,detections = self.detector_manager.predict(frames['color_image'])
					frames['color_image'] = image
					self.imgqueue.put(write_fps(toc,frames))

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

