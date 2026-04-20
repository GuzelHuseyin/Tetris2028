"""Picture class for loading and displaying images.

The Picture class represents an image that can be loaded from a file
or created as a blank canvas.
"""

from __future__ import annotations

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from lib.color import Color

# -----------------------------------------------------------------------

_DEFAULT_WIDTH = 512
_DEFAULT_HEIGHT = 512

# -----------------------------------------------------------------------


class Picture:
	"""A Picture object models an image.

	It is initialized such that it has a given width and height and contains
	all black pixels. Subsequently you can load an image from a given JPG
	or PNG file.
	"""

	_surface: pygame.Surface

	def __init__(
		self, arg1: int | str | None = None, arg2: int | None = None
	) -> None:
		"""Create a Picture.

		If both `arg1` and `arg2` are None: create a blank image using
		the default size. If `arg1` is a string and `arg2` is None: load the
		image from the filename. If both `arg1` and `arg2` are ints: create
		a blank image with the given width and height.
		"""
		if (arg1 is None) and (arg2 is None):
			max_w = _DEFAULT_WIDTH
			max_h = _DEFAULT_HEIGHT
			self._surface = pygame.Surface((max_w, max_h))
			self._surface.fill((0, 0, 0))
		elif (arg1 is not None) and (arg2 is None) and isinstance(arg1, str):
			file_name = arg1
			try:
				self._surface = pygame.image.load(file_name)
			except pygame.error as err:
				raise OSError from err
		elif (
			(arg1 is not None)
			and (arg2 is not None)
			and isinstance(arg1, int)
		):
			max_w = arg1
			max_h = arg2
			self._surface = pygame.Surface((max_w, max_h))
			self._surface.fill((0, 0, 0))
		else:
			msg = "Invalid arguments for Picture constructor"
			raise ValueError(msg)

	# -------------------------------------------------------------------

	def save(self, f: str) -> None:
		"""Save self to the file whose name is f."""
		pygame.image.save(self._surface, f)

	# -------------------------------------------------------------------

	def width(self) -> int:
		"""Return the width of self."""
		return int(self._surface.get_width())

	# -------------------------------------------------------------------

	def height(self) -> int:
		"""Return the height of self."""
		return int(self._surface.get_height())

	# -------------------------------------------------------------------

	def get(self, x: int, y: int) -> Color:
		"""Return the color of self at location (x, y)."""
		pygame_color = self._surface.get_at((x, y))
		return Color(pygame_color.r, pygame_color.g, pygame_color.b)

	# -------------------------------------------------------------------

	def set(self, x: int, y: int, c: Color) -> None:
		"""Set the color of self at location (x, y) to `c`."""
		pygame_color = pygame.Color(c.get_red(), c.get_green(), c.get_blue(), 0)
		self._surface.set_at((x, y), pygame_color)
