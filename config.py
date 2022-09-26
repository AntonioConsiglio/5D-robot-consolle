import os
class dotdict(dict):
	"""dot.notation access to dictionary attributes"""
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

HOME_PATH = os.getcwd()
opt = {}
opt['weights'] = "./applicationLib\\yolor\\best_223.pt"
opt["cfg"] = "./applicationLib\\yolor\\cfg\\yolor_p6.cfg"
opt["data"] = "./applicationLib\\yolor\\data.yaml"
opt['imgsz'] = 1280
opt['names'] = './applicationLib\\yolor\\data.names'
opt['conf_thres'] = 0.4
opt['iou_thres'] = 0.5
opt["device"] = '0'
opt["agnostic_nms'"] = False
opt['update'] = False
opt['half'] = True
opt = dotdict(opt)
