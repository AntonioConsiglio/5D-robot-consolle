# 5D-robot-consolle
This is the updated project using ROS2 HUMBLE distribution

## About the project
In this repository, you'll find the code segment designed to create a PC application that interfaces with a 3D-printed robotic arm 
controlled by an Arduino Uno board and an external camera, specifically a stereo camera OAK-D Lite.
The application enables users to command the movements of the robotic arm, calibrate the stereo camera, and assign a reference system. 
Following calibration, an object detection algorithm allows the identification of objects, and their coordinates can be sent 
to the robot for it to reach the identified objects.

This branch use ROS2 humble. To perform the IK moveit2 package is used, most of the code is written in c++.

## How to use it

1) Install ROS2 humble or your Linux OS (Ubuntu 22.04) or use WSL2 by windows (This was my choiche)
   ```bash 
   sudo apt-get install xacro
   sudo apt-get install gazebo-ros
   sudo apt-get install ros2-humble-joint-state-publisher-gui
   sudo apt-get install ros2-humble-ros2-controllers
   sudo apt-get install ros2-humble-gazebo-ros2-control
   # install colcon and libserial for c++
   sudo apt install python3-colcon-common-extension
   sudo apt-get install libserial-dev
2) Install moveit2 and cycloneadds_cpp DDS:

   ```bash
   sudo apt-get install ros2-humble-moveit
   sudo apt install ros2-rolling-raw-cyclonedds-cpp
   # to make work the installed dds
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
3) Add command in the .bashrc called every time a new bash window is initialized
   ```bash
   source /opt/ros/humble/setup.bash #source ros2 
   source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash #source colcon
   # source the current workspace
   source <folder where the repository has been cloned>/5D-robot-consolle/ros2humb_ws/install/setup.bash 
   # For make Gazebo work on wsl2 if you have a dedicated GPU add this line in the .bashrc file:
   export MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"  
4) I'm using the OAK-D Lite smart stereo camera...

      **- - - - -WORK IN PROGRESS- - - - -**

## Some Results

### 1) Developed the hardware interface between ROS2 and Arduino. Throught an Action server it is possible to move the robot giving an x,y,z goal:

![](https://github.com/AntonioConsiglio/5D-robot-consolle/blob/ros2humble/images/robot_example.gif)



