from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class FontGroup():
	def __init__(self, family_name:str, size:int):
		self.family_name = family_name
		self.base_size = size

		# self.bold_font = QFont(family_name+' bold', size)
		self.regmetrics = QFontMetrics(self.reg())
		self.boldmetrics = QFontMetrics(self.bold())

	def reg(self) -> QFont:
		"""
		- Returns the normal-weight, unitalicized form of the
		font.
		"""
		return QFont(self.family_name, pointSize=self.base_size)

	def bold(self) -> QFont:
		"""
		- Returns a 600-weight, unitalicized form of the font.
		"""
		return QFont(self.family_name, pointSize=self.base_size, weight=600)

	def ital(self) -> QFont:
		"""
		- Returns an italicized, normal-weight form of the font.
		"""
		return QFont(self.family_name, pointSize=self.base_size, italic=True)

	def at_weight(self, weight:int) -> QFont:
		"""
		- Returns an unitalicized form of the font at the
		specified weight.
		"""
		return QFont(self.family_name, pointSize=self.base_size, weight=weight)

	def scaled(self, factor:float) -> QFont:
		return QFont(self.family_name, pointSize=round(self.base_size * factor))

	def find_gwidth(self, string, style='regular'):
		"""
		- Attempts to find the graphic width (in pixels) of the
		string passed in.
		"""
		if style == 'regular':
			metrics_style = self.regmetrics
		else:
			metrics_style = self.boldmetrics
		text_width = metrics_style.size(0, str(string)).width()
		return text_width

	def find_gheight(self, string):
		"""
		- Attempts to find the graphic height (in pixels) of the
		string passed in.
		"""
		text_height = self.regmetrics.size(0, str(string)).height()
		return text_height