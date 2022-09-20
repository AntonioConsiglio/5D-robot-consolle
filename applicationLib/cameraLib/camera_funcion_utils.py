import depthai as dhai
import cv2
import numpy as np
try:
	from .pointclouds_utils.pointclouds_manager import PointsCloudManager
	from .calibrationLib.calibration_function import load_calibration_json,check_calibration_exist
	from .calibrationLib.calibration_kabsch import Transformation
except:
	print('PointsCloudManager not loaded within calibration functions')

############################ RGB SENSOR CONFIGURATION FUNCTIONS ############################

def configure_rgb_sensor(pipeline,size,fps,nn_active,blob_path,calibration):

		cam_rgb = pipeline.create(dhai.node.ColorCamera)
		cam_rgb.setResolution(dhai.ColorCameraProperties.SensorResolution.THE_1080_P)
		if calibration.value == 1:
			pass
			#cam_rgb.initialControl.setManualFocus(130)
		cam_rgb.setPreviewSize(size)
		cam_rgb.setBoardSocket(dhai.CameraBoardSocket.RGB)
		cam_rgb.setInterleaved(False)
		cam_rgb.setFps(fps)
		xout_rgb = pipeline.create(dhai.node.XLinkOut)
		xout_rgb.setStreamName("rgb")
		cam_rgb.preview.link(xout_rgb.input)
		if nn_active.value == 2:
			manip,_= configure_image_manipulator(pipeline)
			cam_rgb.preview.link(manip.inputImage)
			configure_nn_node(manip,pipeline,blob_path)
		return xout_rgb

def configure_image_manipulator(pipeline):

    manip = pipeline.create(dhai.node.ImageManip)
    manipOut = pipeline.create(dhai.node.XLinkOut)
    manipOut.setStreamName('neural_input')
    manip.initialConfig.setResize(300,300)
    manip.initialConfig.setFrameType(dhai.ImgFrame.Type.BGR888p)
    manip.out.link(manipOut.input)
    
    return manip,manipOut

def configure_nn_node(manip,pipeline,blob_path):
		
		nn = pipeline.create(dhai.node.MobileNetDetectionNetwork)
		nnOut = pipeline.create(dhai.node.XLinkOut)
		nnOut.setStreamName("neural")
		# define nn features
		nn.setConfidenceThreshold(0.4)
		nn.setBlobPath(blob_path)
		nn.setNumInferenceThreads(2)
		# Linking
		manip.out.link(nn.input)
		nn.out.link(nnOut.input)

############################ DEPTH CONFIGURATION FUNCTIONS ############################

def configure_depth_sensor(pipeline,calibration):

    monoLeft = pipeline.create(dhai.node.MonoCamera)
    monoRight = pipeline.create(dhai.node.MonoCamera)
    depth = pipeline.create(dhai.node.StereoDepth)
    xout_depth = pipeline.create(dhai.node.XLinkOut)
    xout_depth.setStreamName("depth")
    xout_disparity = pipeline.create(dhai.node.XLinkOut)
    xout_disparity.setStreamName("disparity")
    configure_depth_proprieties(monoLeft,monoRight,depth,calibration)
    if calibration.value == 1:
        depth.setDepthAlign(dhai.CameraBoardSocket.RGB)
    monoLeft.out.link(depth.left)
    monoRight.out.link(depth.right)
    depth.disparity.link(xout_disparity.input)
    depth.depth.link(xout_depth.input)

def configure_depth_proprieties(left,right,depth,calibration):
	if not calibration.value == 1:
		left.setResolution(dhai.MonoCameraProperties.SensorResolution.THE_480_P)
		left.setBoardSocket(dhai.CameraBoardSocket.LEFT)
		right.setResolution(dhai.MonoCameraProperties.SensorResolution.THE_480_P)
		right.setBoardSocket(dhai.CameraBoardSocket.RIGHT)
	else:
		left.setResolution(dhai.MonoCameraProperties.SensorResolution.THE_480_P)
		left.setBoardSocket(dhai.CameraBoardSocket.LEFT)
		right.setResolution(dhai.MonoCameraProperties.SensorResolution.THE_480_P)
		right.setBoardSocket(dhai.CameraBoardSocket.RIGHT)


	# Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
	depth.setDefaultProfilePreset(dhai.node.StereoDepth.PresetMode.HIGH_DENSITY)
	# Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
	depth.initialConfig.setMedianFilter(dhai.MedianFilter.KERNEL_5x5)
	depth.setLeftRightCheck(True)
	depth.setExtendedDisparity(True)
	depth.setSubpixel(False)

	config = depth.initialConfig.get()
	config.postProcessing.speckleFilter.enable = False
	config.postProcessing.speckleFilter.speckleRange = 50
	config.postProcessing.temporalFilter.enable = True
	config.postProcessing.spatialFilter.enable = True
	config.postProcessing.spatialFilter.holeFillingRadius = 2
	config.postProcessing.spatialFilter.numIterations = 1
	config.postProcessing.thresholdFilter.minRange = 300
	config.postProcessing.thresholdFilter.maxRange = 650
	config.postProcessing.decimationFilter.decimationFactor = 1
	depth.initialConfig.set(config)

	############################ POINTCLOUD MANAGER FUNCTIONS ############################

def create_pointcloud_manager(id,calibrationInfo):

	pointcloud_manager = PointsCloudManager(id)
	check_calibration_exist()
	calibration_info,roi_2D,viewROI = load_calibration_json()
	pointcloud_manager.viewROI = viewROI
	calibrationInfo.append(calibration_info)
	pointcloud_manager.SetParameters(calibrationInfo,roi_2D,viewROI)

	return pointcloud_manager


	## IMAGE PLOTTING

def visualise_Axes(color_image, calibration_info_devices, len_axes = 0.10):

		
	bounding_box_points_devices = create_axis_draw_points(calibration_info_devices, len_axes)

	points = bounding_box_points_devices.astype(int)
	origin = points[0]

	xend = points[1]
	x_color = (255,0,0)
	cv2.line(color_image, (origin[0],origin[1]), (xend[0],xend[1]), x_color, 2)
	cv2.putText(color_image, "X", (xend[0],xend[1]), cv2.FONT_HERSHEY_PLAIN, 2, x_color )

	yend = points[3]
	y_color = (0,255,0)
	cv2.line(color_image, (origin[0],origin[1]), (yend[0],yend[1]), y_color, 2)
	cv2.putText(color_image, "Y", (yend[0],yend[1]), cv2.FONT_HERSHEY_PLAIN, 2, y_color )

	zend = points[5]
	z_color = (0,0,255)
	cv2.line(color_image, (origin[0],origin[1]), (zend[0],zend[1]), z_color, 2)
	cv2.putText(color_image, "Z", (zend[0],zend[1]), cv2.FONT_HERSHEY_PLAIN, 2, z_color )

	return color_image

def create_draw_points(bounding_box_world_3d, calibration_info_devices):

# Get the bounding box points in the image coordinates
	bounding_box_points_color_image = Convert3Dto2DImage(calibration_info_devices,bounding_box_world_3d.T)

	return bounding_box_points_color_image


def make_axis_points(len_axes = 0.02):
	x = [0, len_axes, 0, 0, 0, 0]
	y = [0, 0, 0, len_axes, 0, 0]
	z = [0, 0, 0, 0, 0, len_axes]
	return np.stack([x, y, z],1)


def create_axis_draw_points(calibration_info_devices, len_axes = 0.02):
	bounding_box_world_3d = make_axis_points(len_axes)
	return create_draw_points(bounding_box_world_3d, calibration_info_devices)

def Convert3Dto2DImage(calibration_info,bounding_box_world_3d):

	T0 = calibration_info[3] #Transformation(trasformation_mat = calibration_info[3])
	color_intrinsics = calibration_info[0]
	T2 = calibration_info[2] #Transformation(trasformation_mat = calibration_info[2])

	bounding_box_device_3d = T0.inverse().apply_transformation(bounding_box_world_3d)
	bounding_box_device_3d_RGB = T2.apply_transformation(np.array(bounding_box_device_3d))

	z_RGB = bounding_box_device_3d_RGB[2,:]
	x_RGB = np.divide(bounding_box_device_3d_RGB[0,:],z_RGB)
	y_RGB = np.divide(bounding_box_device_3d_RGB[1,:],z_RGB)

	u = (x_RGB * color_intrinsics.fx + color_intrinsics.cx).astype(int) # (x_RGB * color_intrinsics.fx + color_intrinsics.ppx + 0.5).astype(np.int)
	v = (y_RGB * color_intrinsics.fy + color_intrinsics.cy).astype(int)  #	v = (y_RGB * color_intrinsics.fy + color_intrinsics.ppy + 0.5).astype(np.int)
	
	return np.stack([u,v],0).astype(int).T