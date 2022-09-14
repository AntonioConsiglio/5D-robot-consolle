import sys
#3rd party
from PySide2.QtWidgets import QApplication
import numpy as np
#mine
from applicationLib.hmiLib import MainWindow
from applicationLib.utilsLib import ArduinoConnection
from applicationLib.robotLib import Robot

def main():

    app = QApplication(sys.argv)
    root = MainWindow()

    socket_arduino = ArduinoConnection()
    root.set_connection_socket(socket_arduino)

    robot_object = Robot('Robot1')
    root.set_robot_object(robot_object)

    root.show()
    app.exec_()

if __name__ == '__main__':
    
    main()

    