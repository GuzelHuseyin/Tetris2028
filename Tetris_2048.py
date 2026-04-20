import os
import random
import time

import lib.stddraw as stddraw
from lib.color import Color

from game_grid import GameGrid
from tetromino import Tetromino
from theme import ALL_THEMES, DEFAULT_THEME
from sound_manager import SoundManager

GRID_HEIGHT     = 20
GRID_WIDTH      = 12
CELL_SIZE       = 36
PANEL_UNITS     = 5
TETROMINO_TYPES = ['I', 'O', 'Z', 'S', 'T', 'L', 'J']

BASE_FALL_DELAY = 0.48
MIN_FALL_DELAY  = 0.10
SPEED_STEP      = 0.03
SPEED_THRESHOLD = 250
TARGET_FPS      = 60


def create_tetromino():
    return Tetromino(random.choice(TETROMINO_TYPES))


def current_fall_delay(score):
    return max(MIN_FALL_DELAY,
               BASE_FALL_DELAY - (score // SPEED_THRESHOLD) * SPEED_STEP)


def draw_button(cx, cy, w, h, fill, label, text_color):
    stddraw.setPenColor(fill)
    stddraw.filledRectangle(cx - w/2, cy - h/2, w, h)
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.rectangle(cx - w/2, cy - h/2, w, h)
    stddraw.setFontFamily('Arial')
    stddraw.setFontSize(22)
    stddraw.setPenColor(text_color)
    stddraw.boldText(cx, cy, label)


# ══════════════════════════════════════════════════════════════════════════
#  MENÜ HERO BÖLÜMÜ
#  Üst: "TETRIS" harfleri tetromino bloklarıyla
#  Alt: 7 renkli mini tetromino sırası  +  2048 rozeti
# ══════════════════════════════════════════════════════════════════════════

# Her harf: 4 sütun × 5 satır ızgarasında (col, row), row=0 alt
_LETTER_CELLS = {
    'T': [(0,4),(1,4),(2,4),(3,4),
                (1,3),
                (1,2),
                (1,1),
                (1,0)],
    'E': [(0,4),(1,4),(2,4),(3,4),
          (0,3),
          (0,2),(1,2),(2,2),
          (0,1),
          (0,0),(1,0),(2,0),(3,0)],
    'R': [(0,4),(1,4),(2,4),(3,4),
          (0,3),      (3,3),
          (0,2),(1,2),(2,2),
          (0,1),      (2,1),
          (0,0),            (3,0)],
    'I': [(0,4),(1,4),(2,4),
                (1,3),
                (1,2),
                (1,1),
          (0,0),(1,0),(2,0)],
    'S': [(0,4),(1,4),(2,4),(3,4),
          (0,3),
          (0,2),(1,2),(2,2),(3,2),
                            (3,1),
          (0,0),(1,0),(2,0),(3,0)],
}

# Renk: her harfe farklı tetromino rengi
_LETTER_COLORS = [
    Color(32, 178, 210),   # T – cyan (I-piece)
    Color(240, 140,  40),  # E – orange (L-piece)
    Color(146,  56, 200),  # T – purple (T-piece)
    Color( 60, 190,  60),  # R – green  (S-piece)
    Color(210,  50,  50),  # I – red    (Z-piece)
    Color( 50,  80, 200),  # S – blue   (J-piece)
]

# 7 mini tetromino için şekil ve renkler (sıra: T I O L J S Z)
_MINI_SHAPES = {
    'T': [(0,1),(1,1),(2,1),(1,2)],
    'I': [(0,0),(1,0),(2,0),(3,0)],
    'O': [(0,0),(1,0),(0,1),(1,1)],
    'L': [(0,0),(0,1),(0,2),(1,0)],
    'J': [(1,0),(1,1),(1,2),(0,0)],
    'S': [(1,0),(2,0),(0,1),(1,1)],
    'Z': [(0,0),(1,0),(1,1),(2,1)],
}
_MINI_COLORS = {
    'T': Color(146,  56, 200),
    'I': Color( 32, 178, 210),
    'O': Color(210, 180,  30),
    'L': Color(240, 140,  40),
    'J': Color( 50,  80, 200),
    'S': Color( 60, 190,  60),
    'Z': Color(210,  50,  50),
}


def _draw_pixel_letter(cells, color, origin_x, origin_y, block_sz):
    """
    cells    : (col, row) listesi, row=0 en alt
    origin_x : sol-alt köşenin x koordinatı
    origin_y : sol-alt köşenin y koordinatı
    block_sz : her bloğun yan boyutu (grid birimi)
    """
    br = min(255, color._r + 45)
    bg = min(255, color._g + 45)
    bb = min(255, color._b + 45)
    border = Color(br, bg, bb)
    half   = block_sz * 0.46
    for (c, r) in cells:
        px = origin_x + c * block_sz
        py = origin_y + r * block_sz
        stddraw.setPenColor(color)
        stddraw.filledSquare(px, py, half)
        stddraw.setPenColor(border)
        stddraw.setPenRadius(0.002)
        stddraw.square(px, py, half)
        stddraw.setPenRadius()


def _draw_mini_piece(key, cx, cy, sz):
    """Mini tetromino: (col,row) → merkez cx,cy, tile half-size sz."""
    cells  = _MINI_SHAPES[key]
    max_c  = max(c for c, r in cells)
    max_r  = max(r for c, r in cells)
    ox     = cx - (max_c / 2.0) * sz * 2
    oy     = cy - (max_r / 2.0) * sz * 2
    col    = _MINI_COLORS[key]
    br     = min(255, col._r + 50)
    bg_c   = min(255, col._g + 50)
    bb     = min(255, col._b + 50)
    border = Color(br, bg_c, bb)
    for (c, r) in cells:
        px = ox + c * sz * 2
        py = oy + r * sz * 2
        stddraw.setPenColor(col)
        stddraw.filledSquare(px, py, sz * 0.90)
        stddraw.setPenColor(border)
        stddraw.setPenRadius(0.002)
        stddraw.square(px, py, sz * 0.90)
        stddraw.setPenRadius()


def draw_menu_hero(cx, top_y, theme):
    """
    top_y: 'TETRIS' harflerinin üst kenarının y koordinatı.

    Düzen (yukarıdan aşağıya):
      TETRIS  (piksel harfler, tetromino bloklarıyla)
      ─ ince çizgi ─
      7 mini tetromino sırası
      2048 rozeti
    """
    BLOCK   = 0.38    # piksel-harf blok boyutu (grid birimi)
    LETTER_H = 5      # harf yüksekliği (row sayısı)
    LETTER_W = 4      # harf genişliği  (col sayısı)
    GAP     = 0.55    # harfler arası boşluk

    letters = ['T', 'E', 'T', 'R', 'I', 'S']
    n_let   = len(letters)
    # Toplam genişlik: n_let harfin genişliği + aralarındaki boşluklar
    total_letter_w = n_let * (LETTER_W * BLOCK) + (n_let - 1) * GAP
    start_x = cx - total_letter_w / 2

    # Harflerin alt kenarı = top_y - LETTER_H*BLOCK
    letter_base_y = top_y - LETTER_H * BLOCK

    for i, ch in enumerate(letters):
        lx = start_x + i * (LETTER_W * BLOCK + GAP)
        _draw_pixel_letter(_LETTER_CELLS[ch], _LETTER_COLORS[i],
                           lx, letter_base_y, BLOCK)

    # İnce çizgi harflerin altında
    line_y = letter_base_y - 0.4
    stddraw.setPenColor(theme.panel_divider)
    stddraw.setPenRadius(0.003)
    stddraw.line(cx - 7.5, line_y, cx + 7.5, line_y)
    stddraw.setPenRadius()

    # 2048 rozeti
    badge_y = line_y - 0.85
    stddraw.setPenColor(Color(232, 110, 100))
    stddraw.filledRectangle(cx - 1.4, badge_y - 0.52, 2.8, 1.04)
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.setFontFamily('Arial')
    stddraw.setFontSize(26)
    stddraw.boldText(cx, badge_y, '2048')


def draw_theme_swatches(cx, base_y, themes, current_idx, theme):
    n       = len(themes)
    spacing = 1.3
    start_x = cx - (n - 1) * spacing / 2
    stddraw.setFontFamily('Arial')
    stddraw.setFontSize(12)
    stddraw.setPenColor(theme.secondary_text)
    stddraw.text(cx, base_y + 0.72, 'THEME  ( T )')
    for i, t in enumerate(themes):
        x        = start_x + i * spacing
        selected = (i == current_idx)
        if selected:
            stddraw.setPenColor(Color(255, 255, 255))
            stddraw.filledSquare(x, base_y, 0.46)
        stddraw.setPenColor(t.button_fill)
        stddraw.filledSquare(x, base_y, 0.38)
        stddraw.setPenColor(Color(255,255,255) if selected else theme.panel_divider)
        stddraw.setPenRadius(0.005 if selected else 0.002)
        stddraw.square(x, base_y, 0.38)
        stddraw.setPenRadius()
        stddraw.setPenColor(t.button_text)
        stddraw.setFontSize(10)
        stddraw.boldText(x, base_y, t.name[0])
        if selected:
            stddraw.setPenColor(theme.secondary_text)
            stddraw.setFontSize(9)
            stddraw.text(x, base_y - 0.60, t.name.split()[0])


# ══════════════════════════════════════════════════════════════════════════
#  MENÜ EKRANI
# ══════════════════════════════════════════════════════════════════════════

def display_game_menu(full_width, grid_height, themes, current_theme_idx, sound):
    cx = (full_width - 1) / 2   # = 8.0

    # Sabit Y koordinatları (canvas 0…19.5)
    Y_TITLE     = 18.5
    Y_SUBTITLE  = 17.55
    # Hero: TETRIS harfleri üst kenarı
    # letter_base_y = 16.0 - 5*0.38 = 14.1
    # line_y = 13.7,  badge_y = 12.85,  badge_bottom = 12.33
    Y_HERO_TOP   = 16.0
    # Kontrol kutusu — 2048 rozetinin altında (12.33 - 0.65 boşluk)
    Y_CTRL_TOP   = 11.68
    Y_CTRL_BOX_H = 3.2
    # Tema seçici
    Y_SWATCH     = Y_CTRL_TOP - Y_CTRL_BOX_H - 0.9
    # Müzik
    Y_MUSIC      = Y_SWATCH - 1.1
    # Buton
    Y_BTN        = max(1.0, Y_MUSIC - 1.35)

    while True:
        theme = themes[current_theme_idx]
        stddraw.clear(theme.background)

        # Başlık
        stddraw.setFontFamily('Arial')
        stddraw.setFontSize(42)
        stddraw.setPenColor(theme.title_text)
        stddraw.boldText(cx, Y_TITLE, 'TETRIS 2048')
        stddraw.setFontSize(14)
        stddraw.setPenColor(theme.secondary_text)
        stddraw.text(cx, Y_SUBTITLE, 'Merge tiles  •  Clear lines  •  Reach 2048!')

        # Hero (TETRIS yazısı + mini piyesler + 2048)
        draw_menu_hero(cx, Y_HERO_TOP, theme)

        # Kontrol kutusu
        box_w = 14.0
        stddraw.setPenColor(theme.preview_box)
        stddraw.filledRectangle(cx - box_w/2, Y_CTRL_TOP - Y_CTRL_BOX_H,
                                box_w, Y_CTRL_BOX_H)
        stddraw.setPenColor(theme.panel_divider)
        stddraw.rectangle(cx - box_w/2, Y_CTRL_TOP - Y_CTRL_BOX_H,
                          box_w, Y_CTRL_BOX_H)

        stddraw.setFontFamily('Arial')
        stddraw.setFontSize(13)
        col_l = cx - 3.5
        col_r = cx + 3.5
        rows_data = [
            ('← →', 'Move left / right',  'ESC',   'Pause / resume'),
            ('↓',   'Soft drop (+score)', 'R',     'Restart game'),
            ('↑',   'Rotate piece',        'H',     'Hold piece'),
            ('SPC', 'Hard drop (+score)', 'T / M', 'Theme / Music'),
        ]
        for idx, (lk, la, rk, ra) in enumerate(rows_data):
            y = Y_CTRL_TOP - 0.55 - idx * 0.72
            stddraw.setPenColor(theme.title_text)
            stddraw.boldText(col_l - 1.2, y, lk)
            stddraw.setPenColor(theme.muted_text)
            stddraw.text(col_l + 0.9, y, la)
            stddraw.setPenColor(theme.title_text)
            stddraw.boldText(col_r - 0.5, y, rk)
            stddraw.setPenColor(theme.muted_text)
            stddraw.text(col_r + 1.5, y, ra)

        # Tema seçici
        draw_theme_swatches(cx, Y_SWATCH, themes, current_theme_idx, theme)

        # Müzik
        music_label = '\u266a  Music: ON   [ M ]' if sound.enabled \
                      else '\u266a  Music: OFF  [ M ]'
        stddraw.setFontFamily('Arial')
        stddraw.setFontSize(13)
        stddraw.setPenColor(theme.button_fill if sound.enabled else theme.muted_text)
        stddraw.boldText(cx, Y_MUSIC, music_label)

        # Buton
        draw_button(cx, Y_BTN, 10.0, 1.55,
                    theme.button_fill, 'Start Game', theme.button_text)

        stddraw.show(int(1000 / TARGET_FPS))

        # Klavye
        while stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            if key in ('enter', 'return', 'space'):
                stddraw.clearKeysTyped()
                return current_theme_idx
            elif key == 't':
                current_theme_idx = (current_theme_idx + 1) % len(themes)
            elif key == 'm':
                sound.toggle()

        # Fare
        if stddraw.mousePressed():
            mx, my = stddraw.mouseX(), stddraw.mouseY()
            if (cx - 5.0 <= mx <= cx + 5.0 and
                    Y_BTN - 0.775 <= my <= Y_BTN + 0.775):
                return current_theme_idx
            n       = len(themes)
            spacing = 1.3
            sx0     = cx - (n-1)*spacing/2
            for i in range(n):
                sx = sx0 + i * spacing
                if abs(mx - sx) <= 0.42 and abs(my - Y_SWATCH) <= 0.42:
                    current_theme_idx = i
            if abs(mx - cx) <= 3.5 and abs(my - Y_MUSIC) <= 0.42:
                sound.toggle()


# ══════════════════════════════════════════════════════════════════════════
#  OVERLAY
# ══════════════════════════════════════════════════════════════════════════

def build_overlay(grid, current_tetromino, title, lines, title_color):
    stddraw.clear(grid.theme.background)
    grid.draw_grid()
    if current_tetromino is not None:
        current_tetromino.draw_ghost(grid)
        current_tetromino.draw()
    grid.draw_boundaries()
    grid.draw_ui()
    grid.draw_overlay(title, lines, title_color)
    stddraw.show(int(1000 / TARGET_FPS))


# ══════════════════════════════════════════════════════════════════════════
#  OYUN BAŞLATMA
# ══════════════════════════════════════════════════════════════════════════

def init_game(theme):
    grid              = GameGrid(GRID_HEIGHT, GRID_WIDTH, theme=theme)
    current_tetromino = create_tetromino()
    next_tetromino    = create_tetromino()
    grid.current_tetromino = current_tetromino
    grid.next_tetromino    = next_tetromino
    return grid, current_tetromino, next_tetromino


def lock_and_spawn(grid, cur, nxt, sound):
    tiles, position = cur.get_min_bounded_tile_matrix(return_position=True)
    score_before    = grid.score
    lines_before    = grid.lines_cleared
    game_over       = grid.update_grid(tiles, position)

    if game_over:
        sound.stop_bgm()
        sound.play('gameover')
        return cur, nxt, True

    if grid.lines_cleared > lines_before:
        sound.play('clear')
    elif grid.score > score_before:
        sound.play('merge')
    else:
        sound.play('land')

    if grid.game_won and not grid.kept_playing:
        sound.stop_bgm()
        sound.play('win')

    new_cur                = nxt
    new_nxt                = create_tetromino()
    grid.current_tetromino = new_cur
    grid.next_tetromino    = new_nxt
    grid.hold_used         = False
    return new_cur, new_nxt, False


def do_hold(grid, cur, nxt, sound):
    """H tuşu: mevcut parçayı hold'a koy, hold'daki parçayla yer değiştir."""
    if grid.hold_used:
        return cur, nxt
    sound.play('rotate')
    grid.hold_used = True

    if grid.held_tetromino is None:
        grid.held_tetromino    = Tetromino(cur.type)
        new_cur                = nxt
        new_nxt                = create_tetromino()
        grid.next_tetromino    = new_nxt
    else:
        old_type               = cur.type
        new_cur                = Tetromino(grid.held_tetromino.type)
        grid.held_tetromino    = Tetromino(old_type)
        new_nxt                = nxt

    new_cur.reset_position(randomize=False)
    grid.current_tetromino = new_cur
    return new_cur, new_nxt


# ══════════════════════════════════════════════════════════════════════════
#  ANA DÖNGÜ
# ══════════════════════════════════════════════════════════════════════════

def main():
    canvas_width  = CELL_SIZE * (GRID_WIDTH + PANEL_UNITS)
    canvas_height = CELL_SIZE * GRID_HEIGHT
    stddraw.setCanvasSize(canvas_width, canvas_height)
    stddraw.setXscale(-0.5, GRID_WIDTH + PANEL_UNITS - 0.5)
    stddraw.setYscale(-0.5, GRID_HEIGHT - 0.5)

    Tetromino.grid_height = GRID_HEIGHT
    Tetromino.grid_width  = GRID_WIDTH

    sound     = SoundManager(enabled=True)
    themes    = ALL_THEMES
    theme_idx = 0

    theme_idx = display_game_menu(GRID_WIDTH + PANEL_UNITS, GRID_HEIGHT,
                                   themes, theme_idx, sound)
    theme = themes[theme_idx]
    sound.start_bgm()

    grid, cur, nxt   = init_game(theme)
    paused           = False
    previous_time    = time.time()
    fall_accumulator = 0.0

    while True:
        now   = time.time()
        delta = now - previous_time
        previous_time = now

        while stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()

            # Her zaman aktif
            if key == 'r':
                grid, cur, nxt = init_game(theme)
                paused = False; fall_accumulator = 0.0
                sound.stop_bgm(); sound.start_bgm()
                continue
            if key == 't':
                theme_idx  = (theme_idx + 1) % len(themes)
                theme      = themes[theme_idx]
                grid.theme = theme
                continue
            if key == 'm':
                sound.toggle()
                continue

            if grid.game_over:
                continue

            if grid.game_won and not grid.kept_playing:
                if key == 'c':
                    grid.kept_playing = True
                    grid.game_won     = False
                    sound.start_bgm()
                continue

            if key == 'escape':
                paused = not paused
                if paused: sound.pause_bgm()
                else:      sound.resume_bgm()
                continue

            if paused:
                continue

            # Oyun tuşları
            if key == 'left':
                if cur.move('left', grid): sound.play('move')
            elif key == 'right':
                if cur.move('right', grid): sound.play('move')
            elif key == 'down':
                if not cur.move('down', grid):
                    cur, nxt, go = lock_and_spawn(grid, cur, nxt, sound)
                    if go: grid.game_over = True
                else:
                    grid.score += 1
            elif key == 'up':
                if cur.rotate(grid): sound.play('rotate')
            elif key == 'space':
                dist = cur.hard_drop_distance(grid)
                sound.play('harddrop')
                for _ in range(dist): cur.move('down', grid)
                grid.score += dist * 2
                cur, nxt, go = lock_and_spawn(grid, cur, nxt, sound)
                if go: grid.game_over = True
            elif key == 'h':
                cur, nxt = do_hold(grid, cur, nxt, sound)

        stddraw.clearKeysTyped()

        # Otomatik düşüş
        if not paused and not grid.game_over \
                and not (grid.game_won and not grid.kept_playing):
            fall_accumulator += delta
            delay = current_fall_delay(grid.score)
            while fall_accumulator >= delay:
                fall_accumulator -= delay
                if not cur.move('down', grid):
                    cur, nxt, go = lock_and_spawn(grid, cur, nxt, sound)
                    if go: grid.game_over = True
                    break

        # Render
        if grid.game_over:
            build_overlay(grid, None, 'GAME OVER',
                          [f'Final Score : {grid.score}',
                           f'Lines Cleared: {grid.lines_cleared}',
                           '', 'Press R to restart'],
                          Color(255, 92, 92))
        elif grid.game_won and not grid.kept_playing:
            build_overlay(grid, cur, 'YOU WIN!',
                          [f'Score : {grid.score}',
                           f'Lines : {grid.lines_cleared}',
                           '', 'Press C to continue', 'Press R to restart'],
                          Color(255, 220, 80))
        elif paused:
            music_line = '[ M ]  Music: ON ' if sound.enabled \
                         else '[ M ]  Music: OFF'
            build_overlay(grid, cur, 'PAUSED',
                          [f'Score : {grid.score}', f'Theme : {theme.name}',
                           '', '[ ESC ]  Resume', '[ T ]    Next Theme',
                           music_line, '[ R ]    Restart'],
                          Color(255, 255, 255))
        else:
            grid.display(0)
            time.sleep(max(0.0, (1.0 / TARGET_FPS) - (time.time() - now)))


if __name__ == '__main__':
    main()
