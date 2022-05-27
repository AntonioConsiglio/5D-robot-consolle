from .pointclouds_function_utils import *
import PyQt5
from PyQt5.QtCore import QThread,pyqtSignal,QObject,pyqtProperty,Qt

class PointsCloudManager:
	def __init__(self,id):

		self.parameters = None
		self.sende = None
		self.receiver = None
		self.stopq = None
		self.viewROI = None
		self.id = id
		self._HasData = False
		self.pars = None

	def SetParameters(self, calibration_info,roi_2D,viewROI):
		self.pars = CalculatePointsCloudParameters(calibration_info, roi_2D, viewROI)


	def PointsCloudManagerStartCalculation(self,depth_image,color_image,APPLY_ROI,
											Kdecimation,ZmmConversion,
											depth_threshold,viewROI):

		if self.pars is not None:
			pc_start = PointCloudCalculation(depth_image,
											 color_image,
											 self.pars,
											 [],
											 self.id,
											 APPLY_ROI,
											 Kdecimation,
											 ZmmConversion,
											 depth_threshold,
											 viewROI)

			pc_start.ready_result.connect(self._hasresult)
			pc_start.start()
			

	def _hasresult(self,results):

		self.data = results
		self._HasData = True


	def HasData(self):
		return self._HasData

	def PointsCloudManagerGetResult(self):
		if self._HasData:
			self._HasData = False
			return self.data
		else:
			return None

class PointCloudCalculation(QThread):

	ready_result = pyqtSignal(dict)
	def __init__(self,depth_image,color_image,pars,addinfo,
					id,apply_roi,Kdecimation,ZmmConversion,
					depth_threshold,viewROI):
		super(PointCloudCalculation,self).__init__()
		self.depth_image = depth_image
		self.color_image = color_image
		self.pars = pars
		self.addinfo = addinfo
		self.id = id
		self.apply_roi = apply_roi
		self.Kdecimation = Kdecimation
		self.ZmmConversion = ZmmConversion
		self.depth_threshold = depth_threshold
		self.viewROI = viewROI

	def run(self):

		result = CalculatePointsCloud(self.depth_image,
									  self.color_image,
									  self.pars,
									  self.addinfo,
									  self.id,
									  self.apply_roi,
									  self.Kdecimation,
									  self.ZmmConversion,
									  self.depth_threshold,
									  self.viewROI)
		if result:
			self.ready_result.emit(result)
	
			
