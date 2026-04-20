import random
import lib.stddraw as stddraw
from lib.color import Color


class Tile:
    boundary_thickness = 0.004
    font_family = 'Arial'
    font_size = 16

    PALETTE = {
        2:    (Color(238, 228, 218), Color(119, 110, 101), Color(187, 173, 160)),
        4:    (Color(237, 224, 200), Color(119, 110, 101), Color(187, 173, 160)),
        8:    (Color(242, 177, 121), Color(255, 255, 255), Color(205, 133, 63)),
        16:   (Color(245, 149, 99), Color(255, 255, 255), Color(200, 100, 40)),
        32:   (Color(246, 124, 95), Color(255, 255, 255), Color(180, 80, 30)),
        64:   (Color(246, 94, 59), Color(255, 255, 255), Color(150, 60, 30)),
        128:  (Color(237, 207, 114), Color(255, 255, 255), Color(140, 110, 50)),
        256:  (Color(237, 204, 97), Color(255, 255, 255), Color(130, 100, 50)),
        512:  (Color(237, 200, 80), Color(255, 255, 255), Color(120, 90, 40)),
        1024: (Color(237, 197, 63), Color(255, 255, 255), Color(110, 80, 30)),
        2048: (Color(237, 194, 46), Color(255, 255, 255), Color(90, 60, 30)),
    }
    DEFAULT_COLORS = (Color(60, 58, 50), Color(255, 255, 255), Color(120, 110, 100))

    def __init__(self, number=None):
        self.number = number if number is not None else (2 if random.random() < 0.75 else 4)
        self._update_colors()

    def clone(self):
        return Tile(self.number)

    def set_number(self, new_number):
        self.number = new_number
        self._update_colors()

    def _update_colors(self):
        self.background_color, self.foreground_color, self.box_color = self.PALETTE.get(
            self.number,
            self.DEFAULT_COLORS,
        )

    def draw(self, position, length=1.0, scale=1.0, ghost=False, ghost_border=None):
        radius = (length * scale) / 2.0
        if ghost:
            stddraw.setPenColor(ghost_border if ghost_border is not None else self.box_color)
            stddraw.setPenRadius(Tile.boundary_thickness)
            stddraw.square(position.x, position.y, radius)
            stddraw.setPenRadius()
            return

        stddraw.setPenColor(self.background_color)
        stddraw.filledSquare(position.x, position.y, radius)

        stddraw.setPenColor(self.box_color)
        stddraw.setPenRadius(Tile.boundary_thickness)
        stddraw.square(position.x, position.y, radius)
        stddraw.setPenRadius()

        font_size = Tile.font_size
        if self.number >= 1024:
            font_size = 13
        elif self.number >= 128:
            font_size = 14

        stddraw.setPenColor(self.foreground_color)
        stddraw.setFontFamily(Tile.font_family)
        stddraw.setFontSize(max(10, int(font_size * scale)))
        stddraw.boldText(position.x, position.y, str(self.number))

    def __repr__(self):
        return f'Tile(number={self.number})'
