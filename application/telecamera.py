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

    def __init__(self,size,fps,nn_mode):
        self.pipeline = dhai.Pipeline()
        self.size = size
        self.fps = fps
        self.nn_active = nn_mode
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
        if self.nn_active:
            manip,_= self._configure_image_manipulator()
            cam_rgb.preview.link(manip.inputImage)
            self._configure_nn_node(manip)
        return xout_rgb

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
    
    def _configure_image_manipulator(self):
        manip = self.pipeline.create(dhai.node.ImageManip)
        manipOut = self.pipeline.create(dhai.node.XLinkOut)
        manipOut.setStreamName('neural_input')
        manip.initialConfig.setResize(300,300)
        manip.initialConfig.setFrameType(dhai.ImgFrame.Type.BGR888p)
        manip.out.link(manipOut.input)

        return manip,manipOut

    def _configure_nn_node(self,manip):
        
        nn = self.pipeline.create(dhai.node.MobileNetDetectionNetwork)
        nnOut = self.pipeline.create(dhai.node.XLinkOut)
        nnOut.setStreamName("neural")
        # define nn features
        nn.setConfidenceThreshold(0.5)
        nn.setBlobPath("C:\\Users\\anton\\Desktop\\5D-robot-consolle\\neuralNetwork\\mobilenet-ssd_openvino_2021.2_6shave.blob")
        nn.setNumInferenceThreads(2)
        # Linking
        manip.out.link(nn.input)
        nn.out.link(nnOut.input)
         
    def enable_device(self):
        self.device_ = dhai.Device(self.pipeline,usb2Mode=True)
        if self.nn_active:
            self.max_disparity = self.node_list[8].initialConfig.getMaxDisparity()
        else:
            self.max_disparity = self.node_list[4].initialConfig.getMaxDisparity()
        self._set_output_queue()
    
    def _set_output_queue(self):
        self.q_rgb = self.device_.getOutputQueue("rgb",maxSize = 1,blocking = False)
        self.q_depth = self.device_.getOutputQueue("depth",maxSize = 1,blocking = False)
        if self.nn_active:
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
            cv2.putText(image,f'{label}: {round(score*100,2)} %',(xmin,ymin-10),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)

    def poll_for_frames(self):

        frames = {}
        state_frame = False
        frame_count = 0

        while not state_frame:
            rgb_foto = self.q_rgb.tryGet()
            depth_frame = self.q_depth.get()
            if self.nn_active:
                nn_foto = self.q_nn_input.tryGet()
                nn_detection = self.q_nn.tryGet()
                if nn_detection is not None:
                    detections = nn_detection.detections
                else:
                    detections = None

            if rgb_foto is not None and depth_frame is not None:

                frames['color_image'] = rgb_foto.getCvFrame()
                frames['depth_image'] = depth_frame.getFrame() #*(255 /self.max_disparity)).astype(np.uint8)
                if nn_foto is not None:
                    frames['nn_input'] = nn_foto.getCvFrame()
                    if detections is not None:
                        detections = self._normalize_detections(detections)
                        self._write_detections_on_image(frames['color_image'],detections)
                state_frame = True
                return state_frame,frames,detections
            else:
                frame_count += 1
                print('empty_frame: ',frame_count)
                return False,None,None

if __name__ == '__main__':

    cam = DeviceManager((640,480),30,nn_mode=True)
    cam.enable_device()
    frame = 0
    while True:
        stato,frames,detections = cam.poll_for_frames()
        if stato:
            cv2.imshow('frame',frames['color_image'])
            cv2.imshow('depth',frames['depth_image'])
            if 'nn_input' in frames:
                cv2.imshow('nn_image',frames['nn_input'])
                print(detections)
            if cv2.waitKey(1) == ord('q'):
                break

