# 5D-robot-consolle

1) Download and install anaconda
2) Open prompt and write [ conda env create -f requirements.txt -n (the name you prefer) ]
3) For the inverse kinematics it is used this library: https://github.com/Phylliade/ikpy
4) I'm using the OAK-D Lite smart stereo camera, you can find the script to manage it inside ./apllicationLib\\cameraLib folder
5) Now it is possibile to calibrate the OAK-D Lite to world cordinate using a simple chessboard.
   Here an example of what is possible using a custom ssd blob model and the calibrated camera.
   
![](https://github.com/AntonioConsiglio/5D-robot-consolle/blob/main/images/example_detection.gif)

6) TODO: Develop the pick and place function.

