from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from storage.Database import *
from ui.Font import *
from storage.CategoryTable import CategoryTable, Category
from storage.SecondPartyTable import SecondPartyTable, SecondParty
from storage.TransactionTable import TransactionTable, Transaction
from storage.ledger_table import LedgerTable, Ledger


def get_screen_dimensions():
	measureapp = QGuiApplication()
	stats = (measureapp.primaryScreen().size().width(), measureapp.primaryScreen().size().height())
	measureapp.shutdown()
	return stats

SCREEN_X, SCREEN_Y = get_screen_dimensions()

DATA_FONT = FontGroup(SETTINGS['main_font'], SETTINGS['main_font_size'])
NAV_FONT = FontGroup(SETTINGS['head_font'], SETTINGS['head_font_size'])

CONTENTS_MINWIDTH = 1200
SIDECOLUMN_WIDTH = 300
CONTENTS_MINHEIGHT = 960
METRICS_SIZE_ADJUST = 1.15

QENV = SQL_Connection()	# 'QENV' for 'Query-ENVironment'. Pronounced as "ˈkɛnv".

MONTH_NOTATION = {
	'01' : 'Jan',	1  : 'Jan',
	'02' : 'Feb',	2  : 'Feb',
	'03' : 'Mar',	3  : 'Mar',
	'04' : 'Apr',	4  : 'Apr',
	'05' : 'May',	5  : 'May',
	'06' : 'Jun',	6  : 'Jun',
	'07' : 'Jul',	7  : 'Jul',
	'08' : 'Aug',	8  : 'Aug',
	'09' : 'Sep',	9  : 'Sep',
	'10' : 'Oct',	10 : 'Oct',
	'11' : 'Nov',	11 : 'Nov',
	'12' : 'Dec',	12 : 'Dec'}

MONTH_DECODER = {val:key for key,val in MONTH_NOTATION.items() if type(key) == str}

def format_date(date:str):
	datepieces = date.split('-')
	date = f"{datepieces[0]}-{MONTH_DECODER[datepieces[1]]}-{datepieces[2]}"
	return date

def decode_date(date:str):
	datepieces = date.split('-')
	date = f"{datepieces[0]}-{MONTH_DECODER[datepieces[1]]}-{datepieces[2]}"
	return date

tr = QCoreApplication.tr

MINORWIDGET_LINEHEIGHT = 30

def format_linewidget(widget:QWidget):
	widget.setFont(DATA_FONT.reg())
	widget.setFixedHeight(MINORWIDGET_LINEHEIGHT)

def format_headLinewidget(widget:QWidget):
	widget.setFont(DATA_FONT.bold())
	widget.setFixedHeight(MINORWIDGET_LINEHEIGHT)


class BalChangeGroup(QWidget):
	def __init__(self,
		operator: typ.Literal['+','-','='],
		# avail_space: int,
		parent: typ.Optional[QWidget]=None,
		value: typ.Optional[float]=None,
		editable = False):

		super().__init__(parent)

		# self.setMinimumWidth(avail_space)

		if operator == '-':
			operator = '\u2212'	# Replace the ASCII hyphen-minus with the actually-tabulated minus-symbol.
		self.shape = QHBoxLayout(self)
		self.operator_symbol = QLabel(operator, self)
		self.shape.addWidget(self.operator_symbol, alignment=Qt.AlignmentFlag.AlignVCenter)

		self.value_area = QLabel(self)
		self.shape.addWidget(self.value_area)
		if value != None:
			fval = f'{value:,.2f}'
			fval = fval.replace('-','')	# Remove duplicate negative symbol from expenses.
			if SETTINGS['do_alt_power_sep']:	# If user has left on my preferred way of separating powers of 3:
				fval = fval.replace(',',"'")
			self.value_area.setText(fval)
		else:
			self.value_area.setText('')

		# -	Doing widget-formatting.
		self.value_area.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
		self.value_area.setMinimumWidth(DATA_FONT.find_gwidth("0'000.00"))
		self.value_area.setMaximumWidth(DATA_FONT.find_gwidth("000'000'000.00"))
		self.value_area.setFont(DATA_FONT.reg())
		self.operator_symbol.setFont(DATA_FONT.reg())

		self.setMinimumHeight(DATA_FONT.regmetrics.lineSpacing()*1.1)

		# self.value_area.setReadOnly(not editable)

		return

class BalChangeLabel(QLabel):
	def __init__(operator:typ.Literal['+','-','='], parent:QWidget=None, value:str=''):
		super().__init__(parent=parent)


class IndexedListItem(QListWidgetItem):
	def init(self, text:str, parent:QListWidget, index:int):
		super().__init__(text, parent)
		self.index = index
		return


class GenericPopup(QDialog):
	def __init__(self, title:str, confirm_action:typ.Callable=None, confirm_text:str=tr('Confirm')):
		super().__init__(f=Qt.WindowType.Window)

		self.shape = QVBoxLayout(self)
		self.setModal(True)
		self.setStyleSheet(f"""
			QWidget {{
				font-family: {SETTINGS['main_font']};
				font-size: {SETTINGS['main_font_size']};
			}}
			QLabel, QPushButton {{
				font-weight: bold;
			}}""")

		###	Setting up popup-contents.
		# -	Window-Title.
		self.title = QLabel(tr(title))
		self.setWindowTitle(self.title.text())
		self.title.setFont(NAV_FONT.bold())
		self.shape.addWidget(self.title)
		self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)


		# - Confirm/cancel buttons.
		self.button_area = QWidget(self)
		self.button_area.shape = QHBoxLayout(self.button_area)
		self.canceller = QPushButton(tr('Cancel'), self.button_area)
		self.canceller.clicked.connect(self.reject)
		self.button_area.shape.addWidget(self.canceller)

		self.confirmer = QPushButton(confirm_text, self.button_area)
		if confirm_action is not None:
			self.confirmer.clicked.connect(confirm_action)
		self.button_area.shape.addWidget(self.confirmer)

		return


class LedgerSelector(QWidget):
	def __init__(self, switch_function:typ.Callable=None, showAllEntry = False, parent:QWidget=None):
		super().__init__(parent=parent)

		self.ledger_access = LedgerTable()

		self.shape = QFormLayout(self)
		self.label = QLabel(tr('Select Ledger: '))
		self.selector = QComboBox()
		self.shape.addRow(self.label, self.selector)

		self.dataDictionary = {}

		for ledger in self.ledger_access.getAll():
			self.dataDictionary[ledger.rowID] = self.selector.count()
			self.selector.addItem(ledger.title, ledger.rowID)
		print(f'dataDictionary {self.dataDictionary}')

		if showAllEntry:
			self.selector.addItem(tr('All Ledgers'), None)

		if switch_function is not None:
			self.selector.currentIndexChanged.connect(switch_function)

		return


class RecordDisplayTable(QTableWidget):
	def __init__(self, parent:QWidget, headers:list[str]):
		self.HEADERS = headers
		self.loaded_display_widgets:list[list[QLabel, BalChangeGroup]] = []

		super().__init__(parent=parent)
		self.setColumnCount(len(self.HEADERS))
		self.setAlternatingRowColors(True)
		self.setFont(DATA_FONT.reg())
		self.lines_per_row = SETTINGS['display_line_count']

		for head in self.HEADERS:
			self.setHorizontalHeaderItem(self.HEADERS.index(head), QTableWidgetItem(head))
			self.horizontalHeaderItem(self.HEADERS.index(head)).setFont(DATA_FONT.bold())


	def populate(self):
		# if len([record for record in widgetset if record[0] == 'TOTAL']) > 0:
		# 	totalrow = [record for record in widgetset if record[0] == 'TOTAL'][0]
		# 	widgetset.remove(totalrow)
		# 	widgetset.insert(0, totalrow)

		# - Begin table-population-loop.
		table_row = 0
		for display_row in self.loaded_display_widgets:
			if table_row == self.rowCount():
				self.insertRow(self.rowCount())
			row_column = 0
			for item in display_row[1:]:
				self.setCellWidget(table_row, row_column, item)
				if self.columnWidth(row_column) < item.width():
					self.setColumnWidth(row_column, item.width()+20)
				row_column += 1
			table_row += 1

		for row in range(self.rowCount()):
			# - Set height of each row to allow two lines of text.
			self.setRowHeight(row, DATA_FONT.regmetrics.lineSpacing() * self.lines_per_row *1.1)
		return


class CategoryMaker(QDialog):
	def __init__(self,
			updateCallback:typ.Callable,
			current_rowid:int):

		super().__init__(None, Qt.WindowType.Window)
		self.current_rowid = current_rowid
		self.updateCallback = updateCallback
		self.setModal(True)
		self.setStyleSheet(f"""
			QWidget {{
				font-family: {SETTINGS['main_font']};
				font-size: {SETTINGS['main_font_size']};
			}}
			QLabel, QPushButton {{
				font-weight: bold;
			}}""")

		self.TITLE_NAME = 'Title'
		self.DESC_NAME = 'Description'

		self.shape = QVBoxLayout(self)
		self.edit_area = QFormLayout(self)	# For setting the values for a new/changed record.
		self.shape.addLayout(self.edit_area)
		self.error_block = QLabel('Errors',self) # for displaying errors
		self.shape.addWidget(self.error_block)
		self.error_block.hide()
		self.action_area = QHBoxLayout(self)	# Holds the buttons for 'Confirm' and 'Cancel' and such.
		self.shape.addLayout(self.action_area)

		self.canceller = QPushButton(tr('Cancel'), self)
		self.canceller.clicked.connect(self.reject)
		self.action_area.addWidget(self.canceller)

		self.confirmer = QPushButton(tr('Confirm'), self)
		self.confirmer.clicked.connect(self.editCategory)
		self.action_area.addWidget(self.confirmer)

		self.title_label = QLabel(tr('Title'), self)
		self.title_entry = QLineEdit(self)
		self.title_entry.setAccessibleName(self.TITLE_NAME)
		self.edit_area.addRow(self.title_label, self.title_entry)

		self.desc_label = QLabel(tr('Description'), self)
		self.desc_entry = QPlainTextEdit(self)
		self.desc_entry.setAccessibleName(self.DESC_NAME)
		self.desc_entry.setTabChangesFocus(True)
		self.edit_area.addRow(self.desc_label, self.desc_entry)
		self.import_current(current_rowid)
		return

	def import_current(self, rowid):
		print(f'inside import_current {rowid}')
		categoryTable = CategoryTable()
		category = categoryTable.get(rowid)
		print(f'found transaction {category.title}')
		self.title_entry.setText(category.title)
		self.desc_entry.setPlainText(category.description)

	def editCategory(self):
		category = Category()
		category.title = self.title_entry.text()
		category.description = self.desc_entry.toPlainText()
		category.rowID = self.current_rowid
		errors = []
		errors.extend(category.validate(True))
		if len(errors) == 0:
			categoryTable = CategoryTable()
			rowID = categoryTable.update(category)
			self.updateCallback()
			# self.updateCallback(category)
			self.done(1)
		else:
			currentErrors = 'Please fix the following issues:\n'
			for error in errors:
				currentErrors = currentErrors + '\n* ' + error.message
			self.error_block.setText(currentErrors)
			self.error_block.show()

		return


class CategoryDisplayTable(RecordDisplayTable):
	def __init__(self, parent:QWidget, updateCallback:typ.Callable=None):
		super().__init__(parent=parent, headers=['Title', 'Description', 'Edit'])
		self.majcat_interface = CategoryTable()

		self.updateCallback = updateCallback
		self.title_index = self.HEADERS.index('Title')+1
		self.desc_index = self.HEADERS.index('Description')+1
		self.edit_index = self.HEADERS.index('Edit')+1

		return


	def format_display_row(self, datalist:list) -> list[int,QLabel]:
		widget_row = [None] * (len(self.HEADERS)+1)

		row_id:int = datalist[0]
		title:str = datalist[self.title_index]
		desc:str = datalist[self.desc_index]
		edit = QPushButton(parent=self, text=tr('Edit'))
		edit.clicked.connect(lambda: self.open_updatemenu(row_id))

		widget_row[0] = row_id
		widget_row[self.title_index] = QLabel(title)
		widget_row[self.title_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Title'), 'bold'))
		widget_row[self.desc_index] = QPlainTextEdit(desc)
		widget_row[self.desc_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Description'), 'bold'))
		widget_row[self.desc_index].setReadOnly(True)
		widget_row[self.desc_index].setStyleSheet(f"""
			QWidget {{
				border: none;
			}}""")
		widget_row[self.edit_index] = edit

		return widget_row


	def process_raw_records(self, dataset:list[Category]):
		for category in dataset:
			processed_record = []
			# -	Including RowID-values so I can later tell which
			#	records are already in the display-table.
			processed_record.insert(0, category.rowID)

			processed_record.insert(self.title_index, category.title)

			# -	Description.
			descript = ''
			if hasattr(category, 'description'):
				descript = category.description
			processed_record.insert(self.desc_index, descript)

			self.loaded_display_widgets.append(self.format_display_row(processed_record))

		return

	@Slot(int)
	def open_updatemenu(self, rowid):
		print(f'launching edit with {rowid}')
		# dialog = CategoryMaker(self.updateCategoryCallback, current_rowid=rowid)
		dialog = CategoryMaker(self.updateCallback, current_rowid=rowid)
		dialog.exec()
		return

	# def updateCategoryCallback(self, category:Category):
	# 	print(f'updating {category.title}')


class PartyMaker(QDialog):
	def __init__(self,
			updateCallback:typ.Callable,
			current_rowid:int):

		super().__init__(None, Qt.WindowType.Window)
		self.current_rowid = current_rowid
		self.updateCallback = updateCallback
		self.setModal(True)
		self.setStyleSheet(f"""
			QWidget {{
				font-family: {SETTINGS['main_font']};
				font-size: {SETTINGS['main_font_size']};
			}}
			QLabel, QPushButton {{
				font-weight: bold;
			}}""")

		self.NAME_NAME = 'Name'
		self.PHONE_NAME = 'Description'
		self.EMAIL_NAME = 'Email'
		self.NOTES_NAME = 'Notes'

		self.shape = QVBoxLayout(self)
		self.edit_area = QFormLayout(self)	# For setting the values for a new/changed record.
		self.shape.addLayout(self.edit_area)
		self.error_block = QLabel('Errors',self) # for displaying errors
		self.shape.addWidget(self.error_block)
		self.error_block.hide()
		self.action_area = QHBoxLayout(self)	# Holds the buttons for 'Confirm' and 'Cancel' and such.
		self.shape.addLayout(self.action_area)

		self.canceller = QPushButton(tr('Cancel'), self)
		self.canceller.clicked.connect(self.reject)
		self.action_area.addWidget(self.canceller)

		self.confirmer = QPushButton(tr('Confirm'), self)
		self.confirmer.clicked.connect(self.editParty)
		self.action_area.addWidget(self.confirmer)

		self.name_label = QLabel(tr('Name'), self)
		self.name_entry = QLineEdit(self)
		self.name_entry.setAccessibleName(self.NAME_NAME)
		self.edit_area.addRow(self.name_label, self.name_entry)

		self.phone_label = QLabel(tr('Phone'), self)
		self.phone_entry = QLineEdit(self)
		self.phone_entry.setAccessibleName(self.PHONE_NAME)
		self.edit_area.addRow(self.phone_label, self.phone_entry)

		self.email_label = QLabel(tr('Email'), self)
		self.email_entry = QLineEdit(self)
		self.email_entry.setAccessibleName(self.EMAIL_NAME)
		self.edit_area.addRow(self.email_label, self.email_entry)

		self.notes_label = QLabel(tr('Notes'), self)
		self.notes_entry = QPlainTextEdit(self)
		self.notes_entry.setAccessibleName(self.NOTES_NAME)
		self.notes_entry.setTabChangesFocus(True)
		self.edit_area.addRow(self.notes_label, self.notes_entry)

		self.import_current(current_rowid)
		return

	def import_current(self, rowid):
		print(f'inside import_current {rowid}')
		partyTable = SecondPartyTable()
		secondParty = partyTable.get(rowid)
		print(f'found second party {secondParty}')
		self.name_entry.setText(secondParty.name)
		self.phone_entry.setText(secondParty.phone)
		self.email_entry.setText(secondParty.email)
		self.notes_entry.setPlainText(secondParty.notes)

	def editParty(self):
		secondParty = SecondParty()
		secondParty.name = self.name_entry.text()
		secondParty.phone = self.phone_entry.text()
		secondParty.email = self.email_entry.text()
		secondParty.notes = self.notes_entry.toPlainText()
		secondParty.rowID = self.current_rowid
		errors = []
		errors.extend(secondParty.validate(True))
		if len(errors) == 0:
			partyTable = SecondPartyTable()
			rowID = partyTable.update(secondParty)
			self.updateCallback()
			# self.updateCallback(secondParty)
			self.done(1)
		else:
			currentErrors = 'Please fix the following issues:\n'
			for error in errors:
				currentErrors = currentErrors + '\n* ' + error.message
			self.error_block.setText(currentErrors)
			self.error_block.show()


class PartyDisplayTable(RecordDisplayTable):
	def __init__(self, parent:QWidget, updateCallback:typ.Callable=None):
		super().__init__(parent=parent, headers=['Name', 'Phone', 'Email', 'Notes', 'Edit'])

		self.party_interface = SecondPartyTable()
		self.updateCallback = updateCallback

		self.name_index = self.HEADERS.index('Name')+1
		self.phone_index = self.HEADERS.index('Phone')+1
		self.email_index = self.HEADERS.index('Email')+1
		self.notes_index = self.HEADERS.index('Notes')+1

	def format_display_row(self, datalist:list) -> list[int,QLabel,QPlainTextEdit]:
		widget_row = [None] * (len(self.HEADERS)+1)

		row_id = datalist[0]
		name = datalist[self.name_index]
		phone = datalist[self.phone_index]
		email = datalist[self.email_index]
		notes = datalist[self.notes_index]
		edit = QPushButton(parent=self, text=tr('Edit'))
		edit.clicked.connect(lambda: self.open_updatemenu(row_id))

		widget_row[0] = row_id
		widget_row[self.name_index] = QLabel(name)
		widget_row[self.name_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Name'), 'bold'))
		widget_row[self.phone_index] = QLabel(phone)
		widget_row[self.phone_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Phone', disambiguation='phone-number'), 'bold'))
		widget_row[self.email_index] = QLabel(email)
		widget_row[self.email_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Email', disambiguation='email-address'), 'bold'))
		widget_row[self.notes_index] = QPlainTextEdit(notes)
		widget_row[self.notes_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Notes'), 'bold'))
		widget_row[self.notes_index].setReadOnly(True)
		widget_row[self.notes_index].setStyleSheet(f"""
			QWidget {{
				border: none;
			}}""")
		widget_row[-1] = edit

		return widget_row


	def process_raw_records(self, dataset:list[SecondParty]):
		for party in dataset:
			processed_record = []

			# -	Including RowID-values so I can later tell which
			#	records are already in the display-table.
			processed_record.insert(0, party.rowID)

			processed_record.insert(self.name_index, party.name)

			phone = ''
			if hasattr(party, 'phone'):
				phone = party.phone
			processed_record.insert(self.phone_index, phone)

			email = ''
			if hasattr(party, 'email'):
				email = party.email
			processed_record.insert(self.email_index, email)

			notes = ''
			if hasattr(party, 'notes'):
				notes = party.notes
			processed_record.insert(self.notes_index, notes)

			self.loaded_display_widgets.append(self.format_display_row(processed_record))

		return

	@Slot(int)
	def open_updatemenu(self, rowid):
		print(f'launching edit with {rowid}')
		dialog = PartyMaker(self.updateCallback, current_rowid=rowid)
		dialog.exec()
		return

	# def updatePartyCallback(self, secondParty:SecondParty):
	# 	print(f'updating {secondParty.name}')