from launch import LaunchDescription
from launch_ros.actions import Node

from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command,LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    model_args = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(
            get_package_share_directory("antoniobot_description"),
            "urdf","antoniobot.urdf.xacro"),
        description="urdf.xacro model to publish in robot_state_publisher"
    )
    # convert from xacro to plain urdf
    robot_description = ParameterValue(Command(["xacro ",LaunchConfiguration("model")]))

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description":robot_description}]
    )

    joint_state_pub_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(get_package_share_directory("antoniobot_description"),"rviz","display.rviz")]
    )
    return LaunchDescription([
        model_args,
        robot_state_publisher,
        joint_state_pub_gui,
        rviz_node
    ])