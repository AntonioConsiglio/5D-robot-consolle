import sys
#3rd party
from PyQt5.QtWidgets import QApplication
#mine
from applicationLib.hmiLib import MainWindow
from applicationLib.utilsLib import ArduinoConnection
from applicationLib.robotLib import Robot



if __name__ == '__main__':
    app = QApplication(sys.argv)
    root = MainWindow()

    socket_arduino = ArduinoConnection()
    root.set_connection_socket(socket_arduino)

    robot_object = Robot('Robot1')
    root.set_robot_object(robot_object)

    root.show()
    app.exec_()