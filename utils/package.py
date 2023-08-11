class Package:
    def __init__(self, cfg, side):
        self.cfg = cfg

        self.host = self.cfg.HOST

        self.side = side

        self.port = getattr(self.cfg.PORT, self.side)
        self.size = getattr(self.cfg.SIZE, self.side)

        self.cam_info = None

        self.frame = None
        self.get_img_time = None

        self.header = None
