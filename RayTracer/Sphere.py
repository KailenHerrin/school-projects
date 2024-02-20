import Color
import Point
# Class sphere
class Sphere: 
    # Init
    def __init__(self, name, location, scale, col, attributes):
        self.name = str(name)
        self.loc = Point.Point(location)
        self.scale = scale
        self.col = Color.Color(col)
        self.attributes = attributes
    # Equals
    def __eq__(self, other):
        if other != None:
            return self.name == other.name
        else:
            return False