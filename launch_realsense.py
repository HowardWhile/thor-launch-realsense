#!/usr/bin/env python3
"""Launch all RealSense cameras with ros2 launch ./launch_realsense.py.

Set the delay with interval:=5; show arguments with --show-args.
Source the ROS 2 environment before launching. Press Ctrl+C to stop all cameras.
"""

import math
import os
import shutil
import re
import subprocess

from ament_index_python.packages import PackageNotFoundError, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, TimerAction
from launch.substitutions import LaunchConfiguration


def parse_serials(output):
    """Read serials from the short listing, preserving device order."""
    return list(dict.fromkeys(re.findall(
        r'^\s*RealSense\s+.+?\s+(\d+)\s+\S+\s*$', output, re.MULTILINE)))


def check_dependencies():
    """Report missing tools and installation instructions before discovery."""
    missing = []
    try:
        get_package_prefix('realsense2_camera')
    except PackageNotFoundError:
        distro = os.environ.get('ROS_DISTRO', '<ros-distro>')
        missing.append(
            'realsense2_camera was not found. Install it with:\n'
            f'  sudo apt install ros-{distro}-realsense2-camera\n'
            'If already installed, source the ROS 2 and workspace setup.bash files.')
    if shutil.which('rs-enumerate-devices') is None:
        missing.append(
            'rs-enumerate-devices was not found. Install it with:\n'
            '  sudo apt install librealsense2-utils\n'
            'If the package is unavailable, configure the RealSense package repository:\n'
            '  https://github.com/realsenseai/librealsense/blob/master/doc/distribution_linux.md')
    if missing:
        raise RuntimeError('Missing RealSense dependencies:\n\n' + '\n\n'.join(missing))


def launch_cameras(context):
    interval = float(LaunchConfiguration('interval').perform(context))
    if not math.isfinite(interval) or interval < 0:
        raise ValueError('interval must be a finite number >= 0')
    check_dependencies()
    try:
        listing = subprocess.run(['rs-enumerate-devices', '-s'], check=True,
                                 capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError) as error:
        details = ''
        if isinstance(error, subprocess.CalledProcessError):
            details = (error.stdout or '') + (error.stderr or '')
        raise RuntimeError(f'Cannot enumerate RealSense cameras: {error}\n{details}') from error
    serials = parse_serials(listing.stdout)
    if not serials:
        raise RuntimeError('No RealSense cameras found.\n' + listing.stdout + listing.stderr)

    actions = []
    for index, serial in enumerate(serials):
        # The underscore keeps numeric serials as strings in ROS launch.
        camera = ExecuteProcess(
            cmd=['ros2', 'launch', 'realsense2_camera', 'rs_launch.py',
                 f'camera_name:=camera{serial}', f'serial_no:=_{serial}'],
            output='screen')
        actions.append(camera if index == 0 else TimerAction(
            period=index * interval, actions=[camera]))
    return actions


def generate_launch_description():
    """Declare the delay and defer discovery until launch execution."""
    return LaunchDescription([
        DeclareLaunchArgument(
            'interval', default_value='2',
            description='Seconds between camera launches; accepts decimals or 0 (default: 2).'),
        OpaqueFunction(function=launch_cameras),
    ])
