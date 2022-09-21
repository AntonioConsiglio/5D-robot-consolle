import serial.tools.list_ports as p
import math
import time
import cv2

def enumerate_serial_ports():
    """  return a iterator of serial (COM) ports existing on this computer.
    """
    port = p.comports()
    ports = [i.device for i in port]
    return ports

def update_com_port(cls):
    ports =  enumerate_serial_ports()
    if ports is not None:
        # ports.insert(0,'None')
        cls.com_port.clear()
        cls.com_port.addItems(ports)
        return True
    else:
        return True

def robot_to_python_angles(angles_list):
    angle_list = [0.0]
    angle_list1 = [math.radians(int(i)-90) for i in angles_list]
    angles_list = angle_list+angle_list1
    return angles_list

def python_to_robot_angles(angles_list):
    angles_list = [math.degrees(i) for i in angles_list]
    angles_list = [int(i+90) for i in angles_list]
    return angles_list

def write_fps(toc,frames):
    tic =time.time()
    fps = 1//(tic-toc)
    cv2.putText(frames['color_image'],f"FPS: {fps}",(20,30),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,0),2)
    return frames
