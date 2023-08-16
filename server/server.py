from __future__ import division
import zlib
import time
import socket
import struct
import subprocess
import logging.handlers

from nvjpeg import NvJpeg
from datetime import datetime
from turbojpeg import TurboJPEG


logger = logging.getLogger('__main__')


class Server:
    def __init__(self, info, dname):
        self.dname = dname

        self.isReady = False

        if subprocess.check_output(["nvidia-smi"]):
            self.decomp = NvJpeg()
        else:
            self.decomp = TurboJPEG()

        self.HOST = info[0]
        self.PORT = info[1]

        self.MAX_DGRAM = 2 ** 16

        self.sock = None
        self.sock_udp()

        self.tmp_data = b''
        self.all_data = None

        self.client_get_img_time = None
        self.server_get_img_time = None

        self.latency_list = []

        self.sec = 0
        self.curr_time = time.time()
        self.prev_time = time.time()

        self.fps_list = []

    def __del__(self):
        self.sock.close()

    def sock_udp(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(1)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.HOST, self.PORT))

            self.isReady = True

            logger.info(f"Opened '{self.dname}' server. Host: {self.HOST}, Port: {self.PORT}")

            # self.dump_buffer()

        except Exception as e:
            logger.warning(e)

    def checksum(self, header):
        checksum = zlib.crc32(self.all_data)
        udp_header = struct.unpack("!I", header)
        correct_checksum = udp_header[0]

        return correct_checksum != checksum

    def dump_buffer(self):
        while True:
            seg, addr = self.sock.recvfrom(self.MAX_DGRAM)
            seg = seg.split(b'end')
            if struct.unpack("B", seg[0])[0] == 1:
                # logger.info("Finish emptying buffer")
                break

    def get_mean_fps(self):
        self.curr_time = time.time()
        self.sec = self.curr_time - self.prev_time
        self.prev_time = self.curr_time
        if self.sec > 0:
            result = round((1 / self.sec), 1)
        else:
            result = 1

        fps = result

        if len(self.fps_list) < 20:
            self.fps_list.append(fps)
        else:
            del self.fps_list[0]
            self.fps_list.append(fps)

        if len(self.fps_list) > 0:
            mean_fps = round(sum(self.fps_list) / len(self.fps_list), 1)

            return mean_fps

    def get_mean_latency(self):
        try:
            start = datetime.strptime(self.client_get_img_time, '%H:%M:%S.%f')
        except ValueError:
            start = datetime.strptime(self.client_get_img_time + '.0', '%H:%M:%S.%f')
        try:
            end = datetime.strptime(self.server_get_img_time, '%H:%M:%S.%f')
        except ValueError:
            end = datetime.strptime(self.server_get_img_time + '.0', '%H:%M:%S.%f')

        result = round((end - start).total_seconds() * 1000, 1)

        latency = result

        if len(self.latency_list) < 20:
            self.latency_list.append(latency)
        else:
            del self.latency_list[0]
            self.latency_list.append(latency)

        if len(self.latency_list) > 0:
            mean_latency = round(sum(self.latency_list) / len(self.latency_list), 1)

            return mean_latency
