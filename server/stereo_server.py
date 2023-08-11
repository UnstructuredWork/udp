import struct

from .server import Server
from datetime import datetime


class StereoServer(Server):
    def __init__(self, cfg, port, dname):
        super().__init__(cfg, port, dname)

    def recv_udp(self):
        seg, addr = self.sock.recvfrom(self.MAX_DGRAM)
        seg = seg.split(b'end')
        if struct.unpack("B", seg[0])[0] > 1:
            self.tmp_data += seg[6]
        else:
            self.client_get_img_time = seg[3].decode('utf-8')
            self.tmp_data += seg[6]
            self.all_data = self.tmp_data
            self.tmp_data = b''

            is_data_corrupted = self.checksum(seg[1])
            if is_data_corrupted:
                # print("corrupted image has been deleted")
                return None
            else:
                rgb = self.decomp.decode(self.all_data)

                self.server_get_img_time = datetime.now().time().isoformat()

                fps = self.get_mean_fps()
                latency = self.get_mean_latency()

                result = {
                    "rgb": rgb,
                    "fps": fps,
                    "latency": latency
                }

                return result
