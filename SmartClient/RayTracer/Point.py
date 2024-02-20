import numpy
# Class Point
class Point: 
    # Init
    def __init__(self, values):
        self.x = float(values[0])
        self.y = float(values[1])
        self.z = float(values[2])
        self.values = values
    # Multiply
    def __mul__(self, other):
        return Point([self.x * other, self.y * other, self.z * other])
    # Subtract 2 points
    def __sub__(self, other):
        return Point([self.x - other.x, self.y - other.y, self.z - other.z])
    # add 2 points
    def __add__(self, other):
        return Point([self.x + other.x, self.y + other.y, self.z + other.z])
    # string
    def __repr__(self):
        return str([self.x, self.y, self.z])
    # Divide
    def __div__(self, other):
        return Point.Point([self.x / other, self.y / other, self.z / other])
    # Equals
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z
