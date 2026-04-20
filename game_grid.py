from collections import deque
import numpy as np
import lib.stddraw as stddraw
from point import Point
from theme import DEFAULT_THEME

WIN_VALUE = 2048


class GameGrid:
    def __init__(self, grid_h, grid_w, theme=None):
        self.grid_height = grid_h
        self.grid_width  = grid_w
        self.tile_matrix = np.full((grid_h, grid_w), None)

        self.current_tetromino = None
        self.next_tetromino    = None
        self.held_tetromino    = None
        self.hold_used         = False

        self.score         = 0
        self.lines_cleared = 0
        self.game_over     = False
        self.game_won      = False
        self.kept_playing  = False

        self.theme          = theme or DEFAULT_THEME
        self.line_thickness = 0.0018
        self.box_thickness  = 0.008

    def display(self, pause=0):
        stddraw.clear(self.theme.background)
        self.draw_grid()
        if self.current_tetromino is not None:
            self.current_tetromino.draw_ghost(self)
            self.current_tetromino.draw()
        self.draw_boundaries()
        self.draw_ui()
        stddraw.show(pause)

    def draw_grid(self):
        stddraw.setPenColor(self.theme.grid_background)
        stddraw.filledRectangle(-0.5, -0.5, self.grid_width, self.grid_height)
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                tile = self.tile_matrix[row][col]
                if tile is not None:
                    tile.draw(Point(col, row))
        stddraw.setPenColor(self.theme.grid_line)
        stddraw.setPenRadius(self.line_thickness)
        for x in range(1, self.grid_width):
            stddraw.line(x - 0.5, -0.5, x - 0.5, self.grid_height - 0.5)
        for y in range(1, self.grid_height):
            stddraw.line(-0.5, y - 0.5, self.grid_width - 0.5, y - 0.5)
        stddraw.setPenRadius()

    def draw_boundaries(self):
        stddraw.setPenColor(self.theme.boundary)
        stddraw.setPenRadius(self.box_thickness)
        stddraw.rectangle(-0.5, -0.5, self.grid_width, self.grid_height)
        stddraw.setPenRadius()

    def draw_ui(self):
        panel_left  = self.grid_width - 0.5
        panel_width = 5
        cx          = panel_left + panel_width / 2
        top_y       = self.grid_height - 0.5   # = 19.5

        # Panel arka planı
        stddraw.setPenColor(self.theme.panel_background)
        stddraw.filledRectangle(panel_left, -0.5, panel_width, self.grid_height)
        stddraw.setPenColor(self.theme.panel_divider)
        stddraw.line(panel_left, -0.5, panel_left, self.grid_height - 0.5)

        # SCORE  cy=17.7  → y: 16.4..19.0
        self._draw_stat_card(cx, top_y - 1.8, 'SCORE', str(self.score), 2.6)
        # LINES  cy=14.5  → y: 13.5..15.5
        self._draw_stat_card(cx, top_y - 5.0, 'LINES', str(self.lines_cleared), 2.0)
        # NEXT   cy=11.0  → y: 9.4..12.6   (yukarı kaydırıldı)
        self._draw_preview_box(cx, top_y - 8.5, 'NEXT', self.next_tetromino)
        # HOLD   cy=6.5   → y: 4.9..8.1    (NEXT ile orantılı yukarı)
        self._draw_preview_box(cx, top_y - 13.0, 'HOLD', self.held_tetromino)

        # Kontrol tuşları – HOLD kutusunun altında (4.9'dan aşağı)
        stddraw.setFontFamily('Arial')
        stddraw.setFontSize(10)
        controls = [
            ('← →', 'Move'),
            ('↓',   'Soft drop'),
            ('↑',   'Rotate'),
            ('SPC', 'Hard drop'),
            ('H',   'Hold'),
            ('ESC', 'Pause'),
            ('R',   'Restart'),
            ('T',   'Theme'),
            ('M',   'Music'),
        ]
        start_y  = 3.8      # HOLD kutusunun altından başla
        spacing  = 0.46
        for i, (k, a) in enumerate(controls):
            y = start_y - i * spacing
            stddraw.setPenColor(self.theme.title_text)
            stddraw.text(cx - 1.0, y, k)
            stddraw.setPenColor(self.theme.muted_text)
            stddraw.text(cx + 1.0, y, a)

    def _draw_stat_card(self, cx, cy, label, value, height):
        width = 3.8
        stddraw.setPenColor(self.theme.preview_box)
        stddraw.filledRectangle(cx - width/2, cy - height/2, width, height)
        stddraw.setPenColor(self.theme.panel_divider)
        stddraw.rectangle(cx - width/2, cy - height/2, width, height)
        stddraw.setFontFamily('Arial')
        stddraw.setPenColor(self.theme.secondary_text)
        stddraw.setFontSize(13)
        stddraw.boldText(cx, cy + 0.45, label)
        stddraw.setPenColor(self.theme.title_text)
        stddraw.setFontSize(22)
        stddraw.boldText(cx, cy - 0.35, value)

    def _draw_preview_box(self, cx, cy, label, tetromino):
        width, height = 3.8, 3.2
        left   = cx - width / 2
        bottom = cy - height / 2
        stddraw.setPenColor(self.theme.preview_box)
        stddraw.filledRectangle(left, bottom, width, height)
        stddraw.setPenColor(self.theme.panel_divider)
        stddraw.rectangle(left, bottom, width, height)
        stddraw.setFontFamily('Arial')
        stddraw.setFontSize(13)
        stddraw.setPenColor(self.theme.secondary_text)
        stddraw.boldText(cx, cy + height/2 - 0.38, label)
        if tetromino is not None:
            # İç alan: label için 0.5 üstten, kenarlardan 0.3 padding
            inner_w = width  - 0.6
            inner_h = height - 0.8   # label alanı dahil
            self._draw_preview(tetromino, cx, cy - 0.22, inner_w, inner_h)

    def _draw_preview(self, tetromino, cx, cy, box_w, box_h):
        """
        Tetromino'yu (cx, cy) merkezine, box_w × box_h alana tam sığacak
        şekilde çizer. Hem tile spacing hem de görsel boyut dinamik hesaplanır.
        """
        tiles, _ = tetromino.get_min_bounded_tile_matrix(return_position=False)
        rows, cols = tiles.shape

        # Kaç aralık var?  (1 tile ise aralık=0 → bölme hatasını önle)
        h_gaps = max(rows - 1, 1)
        w_gaps = max(cols - 1, 1)

        # Her yönde sığacak maksimum spacing (tile merkez–merkez mesafesi)
        sp_h = box_h / (rows + 0.4)   # +0.4: kenar padding payı
        sp_w = box_w / (cols + 0.4)
        spacing = min(sp_h, sp_w, 0.85)   # üst sınır: 0.85 grid birimi

        # Görsel tile boyutu = spacing'in %88'i (aralarında nefes payı)
        scale = spacing * 0.88

        # Toplam şeklin kapladığı alan
        total_h = (rows - 1) * spacing
        total_w = (cols - 1) * spacing

        # Sol-alt başlangıç
        start_x = cx - total_w / 2.0
        start_y = cy - total_h / 2.0

        for row in range(rows):
            for col in range(cols):
                tile = tiles[row][col]
                if tile is None:
                    continue
                px = start_x + col * spacing
                py = start_y + (rows - 1 - row) * spacing
                tile.draw(Point(px, py), scale=scale)

    def draw_overlay(self, title, subtitle_lines, title_color):
        from lib.color import Color
        box_w  = 8.8
        box_h  = max(5.8, 2.5 + len(subtitle_lines) * 0.82)
        cx     = (self.grid_width - 1) / 2
        cy     = self.grid_height / 2
        left   = cx - box_w / 2
        bottom = cy - box_h / 2
        stddraw.setPenColor(self.theme.overlay_fill)
        stddraw.filledRectangle(left, bottom, box_w, box_h)
        stddraw.setPenColor(self.theme.boundary)
        stddraw.rectangle(left, bottom, box_w, box_h)
        stddraw.setFontFamily('Arial')
        stddraw.setPenColor(title_color)
        stddraw.setFontSize(28)
        stddraw.boldText(cx, cy + box_h/2 - 1.1, title)
        stddraw.setPenColor(self.theme.title_text)
        stddraw.setFontSize(15)
        line_y = cy + box_h/2 - 2.2
        for i, line in enumerate(subtitle_lines):
            stddraw.text(cx, line_y - i * 0.80, line)

    def is_inside(self, row, col):
        return 0 <= row < self.grid_height and 0 <= col < self.grid_width

    def is_occupied(self, row, col):
        return self.is_inside(row, col) and self.tile_matrix[row][col] is not None

    def update_grid(self, tiles_to_lock, blc_position):
        self.current_tetromino = None
        rows, cols = tiles_to_lock.shape
        for lc in range(cols):
            for lr in range(rows):
                incoming = tiles_to_lock[lr][lc]
                if incoming is None:
                    continue
                tx = blc_position.x + lc
                ty = blc_position.y + (rows - 1) - lr
                if self.is_inside(ty, tx):
                    self.tile_matrix[ty][tx] = incoming
                else:
                    self.game_over = True
        if not self.game_over:
            self.resolve_landed_tiles()
        return self.game_over

    def resolve_landed_tiles(self):
        total = 0
        while True:
            changed = False
            s, ok = self.merge_vertical_chain()
            if ok: total += s; changed = True
            s, ok = self.clear_full_rows()
            if ok: total += s; changed = True
            s, ok = self.remove_free_tiles()
            if ok: total += s; changed = True
            if not changed:
                break
        self.score += total
        return total

    def merge_vertical_chain(self):
        gained, changed = 0, False
        for col in range(self.grid_width):
            row = 0
            while row < self.grid_height - 1:
                lo = self.tile_matrix[row][col]
                hi = self.tile_matrix[row + 1][col]
                if lo is not None and hi is not None and lo.number == hi.number:
                    nv = lo.number * 2
                    lo.set_number(nv)
                    self.tile_matrix[row + 1][col] = None
                    gained  += nv
                    changed  = True
                    if nv >= WIN_VALUE and not self.kept_playing:
                        self.game_won = True
                    self.apply_column_gravity(col)
                else:
                    row += 1
        return gained, changed

    def apply_column_gravity(self, col):
        tiles = [self.tile_matrix[r][col]
                 for r in range(self.grid_height)
                 if self.tile_matrix[r][col] is not None]
        for r in range(self.grid_height):
            self.tile_matrix[r][col] = tiles[r] if r < len(tiles) else None

    def clear_full_rows(self):
        full_rows = [r for r in range(self.grid_height)
                     if all(t is not None for t in self.tile_matrix[r])]
        if not full_rows:
            return 0, False
        gained = sum(t.number for r in full_rows for t in self.tile_matrix[r])
        new_m  = np.full((self.grid_height, self.grid_width), None)
        wr = 0
        for r in range(self.grid_height):
            if r not in full_rows:
                new_m[wr, :] = self.tile_matrix[r].copy()
                wr += 1
        self.tile_matrix   = new_m
        self.lines_cleared += len(full_rows)
        return gained, True

    def remove_free_tiles(self):
        connected = np.full((self.grid_height, self.grid_width), False)
        q = deque()
        for col in range(self.grid_width):
            if self.tile_matrix[0][col] is not None:
                connected[0][col] = True
                q.append((0, col))
        while q:
            r, c = q.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if not self.is_inside(nr, nc) or connected[nr][nc] \
                        or self.tile_matrix[nr][nc] is None:
                    continue
                connected[nr][nc] = True
                q.append((nr, nc))
        gained, removed = 0, False
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                t = self.tile_matrix[r][c]
                if t is not None and not connected[r][c]:
                    gained += t.number
                    self.tile_matrix[r][c] = None
                    removed = True
        return gained, removed
