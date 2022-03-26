import depthai as dhai
import cv2
import numpy as np

# Help functions

def configure_depth_proprieties(left,right,depth):

    left.setResolution(dhai.MonoCameraProperties.SensorResolution.THE_480_P)
    left.setBoardSocket(dhai.CameraBoardSocket.LEFT)
    right.setResolution(dhai.MonoCameraProperties.SensorResolution.THE_480_P)
    right.setBoardSocket(dhai.CameraBoardSocket.RIGHT)

    # Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
    depth.setDefaultProfilePreset(dhai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    # Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
    depth.initialConfig.setMedianFilter(dhai.MedianFilter.KERNEL_7x7)
    depth.setLeftRightCheck(True)
    depth.setExtendedDisparity(False)
    depth.setSubpixel(False)

    config = depth.initialConfig.get()
    config.postProcessing.speckleFilter.enable = False
    config.postProcessing.speckleFilter.speckleRange = 50
    config.postProcessing.temporalFilter.enable = True
    config.postProcessing.spatialFilter.enable = True
    config.postProcessing.spatialFilter.holeFillingRadius = 2
    config.postProcessing.spatialFilter.numIterations = 1
    config.postProcessing.thresholdFilter.minRange = 400
    config.postProcessing.thresholdFilter.maxRange = 15000
    config.postProcessing.decimationFilter.decimationFactor = 1
    depth.initialConfig.set(config)


class DeviceManager():

    def __init__(self,size,fps):
        self.pipeline = dhai.Pipeline()
        self.size = size
        self.fps = fps
        self._configure_device()
        self.node_list = self.pipeline.getNodeMap()

    def _configure_device(self):
        self._configure_rgb_sensor()
        self._configure_depth_sensor()
 
    def _configure_rgb_sensor(self):

        cam_rgb = self.pipeline.create(dhai.node.ColorCamera)
        cam_rgb.setPreviewSize(self.size)
        cam_rgb.setInterleaved(False)
        cam_rgb.setFps(self.fps)
        xout_rgb = self.pipeline.create(dhai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")
        cam_rgb.preview.link(xout_rgb.input)

    def _configure_depth_sensor(self):
        monoLeft = self.pipeline.create(dhai.node.MonoCamera)
        monoRight = self.pipeline.create(dhai.node.MonoCamera)
        depth = self.pipeline.create(dhai.node.StereoDepth)
        xout_depth = self.pipeline.create(dhai.node.XLinkOut)
        xout_depth.setStreamName("depth")
        configure_depth_proprieties(monoLeft,monoRight,depth)
        monoLeft.out.link(depth.left)
        monoRight.out.link(depth.right)
        depth.disparity.link(xout_depth.input)
            
    def enable_device(self):
        self.device_ = dhai.Device(self.pipeline)
        self.max_disparity = self.node_list[4].initialConfig.getMaxDisparity()
        self._set_output_queue()
    
    def _set_output_queue(self):
        self.q_rgb = self.device_.getOutputQueue("rgb")
        self.q_depth = self.device_.getOutputQueue("depth")

    def poll_for_frames(self):

        frames = {}
        state_frame = False
        frame_count = 0

        while not state_frame:
            rgb_foto = self.q_rgb.tryGet()
            depth_frame = self.q_depth.get()

            if rgb_foto is not None and depth_frame is not None:

                frames['color_image'] = rgb_foto.getCvFrame()
                frames['depth_image'] = depth_frame.getFrame() #*(255 /self.max_disparity)).astype(np.uint8)
                state_frame = True
                return state_frame,frames
            else:
                frame_count += 1
                print('empty_frame: ',frame_count)
                return False,None

if __name__ == '__main__':

    cam = DeviceManager((640,480),25)
    cam.enable_device()
    frame = 0
    while True:
        stato,frames = cam.poll_for_frames()
        if stato:
            cv2.imshow('frame',frames['color_image'])
            cv2.imshow('depth',frames['depth_image'])
            if cv2.waitKey(1) == ord('q'):
                break

