import serial.tools.list_ports as p
import time

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
        # cls.com_port.addItems(ports)
        return True
    else:
        return True
