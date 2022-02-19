'''
This script is made by Antonio Consiglio.
version == 1.0
date: 2022-01-30

Here there are the useful function to run the ROBOT ARM 5D.
'''
import serial
import numpy as np
import tkinter as tk
from threading import Thread
from PIL import Image,ImageTk
import cv2
import time

class SerialConnection():

    def __init__(self,porta,baud_rate):
        self.porta = porta
        self.baud_rate = baud_rate
        self.arduino = None

    def connection(self):
        porta = self.porta.get()
        baudrate = int(self.baud_rate.get())
        self.arduino = serial.Serial(port=porta,baudrate=baudrate,timeout=0.1)
        print('Connesso !')

    def disconnet(self):
        self.arduino.close()
        print('Disconnesso !')

    
class CommandButton():

    def __init__(self,root,**kwargs):
        self.motoNumber = kwargs['number']
        self.frame = self.__create_button_frame(root,kwargs)
        self.menos = self.__button_creator(tipo ='menos',relx=0.25)
        self.plus = self.__button_creator(tipo = 'plus',relx=0.75)
        self.motorLabel = self.__label_creator(relx = 0.5,rely=0.15,relwidth=0.15,relheight=0.7,anchor='n')
        self.name = kwargs['text']
        self.ButtonPlusPress = False
        self.ButtonMenosPress = False
        self.message = None
        self.messagePlus = kwargs['mexPlus']
        self.messageMenos = kwargs['mexMenos']
        

    def __create_button_frame(self,root,kwargs):

        frame = tk.LabelFrame(root,text = kwargs['text'],bg='#a6a6a6',labelanchor='n',font='Helvetic 10 bold')
        frame.place(rely = kwargs['rely'],relx = 0.5,relwidth=0.9,relheight=0.16,anchor='n')
        return frame

    def __button_creator(self,**kwargs):
        img = Image.open(f'images\\{kwargs["tipo"]}.png')
        img = ImageTk.PhotoImage(img)
        button = tk.Button(self.frame,image=img,command = self.__end_command,borderwidth=0,cursor='hand1')
        button.image=img
        button.place(relx=kwargs['relx'],rely=-0.02,anchor='n')
        button.bind('<Button-1>',lambda e: Thread(name = 'Button Pressed',target=self.__continue_command, args=[e,kwargs["tipo"]]).start())
        return button
    
    def __label_creator(self,**kwargs):
        label = tk.Label(self.frame,bg='black',fg='white',text = str(self.motoNumber),font='Helvetic 15 bold',borderwidth=5)
        label.place(kwargs)
        return label


    def __end_command(self):
        self.message = b'0'
        self.ButtonMenosPress = False
        self.ButtonPlusPress = False
        print('END')

    def __continue_command(self,event,button):
        if button == 'menos':
            self.ButtonMenosPress = True
            self.message = self.messageMenos
            print('meno pressed')
        elif button == 'plus':
            self.message = self.messagePlus
            self.ButtonPlusPress = True
            print('plus pressed')

        # while self.ButtonPremuto:
        #     print(self.name)

class CanvasCam(tk.Canvas):

    def __init__(self,master,**kwargs):
        tk.Canvas.__init__(self,master,width=640,height=480,bg='black')
        self.place(kwargs)
    
    def update_image(self,image):
        img = ImageTk.PhotoImage(Image.fromarray(image))
        self.create_image(1,1,image=img,anchor='nw')
        self.image = img


class VideoCapture():
    def __init__(self,canva_to_update,camera_number = 1):
        self.camera = camera_number
        self.canva = canva_to_update
        self.state = True
        self.frames = cv2.VideoCapture(self.camera)
        self._set_frames()
        self.p = Thread(name='video',target=self._start_video,args=())
        self.p.start()

    def _set_frames(self):
        self.frames.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.frames.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.frames.set(cv2.CAP_PROP_FPS, 60)

    def _start_video(self):
        while self.state:
            res,cap = self.frames.read()
            if res:
                cap = cv2.cvtColor(cap,cv2.COLOR_BGR2RGB)
                self.canva.update_image(cap)
            else:
                pass
            #time.sleep(0.005)


class FrameDown(tk.Frame):

    def __init__(self,master,**kwargs):
        tk.Frame.__init__(self,master,kwargs)
        self.subframe_sx = tk.LabelFrame(self,text='da_capire_cosa_devo_farci',labelanchor='n',bg='red')
        self.subframe_dx = tk.Frame(self,bg='green')
        self._place_subframe()
        self._split_subframe_dx()

    def _place_subframe(self):
        self.subframe_dx.place(relx=0.75,rely=0,relwidth=0.5,relheight=1,anchor='n')
        self.subframe_sx.place(relx=0.25,rely=0,relwidth=0.5,relheight=1,anchor='n')

    def _split_subframe_dx(self):
        self.inverse_frame = tk.LabelFrame(self.subframe_dx,text='INVERSE KINEMATICS',
                                            labelanchor='n',bg='lightgray',font='Helvetic 10 bold')
        self.forward_frame = tk.LabelFrame(self.subframe_dx,text='FORWARD KINEMATICS',
                                            labelanchor='n',bg='lightgray',font='Helvetic 10 bold')
        self.inverse_frame.place(relx=0.25,rely=0,relwidth=0.5,relheight=1,anchor='n')
        self.forward_frame.place(relx=0.75,rely=0,relwidth=0.5,relheight=1,anchor='n')


class SerialInterface(tk.LabelFrame):

    def __init__(self,frameSX,porta,list_seria_port,baud_rate,set_connection,update_port_available):
        tk.LabelFrame.__init__(self,frameSX,labelanchor='n',text='SET SERIAL CONNECTION',bg='black',fg='white')
        self.baud_list = ["9600","38400"]
        if len(list_seria_port) == 0:
            self.list_seria_port = [None]
        else:
            self.list_seria_port=list_seria_port
        self._create_frame_items(porta,baud_rate,set_connection,update_port_available)
        self.place(relx=0.5,rely=0.83,relheight=0.17,relwidth=1,anchor='n')

    def _create_frame_items(self,porta,baud_rate,set_connection,update_port_available):
        self.set_porta = tk.OptionMenu(self,porta,*self.list_seria_port)
        self.set_baud_rate = tk.OptionMenu(self,baud_rate,*self.baud_list)
        self.connection_button = tk.Button(self,text='CONNECT',command=lambda: set_connection(self.connection_button),
                                        bg='green',font='Helvetic 10 bold',cursor='hand1')
        self.refresh_button = tk.Button(self,text='refresh port',command=lambda: update_port_available(self.set_porta),
                                    bg='lightblue',font='Helvetic 8 bold',cursor='hand1')
        self.serial_port_label = tk.Label(self,text='SERIAL PORT',bg = 'black',fg='white',borderwidth=0)
        self.baud_rate_label = tk.Label(self,text='BAUD RATE',bg = 'black',fg='white',borderwidth=0)
        self.serial_port_label.place(relx=0.2,rely=0.05,anchor='n')
        self.baud_rate_label.place(relx=0.5,rely=0.05,anchor='n')
        self.set_porta.place(relx=0.2,rely=0.35,anchor='n')
        self.set_baud_rate.place(relx=0.5,rely=0.35,anchor='n')
        self.connection_button.place(relx=0.8,rely=0.50,relwidth=0.3,anchor='n')
        self.refresh_button.place(relx=0.8,rely=0.05,anchor='n')
        
