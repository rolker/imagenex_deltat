#!/usr/bin/env python3

from typing import Optional

import socket
import struct
import math
import datetime

from imagenex_deltat.profile import Ping
from imagenex_deltat.utils import timestamp_from_strings

import rclpy

from rclpy.executors import ExternalShutdownException
from rclpy.executors import SingleThreadedExecutor

from rclpy.lifecycle import Node
from rclpy.lifecycle import Publisher
from rclpy.lifecycle import State
from rclpy.lifecycle import TransitionCallbackReturn

from sensor_msgs_py import point_cloud2
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header


def datetime_to_ros_time(dt: datetime.datetime) -> rclpy.time.Time:
  seconds = (dt - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds()
  return rclpy.time.Time(seconds=int(seconds), nanoseconds=int((seconds % 1)* 1e9))


class DeltaT(Node):
    def __init__(self, node_name, **kwargs):
        self.soundings_publisher: Optional[Publisher] = None
        self.frame_id = 'deltat'
        self.in_socket: Optional[socket.socket] = None
        self.out_socket: Optional[socket.socket] = None
        self.in_host = ''
        self.in_port = 4040
        self.out_host = ''
        self.out_port = 0
        super().__init__(node_name, **kwargs)


    def on_configure(self, state: State) -> TransitionCallbackReturn:
        try:
            self.declare_parameter('frame_id', self.frame_id)
            self.declare_parameter('in_host', self.in_host)
            self.declare_parameter('in_port', self.in_port)
            self.declare_parameter('out_host', self.out_host)
            self.declare_parameter('out_port', self.out_port)

            self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value

            self.in_host = self.get_parameter('in_host').get_parameter_value().string_value
            self.in_port = self.get_parameter('in_port').get_parameter_value().integer_value

            self.out_host = self.get_parameter('out_host').get_parameter_value().string_value
            self.out_port = self.get_parameter('out_port').get_parameter_value().integer_value


            self.in_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.in_socket.settimeout(0.1)
            self.in_socket.bind((self.in_host, self.in_port))

            if self.out_port > 0:
                self.out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.soundings_publisher = self.create_lifecycle_publisher(
                PointCloud2,
                'soundings',
                5
            )



        except Exception as e:
            import traceback
            traceback.print_exc()
            return TransitionCallbackReturn.ERROR

        return TransitionCallbackReturn.SUCCESS


    def on_activate(self, state: State) -> TransitionCallbackReturn:
        return super().on_activate(state)

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        return super().on_deactivate(state)

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        self.destroy_publisher(self.soundings_publisher)
        self.in_socket = None
        self.out_socket = None
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        self.destroy_publisher(self.soundings_publisher)
        self.in_socket = None
        self.out_socket = None
        return TransitionCallbackReturn.SUCCESS

    def spin(self):
       
        while rclpy.ok():
            if self.in_socket is not None:
                try:
                    data, addr = self.in_socket.recvfrom(2048)
                    if self.out_socket is not None:
                        self.out_socket.sendto(data, (self.out_host, self.out_port))

                    p = Ping(data)

                    if p.marker.decode() == '83P':

                        points = []
                        for i in range(len(p.ranges)):
                            if p.intensities is None or p.intensities[i] > 0:
                                angle = p.start_angle+i*p.angle_increment
                                radians = math.radians(angle)
                                c = math.cos(radians)
                                depth = c*p.range_meters[i]
                                s = math.sin(radians)
                                yoffset = s*p.range_meters[i]
                                intensity = 1.0
                                if p.intensities is not None:
                                    intensity *= p.intensities[i]

                                # quick hack to provide uncertainties
                                v_uncertainty = max(0.1, depth*0.01)
                                h_uncertainty = max(0.01, abs(yoffset*0.01))
                                points.append((0.0, yoffset, depth, intensity, v_uncertainty, h_uncertainty))

                        fields = [
                            PointField(
                                name = 'x',
                                offset = 0,
                                datatype = PointField.FLOAT32,
                                count = 1
                            ),
                            PointField(
                                name = 'y',
                                offset = 4,
                                datatype = PointField.FLOAT32,
                                count = 1
                            ),
                            PointField(
                                name = 'z',
                                offset = 8,
                                datatype = PointField.FLOAT32,
                                count = 1
                            ),
                            PointField(
                                name = 'i',
                                offset = 12,
                                datatype = PointField.FLOAT32,
                                count =  1
                            ),
                            PointField(
                                name = 'vertical_uncertainty',
                                offset = 16,
                                datatype = PointField.FLOAT32,
                                count =  1
                            ),
                            PointField(
                                name = 'horizontal_uncertainty',
                                offset = 20,
                                datatype = PointField.FLOAT32,
                                count =  1
                            ),
                        ]

                        header = Header()
                        header.frame_id = self.frame_id

                        timestamp = timestamp_from_strings(p.date, p.time, p.ping_ms)

                        header.stamp = datetime_to_ros_time(timestamp).to_msg()
                        pc2 = point_cloud2.create_cloud(header, fields, points)
                        self.soundings_publisher.publish(pc2)


                except socket.timeout:
                    pass


            rclpy.spin_once(self, timeout_sec=0.0)


  

class FileReader:
  def __init__(self):
    pass

  def read(self, filename):
    f = open(filename, 'rb')
    f.seek(0, 2)
    filesize = f.tell()
    f.seek(0,0)
    print(filename,filesize,'bytes')
    while True:
      header = f.read(6)
      if len(header) != 6:
        break
      f.seek(-6,1)
      marker, version, packet_size = struct.unpack('>3sBH', header[:6])
      print (marker, version, packet_size)
      data = f.read(packet_size)
      #p = imagenex.Ping(data)


# if len(sys.argv) > 1:
#   f = FileReader()
#   for arg in sys.argv[1:]:
#     f.read(arg)
# else:


def main(args=None):
    rclpy.init()
    deltat = DeltaT('deltat')
    try:
        deltat.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()
