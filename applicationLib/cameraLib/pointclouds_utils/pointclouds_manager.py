from .pointclouds_function_utils import *
import cv2
#import ptvsd

class PointsCloudManager:
	def __init__(self,id):

		self.parameters = None
		self.sende = None
		self.receiver = None
		self.stopq = None
		self.viewROI = None
		self.calibration_info = None
		self.id = id
		self._HasData = False
		self.pars = None

	def SetParameters(self, calibration_info,roi_2D,viewROI):
		self.calibration_info = calibration_info
		self.pars = CalculatePointsCloudParameters(calibration_info, roi_2D, viewROI)


	def start_calculation(self,depth_image,color_image,APPLY_ROI,
											Kdecimation,ZmmConversion,
											depth_threshold,viewROI):

		if self.pars is not None:
			try:
				result = CalculatePointsCloud(depth_image,
										  color_image,
										  self.pars,
										  [],
										  self.id,
										  APPLY_ROI,
										  Kdecimation,
										  ZmmConversion,
										  depth_threshold,
										  viewROI)
			except Exception as e:
				print(e)
			if result:
				self.data = result
				return result
			else:
				print('error')
				None

	def _hasresult(self,results):
		self.data = results
		self._HasData = True

	def _determinate_object_location(self,image_to_write,points_cloud_data,detections):

		cordinates = []
		xyz_points = points_cloud_data['XYZ_map_valid']
		for detection in detections:
			xmin,ymin,xmax,ymax = detection[:4].astype(int).tolist()
			xcenter = ((xmin+xmax)//2)
			ycenter = ((ymin+ymax)//2)
			offset = 10
			useful_value = xyz_points[ycenter-offset:ycenter+offset,xcenter-offset:xcenter+offset]
			useful_value = useful_value.reshape((useful_value.shape[0]*useful_value.shape[1],3))
			useful_value = useful_value[np.any(useful_value != 0,axis=1)]
			if useful_value.shape[0] >1:
				avg_pos_obj = (np.mean(useful_value,axis=0)*1000).astype(int)
			else:
				avg_pos_obj= (useful_value*1000).astype(int)
			if not np.all(avg_pos_obj == 0):
				cordinates.append(avg_pos_obj.tolist())
				try:
					x,y,z = avg_pos_obj.tolist()
					cv2.putText(image_to_write,f"x: {x} mm",(xcenter+8,ycenter-30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
					cv2.putText(image_to_write,f'y: {y} mm',(xcenter+8,ycenter-15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
					cv2.putText(image_to_write,f'z: {z} mm',(xcenter+8,ycenter),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
				except Exception as e:
					print(e)
			cv2.circle(image_to_write,(xcenter,ycenter),3,(255,0,0),-1)
			#print(f'The object {detection[0]} has an average position of: {avg_pos_obj} mm')
		return cordinates

	def HasData(self):
		return self._HasData

	def PointsCloudManagerGetResult(self):
		if self._HasData:
			self._HasData = False
			return self.data
		else:
			return None

