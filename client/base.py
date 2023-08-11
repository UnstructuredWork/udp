import socket
import subprocess

from nvjpeg import NvJpeg
from turbojpeg import TurboJPEG


class Base:
    def __init__(self, cfg):
        self.cfg = cfg

        self.sock = None
        self.sock_udp()

        self.img_num = 1

        self.duplicate_check = None

        self.MAX_IMAGE_DGRAM = 2 ** 16 - 256

        if subprocess.check_output(["nvidia-smi"]):
            self.comp = NvJpeg()
        else:
            self.comp = TurboJPEG()

    def __del__(self):
        self.sock.close()

    def sock_udp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)