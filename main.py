from turtle import color
import serial
import tkinter as tk
import time
import function_utils as utils
from PIL import Image,ImageTk
from threading import Thread
import serial.tools.list_ports as p


def commandButtonsHandel(buttons):
    while True:
        for button in buttons:
            if button.message is not None:
                print(button.message)

def setConnection():
    global porta, baud_rate
    if porta is not None and baud_rate is not None:
        serialConn.connection()

def updatePortAvailable(daUpdate,frameUpdate):
    global list_serial_port,porta
    porta.set(None)
    daUpdate['menu'].delete(0, 'end')
    list_serial_port = enumerate_serial_ports()
    for port in list_serial_port:
        daUpdate['menu'].add_command(label=port, command=tk._setit(porta, port))
   



def enumerate_serial_ports():
    """ Uses the Win32 registry to return a iterator of serial 
        (COM) ports existing on this computer.
    """
    port = p.comports()
    ports = [i.device for i in port]
    return ports



if __name__ == '__main__':
    root = tk.Tk()
    root.title('CONSOLLE')
    root.geometry("640x800")
    root.resizable(False,False)

    # gloval variabile
    global porta, baud_rate,list_serial_port
    porta= tk.StringVar()
    porta.set(None)
    baud_rate=tk.StringVar()
    baud_rate.set(None)

    ## MAIN FRAME OF CONSOLLE == 3

    frameSX = tk.Frame(root,bg = 'black')
    frameSX.place(relx= 0.25,rely=0,anchor='n',relwidth=0.5,relheight=0.67)

    frameDX = tk.LabelFrame(root,bg = 'white',labelanchor='n',text='MANUAL COMMAND',font='Helvetic 10 bold')
    frameDX.place(relx= 0.75,rely=0,anchor='n',relwidth=0.5,relheight=0.67)

    frameDown = tk.LabelFrame(root,bg = 'yellow')
    frameDown.place(relx= 0.5,rely=0.67,anchor='n',relwidth=1,relheight=0.33)

    ## FRAME SX

    robotCanva = tk.Canvas(frameSX)
    imageTK = ImageTk.PhotoImage(Image.open('robot.png'))
    robotCanva.create_image(0,5,image = imageTK,anchor='nw')
    robotCanva.image = imageTK
    robotCanva.place(relx=0.5,y=1,relwidth=0.98,relheight=0.83,anchor='n',)

    #FRAME DX (create 6 subframe)
    start, inc = 0.02,0.16
    frame1 = utils.CommandButton(frameDX,text='TWIST',rely=start,mexPlus = 1,mexMenos = 2)
    start += inc
    frame2 = utils.CommandButton(frameDX,text='TWIST',rely=start,mexPlus = 3,mexMenos = 4)
    start += inc
    frame3 = utils.CommandButton(frameDX,text='TWIST',rely=start,mexPlus = 5,mexMenos = 6)
    start += inc
    rot_polso = utils.CommandButton(frameDX,text='TWIST',rely=start,mexPlus = 7,mexMenos = 8)
    start += inc
    polso = utils.CommandButton(frameDX,text='TWIST',rely=start,mexPlus = 9,mexMenos = 10)
    start += inc
    presa = utils.CommandButton(frameDX,text='TWIST',rely=start,mexPlus = 11,mexMenos = 12)

    buttons = [frame1,frame2,frame3,rot_polso,polso,presa]

    Thread(name='message_sender',target=commandButtonsHandel,args = [buttons]).start()


    serialConn = utils.SerialConnection(porta,baud_rate)
    list_serial_port = enumerate_serial_ports()
    print(list_serial_port)


    utils.createSerialInterface(frameSX,porta,list_serial_port,baud_rate,setConnection,updatePortAvailable)


    






    root.mainloop()

