'''
This script is made by Antonio Consiglio.
version == 1.0
date: 2022-01-30

Here there are the useful function to run the ROBOT ARM 5D. This script could be improved but the name of the funcion will remain the same as the start
'''

import serial
import numpy as np
import tkinter as tk
from threading import Thread
from PIL import Image,ImageTk


class SerialConnection():

    def __init__(self,porta,baud_rate):
        self.porta = porta
        self.baud_rate = baud_rate
        self.arduino = None

    def connection(self):
        porta = self.porta.get()
        porta = porta[2:len(porta)-3]
        baudrate = self.baud_rate.get()
        baudrate = int(baudrate[2:len(baudrate)-3])
        self.arduino = serial.Serial(port=porta,baudrate=baudrate)
        print('Connesso !')
    

class CommandButton():

    def __init__(self,root,**kwargs):
        self.frame = self.__create_button_frame(root,kwargs)
        self.menos = self.__buttonCreator(tipo ='menos',relx=0.25)
        self.plus = self.__buttonCreator(tipo = 'plus',relx=0.75)
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

    def __buttonCreator(self,**kwargs):
        img = Image.open(f'images\\{kwargs["tipo"]}.png')
        img = ImageTk.PhotoImage(img)
        button = tk.Button(self.frame,image=img,command = self.__donothing,borderwidth=0)
        button.image=img
        button.place(relx=kwargs['relx'],rely=-0.07,anchor='n')
        button.bind('<Button-1>',lambda e: Thread(name = 'Button Pressed',target=self.__dosomething, args=[e,kwargs["tipo"]]).start())
        return button
    
    def __donothing(self):
        self.ButtonMenosPress = False
        self.ButtonPlusPress = False
        self.message = None
        print('END')

    def __dosomething(self,event,button):
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

def createSerialInterface(frameSX,porta,list_seria_port,baud_rate,setConnection,updatePortAvailable):

    connectionFrame = tk.LabelFrame(frameSX,labelanchor='n',text='SET SERIAL CONNECTION',bg='black',fg='white')
    setPorta = tk.OptionMenu(connectionFrame,variable=porta,value=list_seria_port)
    setBaudrate = tk.OptionMenu(connectionFrame,variable=baud_rate,value=['9600'])
    pulsanteProva = tk.Button(connectionFrame,text='CONNECT',command=setConnection,bg='green',font='Helvetic 10 bold')
    pulsanteProva1 = tk.Button(connectionFrame,text='refresh port',command=lambda: updatePortAvailable(setPorta,connectionFrame),
                                bg='lightblue',font='Helvetic 8 bold')
    label1 = tk.Label(connectionFrame,text='SERIAL PORT',bg = 'black',fg='white',borderwidth=0)
    label2 = tk.Label(connectionFrame,text='BAUD RATE',bg = 'black',fg='white',borderwidth=0)
    label1.place(relx=0.2,rely=0.05,anchor='n')
    label2.place(relx=0.5,rely=0.05,anchor='n')
    setPorta.place(relx=0.2,rely=0.35,anchor='n')
    setBaudrate.place(relx=0.5,rely=0.35,anchor='n')
    pulsanteProva.place(relx=0.8,rely=0.50,relwidth=0.3,anchor='n')
    pulsanteProva1.place(relx=0.8,rely=0.05,anchor='n')
    connectionFrame.place(relx=0.5,rely=0.83,relheight=0.17,relwidth=1,anchor='n')