class Grid:
    def __init__(self, nx, ny, nz, dx, dy, dz):
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.dx = dx
        self.dy = dy
        self.dz = dz

    def __repr__(self):
        return f"Grid({self.nx}x{self.ny}x{self.nz}, cell size=({self.dx}, {self.dy}, {self.dz}))"