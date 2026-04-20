"""Standard drawing module for creating graphics with pygame.

The stddraw module defines functions for creating drawings on a canvas
including shapes, text, colors, and interactive input handling.
"""

from __future__ import annotations

import os
import subprocess as _subprocess  # nosec B404
import sys
import time
from typing import TYPE_CHECKING, Any

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox

import pygame
import pygame.font
import pygame.gfxdraw

if TYPE_CHECKING:
	from lib.color import Color
	from lib.picture import Picture

# Define colors so clients need not import the color module
from lib.color import (
	BLACK,
	BLUE,
	CYAN,
	DARK_BLUE,
	DARK_GREEN,
	DARK_RED,
	GREEN,
	MAGENTA,
	ORANGE,
	PINK,
	RED,
	WHITE,
	YELLOW,
)

# -----------------------------------------------------------------------

# Default Sizes and Values

_BORDER = 0.0
# _BORDER = 0.05
_DEFAULT_XMIN = 0.0
_DEFAULT_XMAX = 1.0
_DEFAULT_YMIN = 0.0
_DEFAULT_YMAX = 1.0
_DEFAULT_CANVAS_SIZE = 512
_DEFAULT_PEN_RADIUS = 0.005  # Maybe change this to 0.0 in the future.
_DEFAULT_PEN_COLOR = BLACK

_DEFAULT_FONT_FAMILY = "Helvetica"
_DEFAULT_FONT_SIZE = 12

# Mouse button constants
_RIGHT_MOUSE_BUTTON = 3
_LEFT_MOUSE_BUTTON = 1

_xmin: float = _DEFAULT_XMIN
_ymin: float = _DEFAULT_YMIN
_xmax: float = _DEFAULT_XMAX
_ymax: float = _DEFAULT_YMAX

_fontFamily: str = _DEFAULT_FONT_FAMILY
_fontSize: int = _DEFAULT_FONT_SIZE

_canvasWidth: float = float(_DEFAULT_CANVAS_SIZE)
_canvasHeight: float = float(_DEFAULT_CANVAS_SIZE)
_penRadius: float = _DEFAULT_PEN_RADIUS
_penColor: Color = _DEFAULT_PEN_COLOR
_keysTyped: list[str] = []

# Background and surface for pygame
_background: Any = None
_surface: Any = None

# Has the window been created?
_windowCreated: bool = False

# -----------------------------------------------------------------------
# Begin added by Alan J. Broder
# -----------------------------------------------------------------------

# Keep track of mouse status

# Has the mouse been left-clicked since the last time we checked?
_mousePressed: bool = False

# The position of the mouse as of the most recent mouse click
_mousePos: tuple[int, int] | None = None

# -----------------------------------------------------------------------
# End added by Alan J. Broder
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------


def _pygameColor(c: Color) -> pygame.Color:
	"""Convert `c` (a color.Color) to an equivalent pygame.Color.

	Return the result.
	"""
	r = c.get_red()
	g = c.get_green()
	b = c.get_blue()
	return pygame.Color(r, g, b)


# -----------------------------------------------------------------------

# Private functions to scale and factor X and Y values.


def _scaleX(x: float) -> float:
	"""Scale x coordinate to canvas width."""
	return _canvasWidth * (x - _xmin) / (_xmax - _xmin)


def _scaleY(y: float) -> float:
	"""Scale y coordinate to canvas height."""
	return _canvasHeight * (_ymax - y) / (_ymax - _ymin)


def _factorX(w: float) -> float:
	"""Factor x width to canvas width."""
	return w * _canvasWidth / abs(_xmax - _xmin)


def _factorY(h: float) -> float:
	"""Factor y height to canvas height."""
	return h * _canvasHeight / abs(_ymax - _ymin)


# -----------------------------------------------------------------------
# Begin added by Alan J. Broder
# -----------------------------------------------------------------------


def _userX(x: float) -> float:
	"""Convert canvas x to user coordinates."""
	return _xmin + x * (_xmax - _xmin) / _canvasWidth


def _userY(y: float) -> float:
	"""Convert canvas y to user coordinates."""
	return _ymax - y * (_ymax - _ymin) / _canvasHeight


# -----------------------------------------------------------------------
# End added by Alan J. Broder
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------


def setCanvasSize(w: int = _DEFAULT_CANVAS_SIZE, h: int = _DEFAULT_CANVAS_SIZE) -> None:
	"""Set the size of the canvas to w pixels wide and h pixels high.
	Calling this function is optional. If you call it, you must do
	so before calling any drawing function.
	"""
	global _background  # noqa: PLW0603
	global _surface  # noqa: PLW0603
	global _canvasWidth  # noqa: PLW0603
	global _canvasHeight  # noqa: PLW0603
	global _windowCreated  # noqa: PLW0603

	if _windowCreated:
		msg = "The stddraw window already was created"
		raise Exception(msg)

	if (w < 1) or (h < 1):
		msg = "width and height must be positive"
		raise Exception(msg)

	_canvasWidth = w
	_canvasHeight = h
	_background = pygame.display.set_mode([w, h])
	pygame.display.set_caption("stddraw window (r-click to save)")
	_surface = pygame.Surface((w, h))
	_surface.fill(_pygameColor(WHITE))
	_windowCreated = True


def setXscale(min: float = _DEFAULT_XMIN, max: float = _DEFAULT_XMAX) -> None:
	"""Set the x-scale of the canvas such that the minimum x value
	is min and the maximum x value is max.
	"""
	global _xmin  # noqa: PLW0603
	global _xmax  # noqa: PLW0603
	min = float(min)
	max = float(max)
	if min >= max:
		msg = "min must be less than max"
		raise Exception(msg)
	size = max - min
	_xmin = min - _BORDER * size
	_xmax = max + _BORDER * size


def setYscale(min: float = _DEFAULT_YMIN, max: float = _DEFAULT_YMAX) -> None:
	"""Set the y-scale of the canvas such that the minimum y value
	is min and the maximum y value is max.
	"""
	global _ymin  # noqa: PLW0603
	global _ymax  # noqa: PLW0603
	min = float(min)
	max = float(max)
	if min >= max:
		msg = "min must be less than max"
		raise Exception(msg)
	size = max - min
	_ymin = min - _BORDER * size
	_ymax = max + _BORDER * size


def setPenRadius(r: float = _DEFAULT_PEN_RADIUS) -> None:
	"""Set the pen radius to r, thus affecting the subsequent drawing
	of points and lines. If r is 0.0, then points will be drawn with
	the minimum possible radius and lines with the minimum possible
	width.
	"""
	global _penRadius  # noqa: PLW0603
	r = float(r)
	if r < 0.0:
		msg = "Argument to setPenRadius() must be non-neg"
		raise Exception(msg)
	_penRadius = r * float(_DEFAULT_CANVAS_SIZE)


def setPenColor(c: Color = _DEFAULT_PEN_COLOR) -> None:
	"""Set the pen color to c, where c is an object of class color.Color.
	c defaults to stddraw.BLACK.
	"""
	global _penColor  # noqa: PLW0603
	_penColor = c


def setFontFamily(f: str = _DEFAULT_FONT_FAMILY) -> None:
	"""Set the font family to f (e.g. 'Helvetica' or 'Courier')."""
	global _fontFamily  # noqa: PLW0603
	_fontFamily = f


def setFontSize(s: int = _DEFAULT_FONT_SIZE) -> None:
	"""Set the font size to s (e.g. 12 or 16)."""
	global _fontSize  # noqa: PLW0603
	_fontSize = s


# -----------------------------------------------------------------------


def _makeSureWindowCreated() -> None:
	"""Ensure the pygame window has been created."""
	global _windowCreated  # noqa: PLW0603
	if not _windowCreated:
		setCanvasSize()
		_windowCreated = True


# -----------------------------------------------------------------------

# Functions to draw shapes, text, and images on the background canvas.


def _pixel(x: float, y: float) -> None:
	"""Draw on the background canvas a pixel at (x, y)."""
	_makeSureWindowCreated()
	xs = _scaleX(x)
	xy = _scaleY(y)
	pygame.gfxdraw.pixel(
		_surface,
		round(xs),
		round(xy),
		_pygameColor(_penColor),
	)


def point(x: float, y: float) -> None:
	"""Draw on the background canvas a point at (x, y)."""
	_makeSureWindowCreated()
	x = float(x)
	y = float(y)
	# If the radius is too small, then simply draw a pixel.
	if _penRadius <= 1.0:
		_pixel(x, y)
	else:
		xs = _scaleX(x)
		ys = _scaleY(y)
		pygame.draw.ellipse(
			_surface,
			_pygameColor(_penColor),
			pygame.Rect(
				xs - _penRadius,
				ys - _penRadius,
				_penRadius * 2.0,
				_penRadius * 2.0,
			),
			0,
		)


def line(x0: float, y0: float, x1: float, y1: float) -> None:
	"""Draw on the background canvas a line from (x0, y0) to (x1, y1)."""
	_makeSureWindowCreated()

	x0 = float(x0)
	y0 = float(y0)
	x1 = float(x1)
	y1 = float(y1)

	lineWidth = _penRadius
	if lineWidth == 0.0:
		lineWidth = 1.0
	x0s = _scaleX(x0)
	y0s = _scaleY(y0)
	x1s = _scaleX(x1)
	y1s = _scaleY(y1)
	pygame.draw.line(
		_surface,
		_pygameColor(_penColor),
		(x0s, y0s),
		(x1s, y1s),
		round(lineWidth),
	)


def circle(x: float, y: float, r: float) -> None:
	"""Draw on the background canvas a circle of radius r centered on
	(x, y).
	"""
	_makeSureWindowCreated()
	x = float(x)
	y = float(y)
	r = float(r)
	ws = _factorX(2.0 * r)
	hs = _factorY(2.0 * r)
	# If the radius is too small, then simply draw a pixel.
	if (ws <= 1.0) and (hs <= 1.0):
		_pixel(x, y)
	else:
		xs = _scaleX(x)
		ys = _scaleY(y)
		pygame.draw.ellipse(
			_surface,
			_pygameColor(_penColor),
			pygame.Rect(xs - ws / 2.0, ys - hs / 2.0, ws, hs),
			round(_penRadius),
		)


def filledCircle(x: float, y: float, r: float) -> None:
	"""Draw on the background canvas a filled circle of radius r
	centered on (x, y).
	"""
	_makeSureWindowCreated()
	x = float(x)
	y = float(y)
	r = float(r)
	ws = _factorX(2.0 * r)
	hs = _factorY(2.0 * r)
	# If the radius is too small, then simply draw a pixel.
	if (ws <= 1.0) and (hs <= 1.0):
		_pixel(x, y)
	else:
		xs = _scaleX(x)
		ys = _scaleY(y)
		pygame.draw.ellipse(
			_surface,
			_pygameColor(_penColor),
			pygame.Rect(xs - ws / 2.0, ys - hs / 2.0, ws, hs),
			0,
		)


def rectangle(x: float, y: float, w: float, h: float) -> None:
	"""Draw on the background canvas a rectangle of width w and height h
	whose lower left point is (x, y).
	"""
	global _surface  # noqa: PLW0602
	_makeSureWindowCreated()
	x = float(x)
	y = float(y)
	w = float(w)
	h = float(h)
	ws = _factorX(w)
	hs = _factorY(h)
	# If the rectangle is too small, then simply draw a pixel.
	if (ws <= 1.0) and (hs <= 1.0):
		_pixel(x, y)
	else:
		xs = _scaleX(x)
		ys = _scaleY(y)
		pygame.draw.rect(
			_surface,
			_pygameColor(_penColor),
			pygame.Rect(xs, ys - hs, ws, hs),
			round(_penRadius),
		)


def filledRectangle(x: float, y: float, w: float, h: float) -> None:
	"""Draw on the background canvas a filled rectangle of width w and
	height h whose lower left point is (x, y).
	"""
	global _surface  # noqa: PLW0602
	_makeSureWindowCreated()
	x = float(x)
	y = float(y)
	w = float(w)
	h = float(h)
	ws = _factorX(w)
	hs = _factorY(h)
	# If the rectangle is too small, then simply draw a pixel.
	if (ws <= 1.0) and (hs <= 1.0):
		_pixel(x, y)
	else:
		xs = _scaleX(x)
		ys = _scaleY(y)
		pygame.draw.rect(
			_surface,
			_pygameColor(_penColor),
			pygame.Rect(xs, ys - hs, ws, hs),
			0,
		)


def square(x: float, y: float, r: float) -> None:
	"""Draw on the background canvas a square whose sides are of length
	2r, centered on (x, y).
	"""
	_makeSureWindowCreated()
	rectangle(x - r, y - r, 2.0 * r, 2.0 * r)


def filledSquare(x: float, y: float, r: float) -> None:
	"""Draw on the background canvas a filled square whose sides are of
	length 2r, centered on (x, y).
	"""
	_makeSureWindowCreated()
	filledRectangle(x - r, y - r, 2.0 * r, 2.0 * r)


def polygon(x: list[float], y: list[float]) -> None:
	"""Draw on the background canvas a polygon with coordinates
	(x[i], y[i]).
	"""
	global _surface  # noqa: PLW0602
	_makeSureWindowCreated()
	# Scale X and Y values.
	x_scaled = [_scaleX(float(xi)) for xi in x]
	y_scaled = [_scaleY(float(yi)) for yi in y]
	points = list(zip(x_scaled, y_scaled, strict=True))
	if points:
		points.append(points[0])
	pygame.draw.polygon(
		_surface,
		_pygameColor(_penColor),
		points,
		round(_penRadius),
	)


def filledPolygon(x: list[float], y: list[float]) -> None:
	"""Draw on the background canvas a filled polygon with coordinates
	(x[i], y[i]).
	"""
	global _surface  # noqa: PLW0602
	_makeSureWindowCreated()
	# Scale X and Y values.
	x_scaled = [_scaleX(float(xi)) for xi in x]
	y_scaled = [_scaleY(float(yi)) for yi in y]
	points = list(zip(x_scaled, y_scaled, strict=True))
	if points:
		points.append(points[0])
	pygame.draw.polygon(_surface, _pygameColor(_penColor), points, 0)


def text(x: float, y: float, s: str) -> None:
	"""Draw string s on the background canvas centered at (x, y)."""
	_makeSureWindowCreated()
	x = float(x)
	y = float(y)
	xs = _scaleX(x)
	ys = _scaleY(y)
	font = pygame.font.SysFont(_fontFamily, _fontSize)
	text = font.render(s, 1, _pygameColor(_penColor))
	textpos = text.get_rect(center=(xs, ys))
	_surface.blit(text, textpos)


def boldText(x: float, y: float, s: str) -> None:
	"""Draw string s as a bold text on the background canvas centered at (x, y)."""
	_makeSureWindowCreated()
	x = float(x)
	y = float(y)
	xs = _scaleX(x)
	ys = _scaleY(y)
	font = pygame.font.SysFont(_fontFamily, _fontSize, True)  # noqa: FBT003
	text = font.render(s, 1, _pygameColor(_penColor))
	textpos = text.get_rect(center=(xs, ys))
	_surface.blit(text, textpos)


def picture(pic: Picture, x: float | None = None, y: float | None = None) -> None:
	"""Draw pic on the background canvas centered at (x, y).  pic is an
	object of class picture.Picture. x and y default to the midpoint
	of the background canvas.
	"""
	global _surface  # noqa: PLW0602
	_makeSureWindowCreated()
	# By default, draw pic at the middle of the surface.
	if x is None:
		x = (_xmax + _xmin) / 2.0
	if y is None:
		y = (_ymax + _ymin) / 2.0
	x = float(x)
	y = float(y)
	xs = _scaleX(x)
	ys = _scaleY(y)
	ws = pic.width()
	hs = pic.height()
	picSurface = pic._surface  # violates encapsulation  # noqa: SLF001
	_surface.blit(picSurface, [xs - ws / 2.0, ys - hs / 2.0, ws, hs])


def clear(c: Color = WHITE) -> None:
	"""Clear the background canvas to color c, where c is an
	object of class color.Color. c defaults to stddraw.WHITE.
	"""
	_makeSureWindowCreated()
	_surface.fill(_pygameColor(c))


def save(f: str) -> None:
	"""Save the window canvas to file f."""
	_makeSureWindowCreated()

	# if sys.hexversion >= 0x03000000:
	#    # Pygame without full image support
	#    # can handle only .bmp files.
	#    bmpFileName = f + '.bmp'
	#    pygame.image.save(_surface, bmpFileName)
	#    os.system('convert ' + bmpFileName + ' ' + f)
	#    os.system('rm ' + bmpFileName)
	# else:
	#    pygame.image.save(_surface, f)

	pygame.image.save(_surface, f)


# -----------------------------------------------------------------------


def _show() -> None:
	"""Copy the background canvas to the window canvas."""
	_background.blit(_surface, (0, 0))
	pygame.display.flip()
	_checkForEvents()


def _showAndWaitForever() -> None:
	"""Copy the background canvas to the window canvas. Then wait
	forever, that is, until the user closes the stddraw window.
	"""
	_makeSureWindowCreated()
	_show()
	QUANTUM = 0.1
	while True:
		time.sleep(QUANTUM)
		_checkForEvents()


def show(msec: float | None = None) -> None:
	"""Copy the background canvas to the window canvas, and
	then wait for msec milliseconds. msec defaults to infinity.
	"""
	if msec is None:
		_showAndWaitForever()
		return

	_makeSureWindowCreated()
	_show()
	_checkForEvents()

	# Sleep for the required time, but check for events every
	# QUANTUM seconds.
	QUANTUM = 0.01
	sec = msec / 1000.0
	if sec < QUANTUM:
		time.sleep(sec)
		return
	secondsWaited = 0.0
	while secondsWaited < sec:
		time.sleep(QUANTUM)
		secondsWaited += QUANTUM
		_checkForEvents()


# -----------------------------------------------------------------------


def _saveToFile() -> None:
	"""Display a dialog box that asks the user for a file name.  Save the
	drawing to the specified file.  Display a confirmation dialog box
	if successful, and an error dialog box otherwise.  The dialog boxes
	are displayed using Tkinter, which (on some computers) is
	incompatible with Pygame. So the dialog boxes must be displayed
	from child processes.
	"""
	_makeSureWindowCreated()

	stddrawPath = os.path.realpath(__file__)

	childProcess = _subprocess.Popen(  # nosec B603  # noqa: S603
		[sys.executable, stddrawPath, "getFileName"],
		stdout=_subprocess.PIPE,
	)
	so, _se = childProcess.communicate()
	fileName_raw = so.strip() if so is not None else b""

	# Convert subprocess output to a string in all cases.
	fileName: str
	if isinstance(fileName_raw, memoryview):
		fileName = fileName_raw.tobytes().decode("utf-8")
	elif isinstance(fileName_raw, bytes | bytearray):
		fileName = bytes(fileName_raw).decode("utf-8")
	else:
		fileName = str(fileName_raw)

	if fileName == "":
		return

	if not fileName.endswith((".jpg", ".png")):
		childProcess = _subprocess.Popen(  # nosec B603  # noqa: S603
			[
				sys.executable,
				stddrawPath,
				"reportFileSaveError",
				'File name must end with ".jpg" or ".png".',
			]
		)
		return

	try:
		save(fileName)
		childProcess = _subprocess.Popen(  # nosec B603  # noqa: S603
			[sys.executable, stddrawPath, "confirmFileSave"],
		)
	except pygame.error as e:
		childProcess = _subprocess.Popen(  # nosec B603  # noqa: S603
			[
				sys.executable,
				stddrawPath,
				"reportFileSaveError",
				str(e),
			]
		)


def _checkForEvents() -> None:
	"""Check if any new event has occured (such as a key typed or button
	pressed).  If a key has been typed, then put that key in a queue.
	"""
	global _surface  # noqa: PLW0602
	global _keysTyped  # noqa: PLW0603

	# -------------------------------------------------------------------
	# Begin added by Alan J. Broder
	# -------------------------------------------------------------------
	global _mousePos  # noqa: PLW0603
	global _mousePressed  # noqa: PLW0603
	# -------------------------------------------------------------------
	# End added by Alan J. Broder
	# -------------------------------------------------------------------

	_makeSureWindowCreated()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			_keysTyped = [pygame.key.name(event.key), *_keysTyped]
		elif (event.type == pygame.MOUSEBUTTONUP) and (
			event.button == _RIGHT_MOUSE_BUTTON
		):
			_saveToFile()

		# ---------------------------------------------------------------
		# Begin added by Alan J. Broder
		# ---------------------------------------------------------------
		# Every time the mouse button is pressed, remember
		# the mouse position as of that press.
		elif (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):
			_mousePressed = True
			_mousePos = event.pos
		# ---------------------------------------------------------------
		# End added by Alan J. Broder
		# ---------------------------------------------------------------


# -----------------------------------------------------------------------

# Functions for retrieving keys


def hasNextKeyTyped() -> bool:
	"""Return True if the queue of the keys the user typed is not empty.
	Otherwise return False.
	"""
	global _keysTyped  # noqa: PLW0602
	return _keysTyped != []


def nextKeyTyped() -> str:
	"""Remove the first key from the queue of the keys that the user typed,
	and return that key.
	"""
	global _keysTyped  # noqa: PLW0602
	return _keysTyped.pop()


def clearKeysTyped() -> None:
	"""Clear all the keys in the queue of the keys that the user typed."""
	global _keysTyped  # noqa: PLW0603
	_keysTyped = []


# -----------------------------------------------------------------------
# Begin added by Alan J. Broder
# -----------------------------------------------------------------------

# Functions for dealing with mouse clicks


def mousePressed() -> bool:
	"""Return True if the mouse has been left-clicked since the
	last time mousePressed was called, and False otherwise.
	"""
	global _mousePressed  # noqa: PLW0603
	if _mousePressed:
		_mousePressed = False
		return True
	return False


def mouseX() -> float:
	"""Return the x coordinate in user space of the location at
	which the mouse was most recently left-clicked. If a left-click
	hasn't happened yet, raise an exception, since mouseX() shouldn't
	be called until mousePressed() returns True.
	"""
	global _mousePos  # noqa: PLW0602
	if _mousePos:
		return _userX(_mousePos[0])
	msg = "Can't determine mouse position if a click hasn't happened"
	raise Exception(msg)


def mouseY() -> float:
	"""Return the y coordinate in user space of the location at
	which the mouse was most recently left-clicked. If a left-click
	hasn't happened yet, raise an exception, since mouseY() shouldn't
	be called until mousePressed() returns True.
	"""
	global _mousePos  # noqa: PLW0602
	if _mousePos:
		return _userY(_mousePos[1])
	msg = "Can't determine mouse position if a click hasn't happened"
	raise Exception(msg)


# -----------------------------------------------------------------------
# End added by Alan J. Broder
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------

# Initialize the x scale, the y scale, and the pen radius.

setXscale()
setYscale()
setPenRadius()
pygame.font.init()

# -----------------------------------------------------------------------

# Functions for displaying Tkinter dialog boxes in child processes.


def _getFileName() -> None:
	"""Display a dialog box that asks the user for a file name."""
	root = tk.Tk()
	root.withdraw()
	reply = tkFileDialog.asksaveasfilename(initialdir=".")
	sys.stdout.write(reply)
	sys.stdout.flush()
	sys.exit()


def _confirmFileSave() -> None:
	"""Display a dialog box that confirms a file save operation."""
	root = tk.Tk()
	root.withdraw()
	tkMessageBox.showinfo(
		title="File Save Confirmation",
		message="The drawing was saved to the file.",
	)
	sys.exit()


def _reportFileSaveError(msg: str) -> None:
	"""Display a dialog box that reports a msg.  msg is a string which
	describes an error in a file save operation.
	"""
	root = tk.Tk()
	root.withdraw()
	tkMessageBox.showerror(title="File Save Error", message=msg)
	sys.exit()


# -----------------------------------------------------------------------


def _regressionTest() -> None:  # noqa: PLR0915
	"""Perform regression testing."""
	clear()

	setPenRadius(0.5)
	setPenColor(ORANGE)
	point(0.5, 0.5)
	show(0.0)

	setPenRadius(0.25)
	setPenColor(BLUE)
	point(0.5, 0.5)
	show(0.0)

	setPenRadius(0.02)
	setPenColor(RED)
	point(0.25, 0.25)
	show(0.0)

	setPenRadius(0.01)
	setPenColor(GREEN)
	point(0.25, 0.25)
	show(0.0)

	setPenRadius(0)
	setPenColor(BLACK)
	point(0.25, 0.25)
	show(0.0)

	setPenRadius(0.1)
	setPenColor(RED)
	point(0.75, 0.75)
	show(0.0)

	setPenRadius(0)
	setPenColor(CYAN)
	for i in range(100):
		point(i / 512.0, 0.5)
		point(0.5, i / 512.0)
	show(0.0)

	setPenRadius(0)
	setPenColor(MAGENTA)
	line(0.1, 0.1, 0.3, 0.3)
	line(0.1, 0.2, 0.3, 0.2)
	line(0.2, 0.1, 0.2, 0.3)
	show(0.0)

	setPenRadius(0.05)
	setPenColor(MAGENTA)
	line(0.7, 0.5, 0.8, 0.9)
	show(0.0)

	setPenRadius(0.01)
	setPenColor(YELLOW)
	circle(0.75, 0.25, 0.2)
	show(0.0)

	setPenRadius(0.01)
	setPenColor(YELLOW)
	filledCircle(0.75, 0.25, 0.1)
	show(0.0)

	setPenRadius(0.01)
	setPenColor(PINK)
	rectangle(0.25, 0.75, 0.1, 0.2)
	show(0.0)

	setPenRadius(0.01)
	setPenColor(PINK)
	filledRectangle(0.25, 0.75, 0.05, 0.1)
	show(0.0)

	setPenRadius(0.01)
	setPenColor(DARK_RED)
	square(0.5, 0.5, 0.1)
	show(0.0)

	setPenRadius(0.01)
	setPenColor(DARK_RED)
	filledSquare(0.5, 0.5, 0.05)
	show(0.0)

	setPenRadius(0.01)
	setPenColor(DARK_BLUE)
	polygon([0.4, 0.5, 0.6], [0.7, 0.8, 0.7])
	show(0.0)

	setPenRadius(0.01)
	setPenColor(DARK_GREEN)
	setFontSize(24)
	text(0.2, 0.4, "hello, world")
	show(0.0)

	# import picture as p
	# pic = p.Picture('saveIcon.png')
	# picture(pic, .5, .85)
	# show(0.0)

	# Test handling of mouse and keyboard events.
	setPenColor(BLACK)
	while True:
		if mousePressed():
			filledCircle(mouseX(), mouseY(), 0.02)
		if hasNextKeyTyped():
			pass
		show(0.0)

	# Never get here.
	show()


# -----------------------------------------------------------------------


# Prefixing a function name with an underscore (_) is a Python convention
# used to indicate that the function is intended for internal use only.
def _main() -> None:
	"""Dispatch to a function that does regression testing, or to a
	dialog-box-handling function.
	"""
	import sys  # noqa: PLC0415

	if len(sys.argv) == 1:
		_regressionTest()
	elif sys.argv[1] == "getFileName":
		_getFileName()
	elif sys.argv[1] == "confirmFileSave":
		_confirmFileSave()
	elif sys.argv[1] == "reportFileSaveError":
		_reportFileSaveError(sys.argv[2])


# Call _main() to execute the test code only if this file is run directly.
# When the file is imported as a module, the test code is not executed.
if __name__ == "__main__":
	_main()
