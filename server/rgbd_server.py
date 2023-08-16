import cv2
import pickle
import struct
import numpy as np

from .server import Server
from datetime import datetime


class RgbdServer(Server):
    def __init__(self, info, dname):
        super().__init__(info, dname)

    def recv_udp(self):
        seg, addr = self.sock.recvfrom(self.MAX_DGRAM)
        seg = seg.split(b'end')
        if struct.unpack("B", seg[0])[0] > 1:
            self.tmp_data += seg[7]
        else:
            self.client_get_img_time = seg[3].decode('utf-8')
            self.tmp_data += seg[7]
            self.all_data = self.tmp_data
            self.tmp_data = b''

            is_data_corrupted = self.checksum(seg[1])
            if is_data_corrupted:
                # print("corrupted image has been deleted")
                return None
            else:
                self.all_data = self.all_data.split(b'frame')
                rgb = self.decomp.decode(self.all_data[0])
                depth = cv2.imdecode(np.asarray(bytearray(self.all_data[1]), dtype=np.uint8),
                                     cv2.IMREAD_UNCHANGED)

                self.server_get_img_time = datetime.now().time().isoformat()

                fps = self.get_mean_fps()
                latency = self.get_mean_latency()

                cam_info = seg[6].split(b'info')
                intrinsic = np.reshape(np.frombuffer(cam_info[0], dtype=np.float64), (3, 3))
                imu = np.asarray(pickle.loads(cam_info[1]))
                result = {
                    "rgb": rgb,
                    "depth": depth,
                    "imu": imu,
                    "intrinsic": intrinsic,
                    "fps": fps,
                    "latency": latency
                }

                return result
