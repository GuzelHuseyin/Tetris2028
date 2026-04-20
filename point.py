class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def translate(self, dx, dy):
        self.x += dx
        self.y += dy

    def move(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Point(self.x, self.y)

    def __str__(self):
        return f'({self.x}, {self.y})'
