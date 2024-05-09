#!/usr/bin/env python3

import socket
import struct
import sys
import math

from imagenex_deltat import imagenex

import rospy

from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header


rospy.init_node("deltat")

frame_id = rospy.get_param("~frame_id", "deltat")

pub = rospy.Publisher("soundings", PointCloud2, queue_size=5)

class NetworkListener:
  def __init__(self) -> None:
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    self.s.settimeout(0.1)
    self.s.bind(('', 4040))

  def run(self):
    while True:
      if rospy.is_shutdown():
        break
      try:
        data, addr = self.s.recvfrom(2048)
        #print (data)
        format = '>3sBH2x11sx8sx3sx13sx13sxBHHHHHHHHBH'
        format_size = struct.calcsize(format)
        if len(data) >= format_size:
          parts = struct.unpack(format, data[:format_size])
          #print(parts)
        p = imagenex.Ping(data)

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
            points.append((0.0, yoffset, depth, intensity))

        fields = [PointField('x', 0, PointField.FLOAT32, 1),
          PointField('y', 4, PointField.FLOAT32, 1),
          PointField('z', 8, PointField.FLOAT32, 1),
          PointField('i', 12, PointField.FLOAT32, 1),
          ]

        header = Header()
        header.frame_id = frame_id
        #print(p.timestamp())
        header.stamp = rospy.Time.from_sec(p.timestamp().timestamp())
        pc2 = point_cloud2.create_cloud(header, fields, points)
        pub.publish(pc2)


      except socket.timeout:
        pass
  

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
n = NetworkListener()
n.run()
