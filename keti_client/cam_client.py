from __future__ import division
import cv2
import math
import struct

from .base import Base
from .utils.package import CamPackage


class CamClient(Base):
    def __init__(self, cfg, meta, side):
        super().__init__(cfg)

        self.side = side

        self.pack_cloud = None
        self.pack_unity = None
        if cfg.CLOUD.SEND:
            self.pack_cloud = CamPackage(self.cfg.CLOUD, side)

        if cfg.UNITY.SEND:
            if side != "RGBD":
                self.pack_unity = CamPackage(self.cfg.UNITY, side)

    def send_udp(self, package):
        size = len(package.frame)
        count = math.ceil(size / (self.MAX_IMAGE_DGRAM))
        total_count = count
        array_pos_start = 0
        if self.img_num > 99:
            self.img_num = 1

        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            packet_num = (str(self.img_num).zfill(3) + '-' +
                          str(total_count) + '-' +
                          str(total_count - count + 1)).encode('utf-8')

            try:
                if package.cam_info is None:
                    self.sock.sendto(struct.pack("B", count) + b'end' +
                                     package.header + b'end' +
                                     packet_num + b'end' +
                                     package.get_img_time + b'end' +
                                     str(len(package.frame)).encode('utf-8') + b'end' +
                                     str(array_pos_start).encode('utf-8') + b'end' +
                                     package.frame[array_pos_start:array_pos_end], (package.host[0], package.port))
                else:
                    self.sock.sendto(struct.pack("B", count) + b'end' +
                                     package.header + b'end' +
                                     packet_num + b'end' +
                                     package.get_img_time + b'end' +
                                     str(len(package.frame)).encode('utf-8') + b'end' +
                                     str(array_pos_start).encode('utf-8') + b'end' +
                                     package.cam_info + b'end' +
                                     package.frame[array_pos_start:array_pos_end], (package.host[0], package.port))
            except OSError:
                pass

            array_pos_start = array_pos_end
            count -= 1

        self.img_num += 1

    def resize(self, frame, package):
        if frame.shape[0] == package.size[1]:
            return frame
        else:
            frame = cv2.resize(frame, dsize=(package.size), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            return frame
