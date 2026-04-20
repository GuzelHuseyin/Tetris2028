from lib.color import Color


class Theme:
    def __init__(self, name='Classic Dark'):
        self.name = name
        # defaults (Classic Dark)
        self.background      = Color(34, 45, 60)
        self.grid_background = Color(48, 61, 79)
        self.panel_background= Color(40, 50, 64)
        self.grid_line       = Color(74, 90, 112)
        self.boundary        = Color(114, 144, 179)
        self.panel_divider   = Color(88, 104, 126)
        self.title_text      = Color(240, 244, 248)
        self.secondary_text  = Color(201, 210, 221)
        self.muted_text      = Color(168, 178, 191)
        self.button_fill     = Color(72, 201, 176)
        self.button_text     = Color(24, 36, 48)
        self.overlay_fill    = Color(22, 30, 42)
        self.preview_box     = Color(56, 68, 84)
        self.ghost_border    = Color(185, 193, 202)


def _make(name, bg, gbg, pbg, gl, bd, pd, tt, st, mt, bf, bt, of, pb, gb):
    t = Theme(name)
    t.background      = bg
    t.grid_background = gbg
    t.panel_background= pbg
    t.grid_line       = gl
    t.boundary        = bd
    t.panel_divider   = pd
    t.title_text      = tt
    t.secondary_text  = st
    t.muted_text      = mt
    t.button_fill     = bf
    t.button_text     = bt
    t.overlay_fill    = of
    t.preview_box     = pb
    t.ghost_border    = gb
    return t


DEFAULT_THEME = Theme('Classic Dark')

THEME_MIDNIGHT = _make(
    'Midnight Purple',
    Color(18,14,32), Color(30,22,50), Color(24,18,42),
    Color(58,42,90), Color(130,90,200), Color(80,55,130),
    Color(235,220,255), Color(190,170,230), Color(150,130,190),
    Color(150,80,220), Color(255,245,255), Color(14,10,26),
    Color(42,30,70), Color(180,150,220),
)

THEME_FOREST = _make(
    'Forest Green',
    Color(15,30,20), Color(22,44,28), Color(18,36,22),
    Color(40,80,50), Color(80,160,100), Color(50,110,65),
    Color(220,255,225), Color(170,220,180), Color(130,180,140),
    Color(60,200,100), Color(10,30,15), Color(10,20,14),
    Color(30,60,38), Color(150,210,160),
)

THEME_SUNSET = _make(
    'Sunset Orange',
    Color(30,15,10), Color(48,24,14), Color(38,20,10),
    Color(90,45,20), Color(220,120,50), Color(160,80,30),
    Color(255,240,220), Color(255,210,170), Color(220,170,130),
    Color(240,120,40), Color(30,12,5), Color(20,10,5),
    Color(60,32,18), Color(240,180,130),
)

THEME_ICE = _make(
    'Arctic Ice',
    Color(210,230,245), Color(225,240,252), Color(215,232,248),
    Color(170,200,225), Color(90,140,190), Color(140,175,210),
    Color(20,50,90), Color(40,80,130), Color(80,120,160),
    Color(60,140,210), Color(240,248,255), Color(180,210,235),
    Color(195,218,240), Color(100,150,200),
)

ALL_THEMES = [DEFAULT_THEME, THEME_MIDNIGHT, THEME_FOREST, THEME_SUNSET, THEME_ICE]
