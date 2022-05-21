import os
from shutil import copyfile
import json

import cv2
import numpy as np

from .calibration_kabsch import PoseEstimation, Transformation



def docalibration(device_manager,intrinsics_devices,extriniscs_device, chessboard_params, calibration_roi, shiftcalibration, path = "./"):
	'''
	#This function is used to calibrate one or more cameras in 3D space.\n
	input:\n
	- device_manager : class to manage cameras\n
	- intrisics_devices: intrinsic camera's parameters\n
	- chessboard_params: [n_corners_along_h, n_corners_along_w, square_size]\n
	- calibration_roi: Region of interest\n
	- shiftcalibration: a vector if there is a shift of the calibration\n
	- path: the path where the .json file with calibration parameters (trasportation matrix) is stored\n
	'''
	# Set the chessboard parameters for calibration 
	# Estimate the pose of the chessboard in the world coordinate using the Kabsch Method
	try:
		calibrated_device_count = 0

		while calibrated_device_count < 1: #len(device_manager._available_devices)
			frames = device_manager.poll_for_frames()
			pose_estimator = PoseEstimation(frames, intrinsics_devices,extriniscs_device, chessboard_params)
			transformation_result_kabsch, corners3D,immagine = pose_estimator.perform_pose_estimation()
			#object_point, _ = pose_estimator.get_chessboard_corners_in3d()
			calibrated_device_count = 0

			if not transformation_result_kabsch[0]:
				print("Place the chessboard on the plane where the object needs to be detected..")
			else:
				calibrated_device_count += 1

			# color_frame = frames['color_image']

			# box_info =  "SELF CALIBRATION ONGOING.."
			# cv2.putText(color_frame, box_info, (20,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,255) )

		# Save the transformation object for all devices in an array to use for measurements

		chessboard_points_cumulative_3d = np.array([-1,-1,-1]).transpose()



		transformation_device= transformation_result_kabsch[1].inverse()
		t = Transformation(translation_vector = -np.array(shiftcalibration))
		mf = np.dot(t.get_matrix(),transformation_device.get_matrix())
		transformation_device.set_matrix(mf)

		# points3D = object_point[2][:,object_point[3]]
		# points3D = transformation_device.apply_transformation(points3D)
		# chessboard_points_cumulative_3d = np.column_stack( (chessboard_points_cumulative_3d,points3D) )

		# Extract the bounds between which the object's dimensions are needed
		# It is necessary for this demo that the object's length and breath is smaller than that of the chessboard
		#chessboard_points_cumulative_3d = np.delete(chessboard_points_cumulative_3d, 0, 1)
		roi_2D = calibration_roi # get_boundary_corners_2D(chessboard_points_cumulative_3d)

		save_calibration_json(transformation_device, roi_2D, path)

		return corners3D
	except Exception as e:
		print(e)

def check_calibration_exist(available_devices, path = "./"):

	if not os.path.isfile(get_roi_2D_name(path)):
		return False

	for device in available_devices:
		if not os.path.isfile(get_calibration_name(path,device)):
			modelfile_path = os.path.join(path,'calibration_model.json')
			copyfile(modelfile_path,get_calibration_name(path,device))
			#return False
	return True

def load_calibration_json(device_manager, path = "./"):

	transformation_devices = {}
	for device in device_manager._available_devices:
		with open(device + '_calibration.json') as json_file:
			pose_mat = np.array(json.load(json_file))
			transformation_devices[device] = Transformation(pose_mat[:3,:3],pose_mat[:3,3])

	with open('roi_2D.json') as json_file:
		roi_2D = json.load(json_file)

	return transformation_devices, roi_2D

def get_calibration_name(path):
	return os.path.join(path,'camera_calibration.json')

def get_roi_2D_name(path):
	return os.path.join(path, 'roi_2D.json')

def save_calibration_json(transformation_devices, roi_2D, path = "./"):
	
	transformation_device = transformation_devices
	mat = transformation_device.get_matrix()
	with open(get_calibration_name(path), 'w') as outfile:
		json.dump(mat.tolist(), outfile)
	with open(get_roi_2D_name(path), 'w') as outfile:
		json.dump(roi_2D, outfile)

