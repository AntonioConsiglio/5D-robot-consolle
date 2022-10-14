try:
	import depthai as dhai
except:
	print('depthai library is not installed!!')
	print('Install depthai library ... "pip install depthai"')
import cv2
import numpy as np
import os
import time

try:
	from .calibrationLib.calibration_kabsch import Transformation 
except:
	print('Impossible to import Transformation class from ..calibrationLib.calibration_kabsch ')

from .camera_funcion_utils import configure_rgb_sensor,configure_depth_sensor,create_pointcloud_manager,visualise_Axes

CURRENT_FOLDER = os.getcwd()
BLOB_FODLER  = os.path.join(CURRENT_FOLDER,"neuralNetwork")
#BLOB_NAME = "mobilenet-ssd_openvino_2021.2_6shave.blob"
BLOB_NAME = "frozen_inference_graph_openvino_2021.4_6shave.blob"
BLOB_PATH = os.path.join(BLOB_FODLER,BLOB_NAME)

ZmmConversion = 1000

# Help functions

def get_available_device():

	available_devices = dhai.Device.getAllAvailableDevices()
	cameras_id = [device.getMxId() for device in available_devices]
	print(cameras_id)

class IntrinsicParameters():
	
	def __init__(self,intrinsic_info,size):

		self.fx = intrinsic_info[0][0]
		self.cx = intrinsic_info[0][2]
		self.fy = intrinsic_info[1][1]
		self.cy = intrinsic_info[1][2]
		self.h = size[1]
		self.w = size[0]

class DeviceManager():

	def __init__(self,size,fps,nn_mode,calibration_mode):
		self.pipeline = dhai.Pipeline()
		self.size = size
		self.fps = fps
		self.nn_active = nn_mode
		self.calibration = calibration_mode
		self._configure_device()
		self.node_list = self.pipeline.getNodeMap()

	def _configure_device(self):

		configure_rgb_sensor(self.pipeline,self.size,self.fps,self.nn_active,BLOB_PATH,self.calibration)
		configure_depth_sensor(self.pipeline,self.calibration)


	def enable_device(self):
		self.device_ = dhai.Device(self.pipeline,usb2Mode=True)
		if self.nn_active.value == 2:
			self.max_disparity = self.node_list[8].initialConfig.getMaxDisparity()
		else:
			self.max_disparity = self.node_list[4].initialConfig.getMaxDisparity()
		self._set_output_queue()
		self.get_intrinsic()
		self.get_extrinsic()
		calibration_info = [self.intrinsic_info['RGB'],self.intrinsic_info['RIGHT'],self.extrinsic_info]

		return calibration_info
		
	def _set_output_queue(self):
		self.q_rgb = self.device_.getOutputQueue("rgb",maxSize = 1,blocking = False)
		self.q_depth = self.device_.getOutputQueue("depth",maxSize = 1,blocking = False)
		self.q_disparity = self.device_.getOutputQueue("disparity",maxSize=1,blocking=False)
		if self.nn_active.value == 2:
			self.q_nn = self.device_.getOutputQueue('neural',maxSize=1,blocking=False)
			self.q_nn_input = self.device_.getOutputQueue('neural_input',maxSize=1,blocking=False)
	
	def _normalize_detections(self,detections):
		det_normal = []
		for detection in detections:
			label = detection.label
			score = detection.confidence
			xmin,ymin,xmax,ymax = detection.xmin,detection.ymin,detection.xmax,detection.ymax
			xmin,xmax = int(xmin*self.size[0]),int(xmax*self.size[0])
			ymin,ymax = int(ymin*self.size[1]),int(ymax*self.size[1])
			det_normal.append([label,score,[xmin,ymin,xmax,ymax]])

		return det_normal
	
	def _write_detections_on_image(self,image,detections):
		for detection in detections:
			xmin,ymin,xmax,ymax = detection[2]
			label = detection[0]
			score = detection[1]
			cv2.rectangle(image,(xmin,ymin),(xmax,ymax),(255,255,255),2)
			cv2.putText(image,f'{label}: {round(score*100,2)} %',(xmin,ymin-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
	
	def _convert_depth(self,depth):
		depth = depth.flatten()/ZmmConversion
		depth = np.reshape(depth,(self.size[1],self.size[0]))
		return depth

	def pull_for_frames(self):
		''' 
		- output:\n
			frame_state: bool \n
			frames: dict[color,depth,disparity]
		'''
		frames = {}
		state_frame = False
		frame_count = 0

		while not state_frame:
			rgb_foto = self.q_rgb.tryGet()
			depth = self.q_depth.get()
			disparity_frame = self.q_disparity.get()
			nn_foto = None
			if self.nn_active.value == 2:
				nn_foto = self.q_nn_input.tryGet()
				nn_detection = self.q_nn.tryGet()
				if nn_detection is not None:
					detections = nn_detection.detections
				else:
					detections = None

			if rgb_foto is not None and depth is not None:
				
				state_frame = True
				frames['color_image'] = rgb_foto.getCvFrame()
				frames['depth'] = self._convert_depth(depth.getFrame()) 
				frames['disparity_image'] = cv2.applyColorMap(disparity_frame.getFrame(),cv2.COLORMAP_JET)#*(255 /self.max_disparity)).astype(np.uint8)
				if nn_foto is not None:
					frames['nn_input'] = nn_foto.getCvFrame()
					if detections is not None:
						detections = self._normalize_detections(detections)
						self._write_detections_on_image(frames['color_image'],detections)
						return state_frame,frames,detections
				return state_frame,frames,None
			else:
				frame_count += 1
				if frame_count > 10:
					print('empty_frame: ',frame_count)
				return False,None,None

	def get_intrinsic(self):
		self.intrinsic_info = {}
		calibration_info = self.device_.readCalibration()
		intr_info_rgb = calibration_info.getCameraIntrinsics(dhai.CameraBoardSocket.RGB,resizeHeight=self.size[1],resizeWidth=self.size[0])
		intr_info_right = calibration_info.getCameraIntrinsics(dhai.CameraBoardSocket.RIGHT,resizeHeight=self.size[1],resizeWidth=self.size[0])
		self.intrinsic_info['RGB'] = IntrinsicParameters(intr_info_rgb,self.size)
		self.intrinsic_info['RIGHT'] = IntrinsicParameters(intr_info_right,self.size)

	def get_extrinsic(self):
		calibration_info = self.device_.readCalibration()
		extrin_info = np.array(calibration_info.getCameraExtrinsics(dhai.CameraBoardSocket.RIGHT,dhai.CameraBoardSocket.RGB))
		extrin_info[:,3] = extrin_info[:,3]/1000 
		self.extrinsic_info = Transformation(trasformation_mat=extrin_info)

	def get_intrisic_and_extrinsic(self):
		return self.intrinsic_info,self.extrinsic_info

if __name__ == '__main__':

	get_available_device()
	cam = DeviceManager((640,480),30,nn_mode=False)
	cam.enable_device()

	frame = 0
	while True:
		stato,frames = cam.pull_for_frames()
		if stato:
			cv2.imshow('frame',frames['color_image'])
			cv2.imshow('disparity map',frames['disparity_image'])
			if cv2.waitKey(1) == ord('q'):
				break

