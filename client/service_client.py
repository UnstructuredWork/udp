from __future__ import division
import cv2
import json
import math
import zlib
import struct

from .base import Base
from datetime import datetime
from .utils.package import ServicePackage
from .utils.parallel import thread_method


class ServiceClient(Base):
    def __init__(self, cfg, service):
        super().__init__(cfg)

        self.service = service

        self.prev_time = 0
        self.curr_time = 0

        self.data = None

        port = getattr(self.cfg.SERVICE, self.service).PORT
        self.pack = ServicePackage(self.cfg.SERVICE.TARGET_HOST, port)

    def send_udp(self):
        size = len(self.pack.data)
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
                if self.service == 'DETECTION':
                    self.sock.sendto(self.pack.data[array_pos_start:array_pos_end], (self.pack.host, self.pack.port))
                else:
                    self.sock.sendto(struct.pack("B", count) + b'end' +
                                     self.pack.header + b'end' +
                                     packet_num + b'end' +
                                     self.pack.get_data_time + b'end' +
                                     str(len(self.pack.data)).encode('utf-8') + b'end' +
                                     str(array_pos_start).encode('utf-8') + b'end' +
                                     self.pack.data[array_pos_start:array_pos_end], (self.pack.host, self.pack.port))
            except OSError:
                pass

            array_pos_start = array_pos_end
            count -= 1

        self.img_num += 1

    def bytescode(self):
        data = self.data
        self.pack.get_data_time = datetime.now().time().isoformat().encode('utf-8')
        if self.service == 'DETECTION':
            self.pack.data = zlib.compress(json.dumps(data).encode('utf-8'))
        elif self.service == 'MONO_DEPTH':
            self.pack.data = cv2.imencode('.png', data, [cv2.IMWRITE_PNG_COMPRESSION, 4])[1].tobytes()

        check = zlib.crc32(self.pack.data)
        if self.duplicate_check != check:
            self.duplicate_check = check
            self.pack.header = struct.pack("!I", check)
            self.send_udp()

    @thread_method
    def run(self, data):
        self.data = data
        self.bytescode()