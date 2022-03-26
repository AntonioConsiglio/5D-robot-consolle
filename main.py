import sys
#3rd party
from PyQt5.QtWidgets import QApplication
#mine
from application import MainWindow,ArduinoConnection
from robot import Robot



if __name__ == '__main__':
    app = QApplication(sys.argv)
    root = MainWindow()

    socket_arduino = ArduinoConnection()
    root.set_connection_socket(socket_arduino)

    robot_object = Robot('Robot1')
    root.set_robot_object(robot_object)

    root.show()
    app.exec_()