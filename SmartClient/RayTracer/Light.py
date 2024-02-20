import Color
import Point
# Class Light
class Light: 
    # Init
    def __init__(self, name, location, col):
        self.name = str(name)
        self.loc = Point.Point(location)
        self.col = Color.Color(col)
