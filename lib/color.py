"""Color class for RGB color representation.

The Color class represents an RGB color and provides standard color constants.
"""

class Color:
	"""An RGB color object.

	Attributes:
		r (int): The red component (0-255).
		g (int): The green component (0-255).
		b (int): The blue component (0-255).
	"""

	_r: int
	_g: int
	_b: int

	def __init__(self, r: int = 0, g: int = 0, b: int = 0) -> None:
		"""Initialize a Color with RGB components.

		Args:
			r: Red component (0-255). Defaults to 0.
			g: Green component (0-255). Defaults to 0.
			b: Blue component (0-255). Defaults to 0.
		"""
		self._r = r
		self._g = g
		self._b = b

	def get_red(self) -> int:
		"""Return the red component of this color."""
		return self._r

	def get_green(self) -> int:
		"""Return the green component of this color."""
		return self._g

	def get_blue(self) -> int:
		"""Return the blue component of this color."""
		return self._b

	def __str__(self) -> str:
		"""Return the string representation of this color.

		Returns:
			A string in the format '(r, g, b)'.
		"""
		return f"({self._r}, {self._g}, {self._b})"

	def __repr__(self) -> str:
		"""Return the representation of this color.

		Returns:
			A string representation suitable for debugging.
		"""
		return f"Color({self._r}, {self._g}, {self._b})"


# Standard color constants
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)

RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)

CYAN = Color(0, 255, 255)
MAGENTA = Color(255, 0, 255)
YELLOW = Color(255, 255, 0)

DARK_RED = Color(128, 0, 0)
DARK_GREEN = Color(0, 128, 0)
DARK_BLUE = Color(0, 0, 128)

GRAY = Color(128, 128, 128)
DARK_GRAY = Color(64, 64, 64)
LIGHT_GRAY = Color(192, 192, 192)

ORANGE = Color(255, 200, 0)
VIOLET = Color(238, 130, 238)
PINK = Color(255, 175, 175)

# Shade of blue used in Introduction to Programming in Java
BOOK_BLUE = Color(9, 90, 166)
BOOK_LIGHT_BLUE = Color(103, 198, 243)

# Shade of red used in Algorithms 4th edition
BOOK_RED = Color(150, 35, 31)
