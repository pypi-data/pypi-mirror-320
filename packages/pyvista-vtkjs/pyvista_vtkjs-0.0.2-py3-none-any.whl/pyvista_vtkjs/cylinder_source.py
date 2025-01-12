class CylinderSource():
    def __init__(
        self,
        center  = (0.0, 0.0, 0.0),
        direction = (1.0, 0.0, 0.0),
        radius = 0.5,
        height = 1.0,
        capping = True,
        resolution = 100,
    ) -> None:
        self.center = center
        self.direction = direction
        self.radius = radius
        self.height = height
        self.resolution = resolution
        self.capping = capping
    def SetHeight(self, x):
        self.height = x
    def SetRadius(self, x):
        self.radius = x
    def SetResolution(self, x):
        self.resolution = x
