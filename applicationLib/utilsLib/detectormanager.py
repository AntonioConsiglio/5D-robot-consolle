from ..yolor.detect_myself import detect,load_model
from config import opt
import random
import torch
from torch.backends import cudnn
import time

class DetectionManager():

    def __init__(self):
        self.device = None
        self.model = None

    def predict(self,frame):
        with torch.no_grad():
            cudnn.benchmark = True
            start = time.time()
            frame,detections = detect(opt,frame,self.device,self.model,self.names,self.colors)
            print(f"EXECUTION TIME: {(time.time() - start)*1000} ms")
        return frame,detections

    def load_yolor_model(self):
        self.device, self.model = load_model(opt)
        self.model.to(self.device).eval()
        names = opt.names
    # Get names and colors
        self.names = self.load_classes(names)
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

    def postprocess_detection(self,result):
        pass
    
    def load_classes(self,path):
    # Loads *.names file at 'path'
        with open(path, 'r') as f:
            names = f.read().split('\n')
        return list(filter(None, names))  # filter removes empty strings (such as last line)