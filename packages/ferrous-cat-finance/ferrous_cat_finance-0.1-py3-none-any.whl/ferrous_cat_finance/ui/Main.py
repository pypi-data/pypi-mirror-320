from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ui.Common import *
from ui.Reports import *
from ui.Category import *
from ui.Transactions import *

NAV_HEIGHT = 80

class CoreWidget(QWidget):
	def __init__(self):
		super().__init__()

		# @ TODO!: Style all UI-elements like this: "self.setStyleSheet('QWidget { background-color: #0000FF; }')".
		self.setStyleSheet(f"""
			QWidget {{
				font-family: {SETTINGS['main_font']};
				font-size: {SETTINGS['main_font_size']};
			}}""")
		self.layout = QVBoxLayout(self)
		self.mainbox = QWidget()
		self.mainbox.layout = QHBoxLayout(self.mainbox)

		###	NAVIGATION-BAR:	####################################
		self.navrow = QWidget()
		self.navrow.layout = QHBoxLayout(self.navrow)	# Row for the nav-buttons.
		self.navrow.setFixedHeight(NAV_HEIGHT)

		# -	Only the label is added for now; other widgets need
		#	to reference later-defined values.
		self.nav_label = QLabel(tr('Menus:'), self, Qt.WindowType.Widget)
		self.nav_label.setFont(NAV_FONT.reg())

		self.navrow.layout.addWidget(self.nav_label, alignment=Qt.AlignmentFlag.AlignLeft)
		self.layout.addWidget(self.navrow)

		###	MENU-WIDGETS: ######################################
		self.TRANSACTIONS = TransactDisplayer()

		# self.CATEG_OVERVIEW = CategMainWidget()

		self.REPORTS = SearchReportWidget()

		### END-SETUP: #########################################
		# - Menu-Management:
		self.MENUS = (
			self.TRANSACTIONS,
			# self.CATEG_OVERVIEW,
			self.REPORTS)
		self.INITIAL_MENU = self.TRANSACTIONS

		# -	Disable all but the initial menu.
		for menu in self.MENUS:
			self.mainbox.layout.addWidget(menu,alignment=Qt.AlignmentFlag.AlignTop)
			menu.hide()
		self.INITIAL_MENU.show()
		self.displayed_menu = self.INITIAL_MENU

		# - Display the initial menu.
		self.layout.addWidget(self.mainbox)
		self.mainbox.layout.addWidget(self.displayed_menu)


		###	NAV-BUTTONS:
		self.NAV_BUTTONS:list[QPushButton] = []
		for menu in self.MENUS:
			nav_button = QPushButton(text=tr(menu.accessibleName()))
			nav_button.setFont(NAV_FONT.reg())
			nav_button.setAccessibleDescription(menu.accessibleName())
			self.navrow.layout.addWidget(nav_button, alignment=Qt.AlignmentFlag.AlignLeft)
			self.NAV_BUTTONS.append(nav_button)

		self.NAVI = {	# Reads properties of the NAV_BUTTONS to connect() them to the proper functions.
			self.TRANSACTIONS.accessibleName() : self.nav_to_transact,
			# self.CATEG_OVERVIEW.accessibleName() : self.nav_to_categ,
			self.REPORTS.accessibleName() : self.nav_to_report}

		for naver in self.NAV_BUTTONS:
			naver.clicked.connect(self.NAVI[naver.accessibleDescription()])



	@Slot()
	def nav_to_menu(self, destination:QWidget):
		self.displayed_menu.hide()
		destination.show()
		self.displayed_menu = destination

		return

	def nav_to_transact(self):
		self.nav_to_menu(self.TRANSACTIONS)

	def nav_to_report(self):
		self.nav_to_menu(self.REPORTS)

	# def nav_to_categ(self):
	# 	self.nav_to_menu(self.CATEG_OVERVIEW)


class MenuShell(QMainWindow):
	"""
	- MenuShell serves as the top-level container for the
	application, and determines the layout of the GUI's sections.
	"""
	def __init__(self):
		super().__init__(None, Qt.WindowType.Window)
		self.setWindowTitle('Rothe Finance')

		#@! Doing colors properly will take a lot of work!

		self.NAME = 'Shell'
		self.setWindowState(Qt.WindowState.WindowMaximized)

		return

	# def resizeEvent(self):