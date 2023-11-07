# 5D-robot-consolle

## About the project
In this repository, you'll find the code segment designed to create a PC application that interfaces with a 3D-printed robotic arm 
controlled by an Arduino Uno board and an external camera, specifically a stereo camera OAK-D Lite.
The application enables users to command the movements of the robotic arm, calibrate the stereo camera, and assign a reference system. 
Following calibration, an object detection algorithm allows the identification of objects, and their coordinates can be sent 
to the robot for it to reach the identified objects.

This code was written between the end of 2020 and 2021, at a time when I was delving into computer vision and Python development. 
It was one of my exercises that demanded significant effort at the time. I hope you enjoy it.

## How to use it

1) Download and install anaconda
2) Open prompt and write [ conda env create -f requirements.txt -n (the name you prefer) ]
3) For the inverse kinematics it is used this library: https://github.com/Phylliade/ikpy
4) I'm using the OAK-D Lite smart stereo camera, you can find the script to manage it inside ./apllicationLib\\cameraLib folder

## Some Results

### 1) Now it is possibile to calibrate the OAK-D Lite to world cordinate using a simple chessboard.
   Here an example of what is possible using a custom ssd blob model and the calibrated camera.
   
![](https://github.com/AntonioConsiglio/5D-robot-consolle/blob/main/images/example_detection.gif)

### 2) Developed the pick and place function.Click to the picture above to watch the video on YouTube:

[![Alt text](https://github.com/AntonioConsiglio/5D-robot-consolle/blob/main/images/Screenshot_ROBOTPROJECT.png)](https://www.youtube.com/watch?v=aZVqMUgobNk)

