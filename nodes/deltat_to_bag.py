#!/usr/bin/env python3

import sys
import datetime
import rclpy

from rclpy.serialization import serialize_message
from marine_acoustic_msgs.msg import SonarDetections
import rosbag2_py

from imagenex_deltat.data_storage import read_file
from imagenex_deltat.utils import timestamp_from_strings


def datetime_to_ros_time(dt: datetime.datetime) -> rclpy.time.Time:
  seconds = (dt - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds()
  return rclpy.time.Time(seconds=int(seconds), nanoseconds=int((seconds % 1)* 1e9))


bag = rosbag2_py.SequentialWriter()
storage_options = rosbag2_py.StorageOptions(uri=sys.argv[1]+'.mcap', storage_id='mcap')
converter_options = rosbag2_py.ConverterOptions('', '')
bag.open(storage_options, converter_options)


bag.create_topic(rosbag2_py.TopicMetadata(id=0, name='sonar_detections', type='marine_acoustic_msgs/msg/SonarDetections', serialization_format='cdr'))


for ping in read_file(sys.argv[1]):
    print (ping)
    print (ping.ranges)
    msg = SonarDetections()

    timestamp = timestamp_from_strings(ping.date, ping.time, ping.milliseconds)
    msg.header.stamp = datetime_to_ros_time(timestamp).to_msg()

    msg.ping_info.frequency = float(ping.frequency)
    msg.ping_info.sound_speed = float(ping.sound_speed)

    bag.write('sonar_detections', serialize_message(msg), datetime_to_ros_time(timestamp).nanoseconds)
