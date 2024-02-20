# A class to represent Colors
class Color: 
    # Init
    def __init__(self, values):
        self.r = float(values[0])
        self.g = float(values[1])
        self.b = float(values[2])
    # string
    def __repr__(self):
        return str([self.r, self.g, self.b])
    # equals
    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b
    # addition
    def __add__(self, other):
        return Color([self.r + other.r, self.g + other.g, self.b + other.b])
    # addition +=
    def __iadd__(self, other):
        self.r += other.r
        self.g += other.g
        self.b += other.b
        return self
    
    # Function that clamps the color values back down to 1.0 if they have gone beyond
    def clamp(self):
        if self.r > 1.0:
            self.r=1.0
        if self.g > 1.0:
            self.g=1.0
        if self.b > 1.0:
            self.b=1.0
