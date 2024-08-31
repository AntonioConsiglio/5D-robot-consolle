
class ButtonStyle():
    def __init__(self):
        self.red_button= '''QPushButton
                            {
                                background-color:#D21502;
                                border: 1px red solid;
                            }
                            QPushButton:hover
                            {
                                background-color:#F08080;
                            }
                            QPushButton:pressed
                            {
                                background-color:white;
                            }
                            '''
        self.green_button = '''QPushButton
                            {
                                background-color:#299617;
                                border: 1px red solid;
                            }
                            QPushButton:hover
                            {
                                background-color:#32CD32;
                            }
                            QPushButton:pressed
                            {
                                background-color:white;
                            }
                            '''