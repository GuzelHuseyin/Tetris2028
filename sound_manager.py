"""
SoundManager – wraps pygame.mixer for Tetris 2048.

Because stddraw already initialises pygame (display + event),
we MUST NOT call pygame.init() again here.  We only init the
mixer sub-system that stddraw never touches.

If no audio hardware is present (headless server / sandbox),
the class falls back to a silent no-op mode so the game still
runs without errors.
"""

import os


class SoundManager:
    """
    Manages background music and sound effects.

    Attributes
    ----------
    enabled : bool
        Whether audio playback is currently active.
    """

    SOUND_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sounds')

    # Map logical names to file names
    EFFECTS = {
        'move':     'move.wav',
        'rotate':   'rotate.wav',
        'land':     'land.wav',
        'clear':    'clear.wav',
        'merge':    'merge.wav',
        'harddrop': 'harddrop.wav',
        'gameover': 'gameover.wav',
        'win':      'win.wav',
    }
    BGM_FILE = 'bgm.wav'

    def __init__(self, enabled=True):
        self._available = False
        self._sounds = {}
        self._bgm = None
        self.enabled = enabled

        try:
            import pygame
            # Try to initialise mixer; use dummy driver if no hardware
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
                except pygame.error:
                    import os as _os
                    _os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
                    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

            self._pygame = pygame
            self._available = True
            self._load_sounds()
        except Exception:
            # Audio completely unavailable – silent mode
            self._available = False

    def _load_sounds(self):
        """Pre-load all WAV files into memory."""
        for name, fname in self.EFFECTS.items():
            path = os.path.join(self.SOUND_DIR, fname)
            if os.path.isfile(path):
                try:
                    self._sounds[name] = self._pygame.mixer.Sound(path)
                    self._sounds[name].set_volume(0.55)
                except Exception:
                    pass

        bgm_path = os.path.join(self.SOUND_DIR, self.BGM_FILE)
        if os.path.isfile(bgm_path):
            try:
                self._bgm = self._pygame.mixer.Sound(bgm_path)
                self._bgm.set_volume(0.30)
            except Exception:
                pass

    # ──────────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────────

    def play(self, name: str):
        """Play a named sound effect once (non-blocking)."""
        if not self._available or not self.enabled:
            return
        sound = self._sounds.get(name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def start_bgm(self):
        """Start looping background music."""
        if not self._available or not self.enabled or self._bgm is None:
            return
        try:
            self._bgm.play(loops=-1)
        except Exception:
            pass

    def stop_bgm(self):
        """Stop background music."""
        if not self._available or self._bgm is None:
            return
        try:
            self._bgm.stop()
        except Exception:
            pass

    def pause_bgm(self):
        """Pause background music (can be resumed)."""
        if not self._available:
            return
        try:
            self._pygame.mixer.pause()
        except Exception:
            pass

    def resume_bgm(self):
        """Resume paused background music."""
        if not self._available or not self.enabled:
            return
        try:
            self._pygame.mixer.unpause()
        except Exception:
            pass

    def toggle(self):
        """Toggle audio on/off. Returns new state (True = enabled)."""
        self.enabled = not self.enabled
        if self.enabled:
            self.resume_bgm()
        else:
            self.pause_bgm()
        return self.enabled

    def set_enabled(self, state: bool):
        """Explicitly enable or disable audio."""
        if state == self.enabled:
            return
        self.enabled = state
        if self.enabled:
            self.resume_bgm()
        else:
            self.pause_bgm()
