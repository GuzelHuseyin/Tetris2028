import copy as cp
import random
import numpy as np
from point import Point
from tile import Tile


class Tetromino:
    SHAPES = {
        'I': [(1, 0), (1, 1), (1, 2), (1, 3)],
        'O': [(0, 0), (0, 1), (1, 0), (1, 1)],
        'Z': [(0, 0), (1, 0), (1, 1), (2, 1)],
        'S': [(1, 0), (2, 0), (0, 1), (1, 1)],
        'T': [(1, 0), (0, 1), (1, 1), (2, 1)],
        'L': [(0, 0), (0, 1), (0, 2), (1, 2)],
        'J': [(1, 0), (1, 1), (1, 2), (0, 2)],
    }

    grid_height = 20
    grid_width = 12

    def __init__(self, shape_type):
        self.type = shape_type
        self.tile_matrix = self._build_matrix(shape_type)
        self.bottom_left_cell = Point()
        self.reset_position(randomize=True)

    def _build_matrix(self, shape_type):
        size = 4 if shape_type == 'I' else 2 if shape_type == 'O' else 3
        matrix = np.full((size, size), None)
        for col_idx, row_idx in self.SHAPES[shape_type]:
            matrix[row_idx][col_idx] = Tile()
        return matrix

    def clone(self):
        cloned = Tetromino(self.type)
        rows, cols = self.tile_matrix.shape
        cloned.tile_matrix = np.full((rows, cols), None)
        for row in range(rows):
            for col in range(cols):
                if self.tile_matrix[row][col] is not None:
                    cloned.tile_matrix[row][col] = self.tile_matrix[row][col].clone()
        cloned.bottom_left_cell = self.bottom_left_cell.copy()
        return cloned

    def get_cell_position(self, row, col, bottom_left=None, matrix=None):
        matrix = self.tile_matrix if matrix is None else matrix
        bottom_left = self.bottom_left_cell if bottom_left is None else bottom_left
        size = len(matrix)
        return Point(bottom_left.x + col, bottom_left.y + (size - 1) - row)

    def get_min_bounded_tile_matrix(self, return_position=False):
        size = len(self.tile_matrix)
        min_row, max_row = size - 1, 0
        min_col, max_col = size - 1, 0

        for row in range(size):
            for col in range(size):
                if self.tile_matrix[row][col] is not None:
                    min_row = min(min_row, row)
                    max_row = max(max_row, row)
                    min_col = min(min_col, col)
                    max_col = max(max_col, col)

        bounded = np.full((max_row - min_row + 1, max_col - min_col + 1), None)
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                if self.tile_matrix[row][col] is not None:
                    bounded[row - min_row][col - min_col] = self.tile_matrix[row][col].clone()

        if not return_position:
            return bounded, None

        blc = cp.copy(self.bottom_left_cell)
        blc.translate(min_col, (size - 1) - max_row)
        return bounded, blc

    def draw(self):
        size = len(self.tile_matrix)
        for row in range(size):
            for col in range(size):
                tile = self.tile_matrix[row][col]
                if tile is None:
                    continue
                pos = self.get_cell_position(row, col)
                if pos.y < self.grid_height:
                    tile.draw(pos)

    def draw_ghost(self, game_grid):
        ghost_bottom_left = self.bottom_left_cell.copy()
        while self.can_be_moved('down', game_grid, bottom_left=ghost_bottom_left):
            ghost_bottom_left.y -= 1
        size = len(self.tile_matrix)
        for row in range(size):
            for col in range(size):
                tile = self.tile_matrix[row][col]
                if tile is None:
                    continue
                pos = self.get_cell_position(row, col, bottom_left=ghost_bottom_left)
                if pos.y < self.grid_height:
                    tile.draw(pos, scale=0.92, ghost=True, ghost_border=game_grid.theme.ghost_border)

    def move(self, direction, game_grid):
        if not self.can_be_moved(direction, game_grid):
            return False
        if direction == 'left':
            self.bottom_left_cell.x -= 1
        elif direction == 'right':
            self.bottom_left_cell.x += 1
        elif direction == 'down':
            self.bottom_left_cell.y -= 1
        return True

    def hard_drop_distance(self, game_grid):
        distance = 0
        probe = self.bottom_left_cell.copy()
        while self.can_be_moved('down', game_grid, bottom_left=probe):
            probe.y -= 1
            distance += 1
        return distance

    def can_be_moved(self, direction, game_grid, bottom_left=None, matrix=None):
        matrix = self.tile_matrix if matrix is None else matrix
        bottom_left = self.bottom_left_cell if bottom_left is None else bottom_left
        size = len(matrix)
        for row in range(size):
            for col in range(size):
                if matrix[row][col] is None:
                    continue
                pos = self.get_cell_position(row, col, bottom_left=bottom_left, matrix=matrix)
                next_x, next_y = pos.x, pos.y
                if direction == 'left':
                    next_x -= 1
                elif direction == 'right':
                    next_x += 1
                elif direction == 'down':
                    next_y -= 1

                if next_x < 0 or next_x >= self.grid_width or next_y < 0:
                    return False

                if next_y < self.grid_height and game_grid.is_occupied(next_y, next_x):
                    if not self._belongs_to_self(next_y, next_x, bottom_left, matrix):
                        return False
        return True

    def _belongs_to_self(self, row, col, bottom_left, matrix):
        size = len(matrix)
        for local_row in range(size):
            for local_col in range(size):
                if matrix[local_row][local_col] is None:
                    continue
                pos = self.get_cell_position(local_row, local_col, bottom_left=bottom_left, matrix=matrix)
                if pos.y == row and pos.x == col:
                    return True
        return False

    def rotate(self, game_grid):
        if self.type == 'O':
            return True

        rotated = np.rot90(self.tile_matrix, k=3)
        for x_offset in (0, -1, 1, -2, 2):
            candidate = self.bottom_left_cell.copy()
            candidate.x += x_offset
            if self._rotation_fits(rotated, candidate, game_grid):
                self.tile_matrix = rotated
                self.bottom_left_cell = candidate
                return True
        return False

    def _rotation_fits(self, matrix, bottom_left, game_grid):
        size = len(matrix)
        for row in range(size):
            for col in range(size):
                if matrix[row][col] is None:
                    continue
                pos = self.get_cell_position(row, col, bottom_left=bottom_left, matrix=matrix)
                if pos.x < 0 or pos.x >= self.grid_width or pos.y < 0:
                    return False
                if pos.y < self.grid_height and game_grid.is_occupied(pos.y, pos.x):
                    return False
        return True

    def reset_position(self, randomize=False):
        size = len(self.tile_matrix)
        self.bottom_left_cell.y = self.grid_height - 1
        if randomize:
            self.bottom_left_cell.x = random.randint(0, self.grid_width - size)
        else:
            self.bottom_left_cell.x = (self.grid_width - size) // 2

    def __str__(self):
        return f'Tetromino({self.type})'
