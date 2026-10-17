import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory("vishwaa_description")
    gz = get_package_share_directory("gazebo_ros")
    xacro_file = os.path.join(pkg, "urdf", "vishwaa_gazebo.urdf.xacro")
    desc = ParameterValue(Command(["xacro ", xacro_file]), value_type=str)

    # Allow Gazebo to resolve model://vishwaa_description mesh paths
    pkg_share_parent = os.path.dirname(pkg)
    model_path = AppendEnvironmentVariable(
        name="GAZEBO_MODEL_PATH",
        value=pkg_share_parent
    )

    # Prevent Gazebo from hanging while querying the online model database
    database_uri = SetEnvironmentVariable(
        name="GAZEBO_MODEL_DATABASE_URI",
        value=""
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gz, "launch", "gazebo.launch.py")))

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": desc, "use_sim_time": True}]
    )

    spawn = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-entity", "vishwaa",
            "-z", "0.05",
            "-package_to_model"
        ]
    )

    rviz_arg = DeclareLaunchArgument(
        "rviz",
        default_value="false",
        description="Launch RViz2 alongside Gazebo"
    )

    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg, "launch", "rviz.launch.py")),
        condition=IfCondition(LaunchConfiguration("rviz"))
    )

    return LaunchDescription([
        model_path,
        database_uri,
        rviz_arg,
        gazebo,
        rsp,
        spawn,
        rviz_launch
    ])