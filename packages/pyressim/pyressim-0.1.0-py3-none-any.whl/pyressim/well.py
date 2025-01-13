class Well:
    def __init__(self, name, x, y, depth):
        self.name = name
        self.x = x
        self.y = y
        self.depth = depth

    def __repr__(self):
        return f"Well(name={self.name}, location=({self.x}, {self.y}), depth={self.depth})"