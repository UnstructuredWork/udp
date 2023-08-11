class CamPackage:
    def __init__(self, cfg, side):
        self.cfg = cfg
        self.side = side

        self.host = self.cfg.HOST

        self.port = getattr(self.cfg.PORT, self.side)
        self.size = getattr(self.cfg.SIZE, self.side)

        self.cam_info = None

        self.frame = None
        self.get_img_time = None

        self.header = None

class ServicePackage:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.data = None
        self.get_data_time = None

        self.header = None