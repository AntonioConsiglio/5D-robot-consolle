from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
import os

def generate_launch_description():

    gazebo = IncludeLaunchDescription(
        os.path.join(
        get_package_share_directory("antoniobot_description"),
        "launch","gazebo.launch.py"
        ),
    )

    controller = IncludeLaunchDescription(
        os.path.join(
        get_package_share_directory("antoniobot_controller"),
        "launch","controller.launch.py"
        ),
        launch_arguments={"is_sim": "True"}.items()
    )

    moveit = IncludeLaunchDescription(
        os.path.join(
        get_package_share_directory("antoniobot_moveit"),
        "launch","moveit.launch.py"
        ),
    )  

    action_server = Node(
        package="antoniobot_actions",
        executable="task_server_node",
    )

    # ALEXA NOT IMPLEMENTED IN THIS CASE
    return LaunchDescription([
        gazebo,
        controller,
        moveit,
        action_server
    ])