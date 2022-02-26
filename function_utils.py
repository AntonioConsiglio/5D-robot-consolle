'''
This script is made by Antonio Consiglio.
version == 1.0
date: 2022-01-30

Here there are the useful function to run the ROBOT ARM 5D.
'''
from turtle import hideturtle
import serial
import numpy as np
import tkinter as tk
from threading import Thread
from PIL import Image,ImageTk
import cv2
import time
import math

class SerialConnection():

    def __init__(self,porta,baud_rate):
        self.porta = porta
        self.baud_rate = baud_rate
        self.arduino = None

    def connection(self):
        porta = self.porta.get()
        baudrate = int(self.baud_rate.get())
        self.arduino = serial.Serial(port=porta,baudrate=baudrate,timeout=0.01)
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
            if self.camera == 1:
                image = np.zeros((480,640))
                cv2.putText(image,'No Cam Available...',(150,230),cv2.FONT_ITALIC,1,(255,255,255),2)
                self.canva.update_image(image)
                self.state=False
            else:
                res,cap = self.frames.read()
                if res:
                    cap = cv2.cvtColor(cap,cv2.COLOR_BGR2RGB)
                    self.canva.update_image(cap)
                else:
                    pass
                #time.sleep(0.005)


class FrameDown(tk.Frame):

    def __init__(self,master,arduino_obj,robot_obj,**kwargs):
        tk.Frame.__init__(self,master,kwargs)
        self.subframe_sx = tk.LabelFrame(self,text='CONTROL INFO',labelanchor='n',bg='lightgreen')
        self.subframe_dx = tk.Frame(self,bg='green')
        self.arduino_obj = arduino_obj
        self.robot_obj = robot_obj
        self._place_subframe()
        self._split_subframe_dx()
        self._split_subframe_sx()
        self._create_angle_variable()
        self._create_angle_view_variable()
        self._angles_info_labeles()
        self._create_xyz_variable()
        self._create_xyz_variable_info()
        self._xyz_info_labeles()
        self._create_forward_frame()
        self._create_inverse_frame()

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

    def _split_subframe_sx(self):
        self.position_frame = tk.LabelFrame(self.subframe_sx,text="POSITION INFO",labelanchor='n',font='Helvetic 10 bold')
        self.position_frame_angle = tk.LabelFrame(self.position_frame,text="joints' angle",labelanchor='n',font='Helvetic 10 bold')
        self.position_frame_xyz = tk.LabelFrame(self.position_frame,text="xyz position",labelanchor='n',font='Helvetic 10 bold')
        self.position_frame_angle.place(relx=0.5,rely=0,relwidth=1,relheight=0.66,anchor='n')
        self.position_frame_xyz.place(relx=0.5,rely=0.67,relwidth=1,relheight=0.33,anchor='n')
        self.position_frame.place(relx=0.66,rely=0,relwidth=0.33,relheight=1,anchor='nw')
    
    def _create_angle_variable(self):

        self.angle1 = tk.StringVar()
        self.angle2 = tk.StringVar()
        self.angle3 = tk.StringVar()
        self.angle4 = tk.StringVar()
        self.angle5 = tk.StringVar()
        self.angle6 = tk.StringVar()
    
    def _create_angle_view_variable(self):

        self.angle1_info = tk.StringVar()
        self.angle2_info = tk.StringVar()
        self.angle3_info = tk.StringVar()
        self.angle4_info = tk.StringVar()
        self.angle5_info = tk.StringVar()
        self.angle6_info = tk.StringVar()
        self._set_angle_variable()
        
    def _set_angle_variable(self,angoli=None,first=True):

        if first:      
            self.angle1_info.set('160')
            self.angle2_info.set('0')
            self.angle3_info.set('90')
            self.angle4_info.set('180')
            self.angle5_info.set('110')
            self.angle6_info.set('90')
        elif not first and angoli is not None:
            angles_info = [self.angle6_info,self.angle5_info,self.angle4_info,
                            self.angle3_info,self.angle2_info]
            for index, i in enumerate(angoli):
                angles_info[index].set(i)
        
    def _create_xyz_variable(self):
        
        self.x = tk.StringVar()
        self.y = tk.StringVar()
        self.z = tk.StringVar()
    
    def _create_xyz_variable_info(self):
        
        self.x_info = tk.StringVar()
        self.y_info = tk.StringVar()
        self.z_info = tk.StringVar()
        self._set_xyz_variable()

    def _set_xyz_variable(self,xyz = None,first=True):
        
        if first:
            angles_list = [self.angle6_info.get(),self.angle5_info.get(),self.angle4_info.get(),self.angle3_info.get(),self.angle2_info.get()]
            angles_int_list = [math.radians(int(i)-90) for i in angles_list]
            angles_int_list.insert(0,0)
            angles_int_list.append(0)
            t_matrix = self.robot_obj.forward_kinematics(angles_int_list)
            position = np.round(t_matrix[:3,3],2)

            self.x_info.set(str(position[0]).split('.')[0])
            self.y_info.set(str(position[1]).split('.')[0])
            self.z_info.set(str(position[2]).split('.')[0])

        elif not first and xyz is not None:

            self.x_info.set(str(xyz[0]).split('.')[0])
            self.y_info.set(str(xyz[1]).split('.')[0])
            self.z_info.set(str(xyz[2]).split('.')[0])
    
    def _create_label_variable(self):
        start,offset,x,x2 = 0.05,0.13,0.25,0.8
        for i in range(6):
            label = tk.Label(self.forward_frame,text=f'angle joint {i+1}: '.upper(),font='Helvetic 10 bold',bg='lightgray')
            label.place(relx=x,rely=start+offset*i,anchor='n')
            limitlabel = tk.Label(self.forward_frame,text='(0 ÷ 180)',font='Helvetic 10 bold',bg='lightgray')
            limitlabel.place(relx=x2,rely=start+offset*i,anchor='n')

    def _create_forward_frame(self):

        self._create_label_variable()
        self.entry_angle6 = tk.Entry(self.forward_frame,textvariable=self.angle6,font='Helvetic 10 bold',justify='right')
        self.entry_angle5 = tk.Entry(self.forward_frame,textvariable=self.angle5,font='Helvetic 10 bold',justify='right')
        self.entry_angle4 = tk.Entry(self.forward_frame,textvariable=self.angle4,font='Helvetic 10 bold',justify='right')
        self.entry_angle3 = tk.Entry(self.forward_frame,textvariable=self.angle3,font='Helvetic 10 bold',justify='right')
        self.entry_angle2 = tk.Entry(self.forward_frame,textvariable=self.angle2,font='Helvetic 10 bold',justify='right')
        self.entry_angle1 = tk.Entry(self.forward_frame,textvariable=self.angle1,font='Helvetic 10 bold',justify='right')
        start,offset,x = 0.05,0.13,0.55
        self.entry_angle1.place(relx = x,rely=start,anchor='n',relwidth=0.2)
        self.entry_angle2.place(relx = x,rely=start+offset,anchor='n',relwidth=0.2)
        self.entry_angle3.place(relx = x,rely=start+offset*2,anchor='n',relwidth=0.2)
        self.entry_angle4.place(relx = x,rely=start+offset*3,anchor='n',relwidth=0.2)
        self.entry_angle5.place(relx = x,rely=start+offset*4,anchor='n',relwidth=0.2)
        self.entry_angle6.place(relx = x,rely=start+offset*5,anchor='n',relwidth=0.2)

        self.send_angle = tk.Button(self.forward_frame,bg = 'lightblue',text='START',font='Helvetic 13 bold',
                                    command=self._send_angles)
        self.send_angle.place(relx = 0.5,rely = 0.83,anchor='n')

    def _create_label_for_inverse(self):
        start,offset,x,x2 = 0.13,0.13,0.2,0.7

        label_X = tk.Label(self.inverse_frame,text=f'X: '.upper(),font='Helvetic 13 bold',bg='lightgray')
        label_X.place(relx=x,rely=start+offset*0,anchor='n')
        limitlabel_X = tk.Label(self.inverse_frame,text='(0 ÷ 250 mm)',font='Helvetic 13 bold',bg='lightgray')
        limitlabel_X.place(relx=x2,rely=start+offset*0,anchor='n')
        
        label_Y = tk.Label(self.inverse_frame,text=f'Y: '.upper(),font='Helvetic 13 bold',bg='lightgray')
        label_Y.place(relx=x,rely=start+offset*2,anchor='n')
        limitlabel_Y = tk.Label(self.inverse_frame,text='(0 ÷ 250 mm)',font='Helvetic 13 bold',bg='lightgray')
        limitlabel_Y.place(relx=x2,rely=start+offset*2,anchor='n')

        label_Z = tk.Label(self.inverse_frame,text=f'Z: '.upper(),font='Helvetic 13 bold',bg='lightgray')
        label_Z.place(relx=x,rely=start+offset*4,anchor='n')
        limitlabel_Z = tk.Label(self.inverse_frame,text='(0 ÷ 410 mm)',font='Helvetic 13 bold',bg='lightgray')
        limitlabel_Z.place(relx=x2,rely=start+offset*4,anchor='n')

    def _create_inverse_frame(self):

        self._create_label_for_inverse()
        self.X_entry = tk.Entry(self.inverse_frame,textvariable=self.x,font='Helvetic 13 bold',justify='right')
        self.Y_entry = tk.Entry(self.inverse_frame,textvariable=self.y,font='Helvetic 13 bold',justify='right')
        self.Z_entry = tk.Entry(self.inverse_frame,textvariable=self.z,font='Helvetic 13 bold',justify='right')
        start,offset,x = 0.13,0.13,0.4
        self.X_entry.place(relx = x,rely=start,anchor='n',relwidth=0.2)
        self.Y_entry.place(relx = x,rely=start+offset*2,anchor='n',relwidth=0.2)
        self.Z_entry.place(relx = x,rely=start+offset*4,anchor='n',relwidth=0.2)

        self.send_xyz = tk.Button(self.inverse_frame,bg = 'lightblue',text='START',font='Helvetic 13 bold',
                                    command=self._inverse_kinematics)
        self.send_xyz.place(relx = 0.5,rely = 0.83,anchor='n')

    def _inverse_kinematics(self):
        
        target = [self.x,self.y,self.z]
        target = [float(i.get().strip()) for i in target]
        self._set_xyz_variable(xyz=target,first=False)
        _,self.angle6,self.angle5,self.angle4,self.angle3,self.angle2,_ = self.robot_obj.compute_inverse_kinematics(target)
        self._send_angles(inverse_kinematics=True)

    def _send_angles(self,inverse_kinematics = False):
        
        angles_list = [self.angle6,self.angle5,self.angle4,self.angle3,self.angle2]
        if inverse_kinematics:
            angles_list = [math.degrees(i) for i in angles_list]
            angles_list = [int(i+90) for i in angles_list]
            angles_list = [str(i) for i in angles_list]
            self.angle6,self.angle5,self.angle4,self.angle3,self.angle2 = angles_list
            self._set_angle_variable(angoli=angles_list,first=False)
        else:
            angles_list = [i.get().strip() for i in angles_list]
            self._set_angle_variable(angoli=angles_list,first=False)
            angles_int_list = [math.radians(int(i)-90) for i in angles_list]
            
        self.arduino_obj.arduino.write(b'17')
        time.sleep(0.1)
        for i in angles_list:
            self.arduino_obj.arduino.write(i.encode('UTF-8'))
            print(i.encode('UTF-8'))
            time.sleep(0.1)
        if not inverse_kinematics:    
            angles_int_list.insert(0,0)
            angles_int_list.append(0)
            t_matrix = self.robot_obj.forward_kinematics(angles_int_list)
            position = np.round(t_matrix[:3,3],0)
            self._set_xyz_variable(xyz = position,first=False)
            print(f'x: {position[0]} mm y: {position[1]} mm z: {position[2]} mm')

    # INFO PART

    def _angles_info_labeles(self):

        start,offset,x,w,color = 0.05,0.15,0.67,0.2,'white'
        self.info_angle_1=tk.Label(self.position_frame_angle,bg= color,textvariable=self.angle1_info)
        self.info_angle_1.place(relx=x,rely=start+offset*0,relwidth=w,relheight=0.13,anchor='n')
        self.info_angle_2=tk.Label(self.position_frame_angle,bg=color,textvariable=self.angle2_info)
        self.info_angle_2.place(relx=x,rely=start+offset*1,relwidth=w,relheight=0.13,anchor='n')
        self.info_angle_3=tk.Label(self.position_frame_angle,bg=color,textvariable=self.angle3_info)
        self.info_angle_3.place(relx=x,rely=start+offset*2,relwidth=w,relheight=0.13,anchor='n')
        self.info_angle_4=tk.Label(self.position_frame_angle,bg=color,textvariable=self.angle4_info)
        self.info_angle_4.place(relx=x,rely=start+offset*3,relwidth=w,relheight=0.13,anchor='n')
        self.info_angle_5=tk.Label(self.position_frame_angle,bg=color,textvariable=self.angle5_info)
        self.info_angle_5.place(relx=x,rely=start+offset*4,relwidth=w,relheight=0.13,anchor='n')
        self.info_angle_6=tk.Label(self.position_frame_angle,bg=color,textvariable=self.angle6_info)
        self.info_angle_6.place(relx=x,rely=start+offset*5,relwidth=w,relheight=0.13,anchor='n')
        self._create_angles_label_info()

    def _create_angles_label_info(self):
        start,offset,x,x2 = 0.05,0.15,0.35,0.8
        for i in range(6):
            label = tk.Label(self.position_frame_angle,text=f'angle joint {i+1}: '.upper(),font='Helvetic 7 bold',bg='lightgray')
            label.place(relx=x,rely=start+offset*i,anchor='n')
            limitlabel = tk.Label(self.position_frame_angle,text='°',font='Helvetic 7 bold',bg='lightgray')
            limitlabel.place(relx=x2,rely=start+offset*i,anchor='nw')

    def _xyz_info_labeles(self):
        y,w,color = 0.35,0.13,'white'
        self.info_x=tk.Label(self.position_frame_xyz,bg= color,textvariable=self.x_info,font='Helvetic 8 bold')
        self.info_x.place(rely=y,relx=0.19,relwidth=w,anchor='n')
        self.info_y=tk.Label(self.position_frame_xyz,bg=color,textvariable=self.y_info,font='Helvetic 8 bold')
        self.info_y.place(rely=y,relx=0.49,relwidth=w,anchor='n')
        self.info_z=tk.Label(self.position_frame_xyz,bg=color,textvariable=self.z_info,font='Helvetic 8 bold')
        self.info_z.place(rely=y,relx=0.79,relwidth=w,anchor='n')
        self._create_xyz_label_info()

    def _create_xyz_label_info(self):
        start,offset,y,offset2 = 0.05,0.3,0.35,0.27
        assi = ['x','y','z']
        for i,asse in enumerate(assi):
            label = tk.Label(self.position_frame_xyz,text=f'{asse}:'.upper(),font='Helvetic 8 bold',bg='lightgray')
            label.place(rely=y,relx=start+offset*i,anchor='nw')
            limitlabel = tk.Label(self.position_frame_xyz,text='mm',font='Helvetic 8')
            limitlabel.place(rely=y+0.02,relx=offset2*(i+1+(i-1)*0.1),anchor='nw')

class SerialInterface(tk.LabelFrame):

    def __init__(self,frameSX,porta,list_seria_port,baud_rate,set_connection,update_port_available):
        tk.LabelFrame.__init__(self,frameSX,labelanchor='n',text='SET SERIAL CONNECTION',bg='black',fg='white')
        self.baud_list = ["9600","38400"]
        if len(list_seria_port) == 0:
            self.list_seria_port = [None]
        else:
            self.list_seria_port=list_seria_port
        self._create_frame_items(porta,baud_rate,set_connection,update_port_available)
        

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
        
