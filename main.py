import serial
import tkinter as tk
import time
import function_utils as utils
from PIL import Image,ImageTk
from threading import Thread
import serial.tools.list_ports as p
import sys
import os
import matplotlib.pyplot as plt
import robot

my_robot = robot.Robot('arduino_robot')

plt.show()


def start_mode(**kwargs):
    global consolle_mode
    mode = consolle_mode.get()
    if mode == 'manual':
        Thread(name='message_sender',target=command_buttons_handel,args = [kwargs['control_panel'],kwargs['comunication_class']]).start()
    # if mode == 'forward':
    #     Thread(name='message_sender',target=commandButtonsHandel,args = [buttons,arduino]).start()
    # if mode == 'inverse':
    #     Thread(name='message_sender',target=commandButtonsHandel,args = [buttons,arduino]).start()


def command_buttons_handel(buttons,arduino):

    while True:
        try:    
            if  arduino.arduino is not None:
                for button in buttons:
                    if button.message is not None:
                        messaggio = button.message
                        if messaggio != b'0':
                            print(f'message_sent: {messaggio}')
                            arduino.arduino.write(messaggio)
                            button.message = None
                            break
                        if messaggio == b'0':
                            arduino.arduino.write(b'0')
                            button.message = None
                            print('messaggio inviato')
                            break
                               
                        
        except Exception as e:
            print(e)
            pass
            #break            
def set_connection(button):
    global porta, baud_rate
    if porta is not None and baud_rate is not None:
        if arduino.arduino is None:
            arduino.connection()
            button['text'] = 'DISCONNECT'
            button['bg'] = 'red'
        else:
            arduino.disconnet()
            arduino.arduino = None
            button['text'] = 'CONNECT'
            button['bg'] = 'green'


def update_port_available(to_update):
    global list_serial_port,porta
    porta.set(None)
    to_update['menu'].delete(0, 'end')
    list_serial_port = enumerate_serial_ports()
    for port in list_serial_port:
        to_update['menu'].add_command(label=port, command=tk._setit(porta, port))
   

def enumerate_serial_ports():
    """  return a iterator of serial (COM) ports existing on this computer.
    """
    port = p.comports()
    ports = [i.device for i in port]
    return ports


if __name__ == '__main__':
    try:
        root = tk.Tk()
        root.title('CONSOLLE')
        root.geometry("1300x800")
        root.resizable(False,False)

        # gloval variabile
        global porta, baud_rate,list_serial_port,consolle_mode
        porta= tk.StringVar()
        porta.set(None)
        baud_rate=tk.StringVar()
        baud_rate.set(None)
        consolle_mode = tk.StringVar()
        consolle_mode.set('manual')

        # Enumerate serial ports
        list_serial_port = enumerate_serial_ports()

        ## MAIN FRAME OF CONSOLLE == 3

        frameTV = tk.Frame(root,bg = 'grey')
        frameTV.place(relx= 0.25,rely=0,anchor='n',relwidth=0.508,relheight=0.67)

        frameManual = tk.Frame(root,bg = 'black')
        frameManual.place(relx= 0.75,rely=0,anchor='n',relwidth=0.492,relheight=0.67)

        frame_down =  utils.FrameDown(root,bg='yellow')
        frame_down.place(relx= 0.5,rely=0.67,anchor='n',relwidth=1,relheight=0.33)
        ## frameManual subframe

        frameSX = tk.Frame(frameManual,bg = 'black')
        frameSX.place(relx= 0.25,rely=0,anchor='n',relwidth=0.5,relheight=1)

        frameDX = tk.LabelFrame(frameManual,bg = 'white',labelanchor='n',text='MANUAL COMMAND',font='Helvetic 10 bold')
        frameDX.place(relx= 0.75,rely=0,anchor='n',relwidth=0.5,relheight=1)

        ## frameTV subframe
        frame_cam = tk.Frame(frameTV,bg='black',relief='sunken')
        frame_cam.place(relx=0.504,rely=0.05,width=646,height=486,anchor='n')
        
        canvas_cam = utils.CanvasCam(frame_cam,relx=0.5,rely=0,anchor='n')
        camera_manager = utils.VideoCapture(canvas_cam,camera_number=2) 

        ## FRAME SX

        robot_canva = tk.Canvas(frameSX)
        imageTK = ImageTk.PhotoImage(Image.open(r'images\\robot.png'))
        robot_canva.create_image(0,5,image = imageTK,anchor='nw')
        robot_canva.image = imageTK
        robot_canva.place(relx=0.5,y=1,relwidth=0.98,relheight=0.83,anchor='n',)

        utils.SerialInterface(frameSX,porta,list_serial_port,baud_rate,set_connection,update_port_available)

        #FRAME DX (create 6 subframe)
        start, inc = 0.02,0.16
        handTool = utils.CommandButton(frameDX,text='HAND',rely=start,mexPlus = b'1',mexMenos = b'2',number=1)
        start += inc
        wristY = utils.CommandButton(frameDX,text='ROTATION WRIST Y',rely=start,mexPlus = b'3',mexMenos = b'4',number=2)
        start += inc
        wristX = utils.CommandButton(frameDX,text='ROTATION WRIST X',rely=start,mexPlus = b'5',mexMenos = b'6',number=3)
        start += inc
        elbow = utils.CommandButton(frameDX,text='ELBOW',rely=start,mexPlus = b'7',mexMenos = b'8',number=4)
        start += inc
        shoulderY = utils.CommandButton(frameDX,text='ROTATION SHOULDER Y',rely=start,mexPlus = b'9',mexMenos = b'10',number=5)
        start += inc
        shoulderZ = utils.CommandButton(frameDX,text='ROTATION SHOULDER Z',rely=start,mexPlus = b'11',mexMenos = b'12',number=6)

        ## List of buttons for manual command
        buttons = [handTool,wristY,wristX,elbow,shoulderY,shoulderZ]

        # Donw frame setting --> 2 subframe frameDown

        
        # Serial connection object
        arduino = utils.SerialConnection(porta,baud_rate)

        # Robot object
        my_robot = robot.Robot('arduino_robot')
        print(my_robot.forward_kinematics([0]*7))

        # Start mode
        start_mode(control_panel = buttons,comunication_class=arduino)


        

        



        root.protocol("WM_DELETE_WINDOW",lambda: sys.exit())
        root.mainloop()
    except SystemExit:
        camera_manager.state=False
        os.abort()
    

