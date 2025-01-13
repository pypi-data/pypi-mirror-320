import json, typing as typ

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ui.Font import *
from storage.Database import *

from ui.Common import *
from data.Transaction import Transaction
from data.Error import Error

TESTDATA_MARKER = 'Is_Testdata'
NEW_INDICATOR = "new"
ADD_NEW_LABEL = "-- Add New --"

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


class CU_ErrorPopup(GenericPopup):
	def __init__(self,
		table: TableInfo,
		operation_type: typ.Literal['create','update'],
		error_list: list[str]):

		super().__init__(title='Error')

		# -	Generic error-message.
		if len(error_list) > 1:
			sentence_intro = 'There were some issues'
		else:
			sentence_intro = 'There was an issue'

		if table == MAIN_TABLE:
			subject = 'transaction'
		elif table in (MAJCAT_TABLE, SUBCAT_TABLE):
			subject = 'category'
		else:
			subject = 'contact'

		if operation_type == 'create':
			summary = tr(f'{sentence_intro} with the new {subject} you tried to enter;')
		else:
			summary = tr(f'{sentence_intro} with the changes you tried to make to the {subject};')

		self.error_summary = QLabel(summary)
		self.shape.addWidget(self.error_summary)

		self.error_display = QTextEdit()
		for message in error_list:
			self.error_display.append('\n' + message)
		self.error_display.setFont(DATA_FONT.reg())
		self.shape.addWidget(self.error_display)


class TransactWidget(QWidget):
	"""
	- TransactWidget is the superclass which provides a some
	important setup-objects and processing-methods to the
	classes which work with the display, editing, or creation
	of records in the 'Transactions' table.
	"""
	def __init__(self):
		super().__init__()
		self.setAccessibleName('Transactions')
		self.shape = QVBoxLayout(self)

		# >	Configuring the table which displays recently-
		#	entered records.

		# - Setting headers and a dictionary for indices of
		#	specific ones thereof, so child-classes' functions
		#	aren't using literals to point at a column-ordering
		#	which may change.
		self.HEADERS = ['Date', 'Item Name', 'Vendor', 'Expense', 'Revenue', 'Categories', 'Description', 'Edit']
		self.DATA_INDICES = {
			'tDate' : self.HEADERS.index('Date') + 1,	# '+ 1' because HEADERS doesn't have an entry for the RowID column.
			'iName' : self.HEADERS.index('Item Name') + 1,
			'party' : self.HEADERS.index('Vendor') + 1,
			'expen' : self.HEADERS.index('Expense') + 1,
			'reven' : self.HEADERS.index('Revenue') + 1,
			'categ' : self.HEADERS.index('Categories') + 1,
			'descr' : self.HEADERS.index('Description') + 1}

		return

	def compile_balChange(self, expen:BalChangeGroup, reven:BalChangeGroup) -> float:
		"""
		- Takes the display-objects from the 'Expenses' and
		'Revenue' columns and returns a single processable
		'Balance-Change' value from them.
		"""
		expen_val = expen.value_area.text()
		reven_val = reven.value_area.text()

		# -	Removing power-group-separators.
		expen_val = expen_val.replace(',',''); expen_val = expen_val.replace("'",'')
		reven_val = reven_val.replace(',',''); reven_val = reven_val.replace("'",'')

		if expen_val == '':
			expen_val = 0.0
			reven_val = float(reven_val)
		elif reven_val == '':
			expen_val = float(expen_val)
			reven_val = 0.0
		else:	# Will have values for both, as enabled by the 'mixed_cashflow_allowed' setting being True.
			expen_val = float(expen_val)
			reven_val = float(reven_val)

		return (reven_val - expen_val)

	def decouple_categs(self, categories:str) -> tuple[int,int|None]:
		"""
		- Turns a human-readable 'Categories' string into a tuple
		of RowID-values for records in MajorCategories and
		SubCategories — if there is no string-part for
		subcategory, the [1]-index is filled with (None).
		"""
		categories = categories.replace(' ','')
		if ',' in categories:	# There are both a major and minor category defined.
			major = categories.split(',')[0]
			sub = categories.split(',')[1]
		else:
			major = categories
			sub = None

		QENV.edit.execute(f"""
			SELECT RowID FROM {MAJCAT_TABLE}
				WHERE Title = ?""",
			(major,))
		major_id = QENV.edit.fetchone()[0]

		if sub != None:
			QENV.edit.execute(f"""
				SELECT RowID FROM {SUBCAT_TABLE}
					WHERE Title = ?
					AND Parent = ?""",
				(sub, major_id))
			sub_id = QENV.edit.fetchone()[0]
		else:
			sub_id = None

		return (major_id, sub_id)

	def format_dateEdit(self, dateEdit:QDateEdit):
		dateEdit.setDisplayFormat('yyyy-MMM-dd')
		dateEdit.setFont(DATA_FONT.reg())


class TransactMaker(QDialog):
	"""
	- TransactMaker is the class which handles entry of new
	records into the central table of the database,
	'Transactions'.
	"""
	def __init__(self,
			source:typ.Literal['create','update','delete'],
			updateCallback:typ.Callable,
			current_rowid:int=None,
			selected_ledger=None):

		categoryTable = CategoryTable()
		secondPartyTable = SecondPartyTable()

		super().__init__(None, Qt.WindowType.Window)
		self.current_rowid = current_rowid
		self.updateCallback = updateCallback
		self.source = source
		self.setModal(True)
		self.DO_SAVE = True	# Debug-variable which can be recoded to 'False' to make changes not actually save.

		self.setStyleSheet(f"""
			QWidget {{
				font-family: {SETTINGS['main_font']};
				font-size: {SETTINGS['main_font_size']};
			}}
			QLabel, QPushButton {{
				font-weight: bold;
			}}""")

		self.TRIN = TransactWidget()	# 'TRansaction INfo'.
		self.TRIN.hide()
		self.entry_widgets = []

		# Transactions ([0]Date, [1]Item_Name, [2]Balance_Effect, [3]Major_Category, [4]Sub_Category, [5]Description, [6]Second_Party, [7]Is_Testdata)
		self.DATE_NAME = 'Date'
		self.NAME_NAME = 'Name'
		self.PARTY_NAME = 'Vendor'
		self.REVEN_NAME = 'Revenue'
		self.EXPEN_NAME = 'Expense'
		self.CATEG_NAME = 'Categories'
		self.LEDGER_NAME = 'Ledger'
		self.DESC_NAME = 'Description'

		# >	Widget-Setup:
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

		confirm_label = 'Confirm'
		if self.source == 'update':
			confirm_label = 'Edit'
			self.deleter = QPushButton(tr('Delete'), self)
			self.deleter.clicked.connect(self.deleteTransaction)
			self.action_area.addWidget(self.deleter)

		self.confirmer = QPushButton(tr(confirm_label), self)
		self.confirmer.clicked.connect(self.editTransaction)
		self.action_area.addWidget(self.confirmer)


		self.ledger_label = QLabel(tr(self.LEDGER_NAME), self)
		self.ledger_entry = LedgerSelector(None, False, self)
		if selected_ledger is not None:
			ledger_index = self.ledger_entry.dataDictionary[selected_ledger]
			self.ledger_entry.selector.setCurrentIndex(ledger_index)
		self.ledger_entry.label.hide()
		self.edit_area.addRow(self.ledger_label, self.ledger_entry)
		self.entry_widgets.append(self.ledger_entry)

		self.date_label = QLabel(tr(self.TRIN.HEADERS[self.TRIN.DATA_INDICES['tDate']-1]), self)
		self.date_entry = QDateEdit(QDate(), self)
		self.date_entry.setAccessibleName(self.DATE_NAME)
		self.TRIN.format_dateEdit(self.date_entry)
		self.edit_area.addRow(self.date_label, self.date_entry)
		self.entry_widgets.append(self.date_entry)

		self.name_label = QLabel(tr(self.TRIN.HEADERS[self.TRIN.DATA_INDICES['iName']-1]), self)
		self.name_entry = QLineEdit(self)
		self.name_entry.setAccessibleName(self.NAME_NAME)
		self.edit_area.addRow(self.name_label, self.name_entry)
		self.entry_widgets.append(self.name_entry)

		self.party_label = QLabel(tr(self.TRIN.HEADERS[self.TRIN.DATA_INDICES['party']-1]), self)
		self.party_entry = QComboBox(self)
		self.party_entry.setAccessibleName(self.PARTY_NAME)
		secondParties = secondPartyTable.getAll()
		self.party_dict = {}
		for secondParty in secondParties:
			self.party_dict[secondParty.rowID] = self.party_entry.count()
			self.party_entry.addItem(secondParty.name, secondParty.rowID)
		self.party_entry.addItem(ADD_NEW_LABEL, NEW_INDICATOR)
		self.edit_area.addRow(self.party_label, self.party_entry)
		self.entry_widgets.append(self.party_entry)

		# new party entry
		self.new_party_label = QLabel("", self)
		self.new_party_entry = QLineEdit(self)
		self.edit_area.addRow(self.new_party_label, self.new_party_entry)
		self.entry_widgets.append(self.new_party_entry)
		self.new_party_entry.hide()
		self.new_party_label.hide()
		# add listener for change to add new
		self.party_entry.currentIndexChanged.connect(self.toggle_new_party)
		if len(secondParties) == 0:	# Accounting for there being no defined vendors initially.
			self.toggle_new_party()


		expenseLabel = tr(self.TRIN.HEADERS[self.TRIN.DATA_INDICES['expen']-1]) + "  \u200A\u200A(\u2212)"
		self.expen_label = QLabel(expenseLabel, self)
		# self.expen_entry = BalChangeGroup('-', self, None, True)
		self.expen_entry = QLineEdit(self)
		self.expen_entry.setAccessibleName(self.EXPEN_NAME)
		self.edit_area.addRow(self.expen_label, self.expen_entry)
		self.entry_widgets.append(self.expen_entry)

		expenseLabel = tr(self.TRIN.HEADERS[self.TRIN.DATA_INDICES['reven']-1]) + "  (+)"
		self.reven_label = QLabel(expenseLabel, self)
		# self.reven_entry = BalChangeGroup('+', self, None, True)
		self.reven_entry = QLineEdit(self)
		self.reven_entry.setAccessibleName(self.REVEN_NAME)
		self.edit_area.addRow(self.reven_label, self.reven_entry)
		self.entry_widgets.append(self.reven_entry)

		self.categ_label = QLabel(tr(self.TRIN.HEADERS[self.TRIN.DATA_INDICES['categ']-1]), self)
		self.categ_entry = QComboBox(self)
		self.categ_entry.setAccessibleName(self.CATEG_NAME)
		# self.categ_entry.addItems(MAJCAT_TABLE.id_name_map.values())
		categories = categoryTable.getAll()
		self.categ_dict = {}
		for category in categories:
			self.categ_dict[category.rowID] = self.categ_entry.count()
			self.categ_entry.addItem(category.title, category.rowID)
		self.categ_entry.addItem(ADD_NEW_LABEL, NEW_INDICATOR)
		self.edit_area.addRow(self.categ_label, self.categ_entry)
		self.entry_widgets.append(self.categ_entry)

		# new category entry
		self.new_categ_label = QLabel("", self)
		self.new_categ_entry = QLineEdit(self)
		self.edit_area.addRow(self.new_categ_label, self.new_categ_entry)
		self.entry_widgets.append(self.new_categ_entry)
		self.new_categ_entry.hide()
		self.new_categ_label.hide()
		# add listener for change to add new
		self.categ_entry.currentIndexChanged.connect(self.toggle_new_categ)
		if len(categories) == 0:	# Accounting for there being no defined vendors initially.
			self.toggle_new_categ()

		self.desc_label = QLabel(tr(self.TRIN.HEADERS[self.TRIN.DATA_INDICES['descr']-1]), self)
		self.desc_entry = QPlainTextEdit(self)
		self.desc_entry.setAccessibleName(self.DESC_NAME)
		self.desc_entry.setTabChangesFocus(True)
		self.edit_area.addRow(self.desc_label, self.desc_entry)
		self.entry_widgets.append(self.desc_entry)

		self.confirm_message_area = QPlainTextEdit(
			tr("No problems were detected with the new transaction. Press 'Confirm' again if everything seems correct."),	#@ This feature is not implemented.
			self)
		self.confirm_message_area.setReadOnly(True)
		self.shape.addWidget(self.confirm_message_area)
		self.confirm_message_area.hide()

		# >	Operations-Setup:
		if self.source == 'create':
			# - Setting default date to current date.
			self.date_entry.setDate(QDate.currentDate())
			self.name_entry.setPlaceholderText(tr('Item-Name'))

			#@ Remainder of operations to set up blank menu.

		elif self.source == 'update':
			self.import_current(current_rowid)	# @ TODO!: How is this being passed a full transaction?


		return


	def import_current(self, row_id):
		print(f'inside import_current {row_id}')
		transactionTable = TransactionTable()
		transaction = transactionTable.get(row_id)
		print(f'found transaction {transaction.itemName}')
		self.ledger_entry.selector.setCurrentIndex(self.ledger_entry.dataDictionary[transaction.ledgerID])
		date = QDate()
		dateParts = transaction.date.split("-")
		date.setDate(int(dateParts[0]),int(dateParts[1]),int(dateParts[2]))
		self.date_entry.setDate(date)
		self.name_entry.setText(transaction.itemName)
		self.party_entry.setCurrentIndex(self.party_dict[transaction.secondPartyId])
		if (hasattr(transaction, 'revenue')):
			self.reven_entry.setText(str(transaction.revenue))
		else:
			self.expen_entry.setText(str(abs(transaction.expense)))
		self.categ_entry.setCurrentIndex(self.categ_dict[transaction.categoryId])
		self.desc_entry.setPlainText(transaction.description)


	def toggle_new_categ(self):
		selected = self.categ_entry.currentData()
		if selected == NEW_INDICATOR:
			self.new_categ_entry.show()
			self.new_categ_label.show()
		else:
			self.new_categ_entry.hide()
			self.new_categ_label.hide()


	def toggle_new_party(self):
		selected = self.party_entry.currentData()
		if selected == NEW_INDICATOR:
			self.new_party_entry.show()
			self.new_party_label.show()
		else:
			self.new_party_entry.hide()
			self.new_party_label.hide()


	def deleteTransaction(self):
		transactionTable = TransactionTable()
		transactionTable.delete(self.current_rowid)
		self.done(1)
		self.updateCallback()


	def editTransaction(self):
		# verify number for expense/revenue
		errors = []
		transaction = Transaction()
		print('creating new transaction')
		revenue = self.reven_entry.text()
		print('revenue entry', revenue)
		if len(revenue) > 0:
			if is_float(revenue):
				transaction.revenue = float(revenue)
				print('revenue', transaction.revenue)
			else:
				errors.append(Error('not_number', 'reven_entry', 'revenue must be a number'))
		expense = self.expen_entry.text()
		print('expense entry', expense)
		if len(expense) > 0:
			if is_float(expense):
				transaction.expense = float(expense)
				print('expense', transaction.expense)
				self.reject
			else:
				errors.append(Error('not_number', 'expen_entry', 'expense must be a number'))

		transaction.ledgerID = self.ledger_entry.selector.currentData()
		print('ledgerID:', transaction.ledgerID)
		transaction.categoryId = self.categ_entry.currentData()
		print('categoryId', transaction.categoryId)
		transaction.itemName = self.name_entry.text()
		print('itemName', transaction.itemName)
		transaction.description = self.desc_entry.toPlainText()
		print('description', transaction.description)
		transaction.secondPartyId = self.party_entry.currentData()
		print('secondPartyId', transaction.secondPartyId)
		# get the date from date widget
		year = str(self.date_entry.date().year())
		month = self.date_entry.date().month()
		if month < 10:
			month = f'0{month}'
		else:
			month = str(month)
		day = self.date_entry.date().day()
		if day < 10:
			day = f'0{day}'
		else:
			day = str(day)
		transaction.date = year + "-" + month + "-" + day
		print('date', transaction.date)
		if transaction.categoryId == NEW_INDICATOR and len(self.new_categ_entry.text()) == 0:
			errors.append(Error('not_defined', 'new_categ_entry', 'Fill in Category name when adding a new one.'))
		if transaction.secondPartyId == NEW_INDICATOR and len(self.new_party_entry.text()) == 0:
			errors.append(Error('not_defined', 'new_party_entry', 'Fill in Vendor name when adding a new one.'))
		errors.extend(transaction.validate(True))

		if len(errors) == 0:
			if transaction.categoryId == NEW_INDICATOR:
				catTable = CategoryTable()
				transaction.categoryId = catTable.createFromTitle(self.new_categ_entry.text(), using_testdata)

			if transaction.secondPartyId == NEW_INDICATOR:
				secPartyTable = SecondPartyTable()
				transaction.secondPartyId = secPartyTable.createFromName(self.new_party_entry.text(), using_testdata)

			transactionTable = TransactionTable()
			if self.source == 'create':
				rowID = transactionTable.create(transaction)
				transaction.rowID = rowID
				print(f'created transaction with id {rowID}')
				self.done(1)
				self.updateCallback(transaction)
			elif self.source == 'update':
				transaction.rowID = self.current_rowid
				transactionTable.update(transaction)
				self.done(1)
				self.updateCallback()

		else:
			currentErrors = 'Please fix the following issues:\n'
			for error in errors:
				currentErrors += '\n\u2022 ' + error.message
			self.error_block.setText(currentErrors)
			self.error_block.show()

			# TODO - need to display errors on screen


class TransactionDisplayTable(RecordDisplayTable):
	def __init__(self, parent:QWidget, editCallback=None):
		super().__init__(parent=parent, headers=['Date', 'Item Name', 'Vendor', 'Expense', 'Revenue', 'Categories', 'Description', 'Edit'])

		self.editCallback = editCallback
		self.table_interface = TransactionTable()
		self.majcat_interface = CategoryTable()
		# self.subcat_interface = SubCategTable()
		self.party_interface = SecondPartyTable()

		self.date_index = self.HEADERS.index('Date')+1
		self.name_index = self.HEADERS.index('Item Name')+1
		self.party_index = self.HEADERS.index('Vendor')+1
		self.expense_index = self.HEADERS.index('Expense')+1
		self.revenue_index = self.HEADERS.index('Revenue')+1
		self.categ_index = self.HEADERS.index('Categories')+1
		self.desc_index = self.HEADERS.index('Description')+1

		return


	def format_display_row(self, datarow:list) -> list[int,BalChangeGroup,QLabel]:
		widget_row = [None] * (len(self.HEADERS)+1)

		row_id:int = datarow[0]
		date:str = datarow[self.date_index]
		item_name:str = datarow[self.name_index]
		expense:float = datarow[self.expense_index]
		revenue:float = datarow[self.revenue_index]
		categ:str = datarow[self.categ_index]
		desc:str = datarow[self.desc_index]
		party:str = datarow[self.party_index]
		edit = QPushButton(parent=self, text=tr('Edit'))
		edit.clicked.connect(lambda: self.open_edit_menu(self.editCallback, row_id))

		widget_row[0] = row_id
		widget_row[self.date_index] = QLabel(date)
		widget_row[self.date_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Date'), 'bold'))
		widget_row[self.name_index] = QLabel(item_name)
		widget_row[self.name_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Item Name'), 'bold'))
		widget_row[self.expense_index] = BalChangeGroup('-', self, expense)
		widget_row[self.revenue_index] = BalChangeGroup('+', self, revenue)
		widget_row[self.categ_index] = QLabel(categ)
		widget_row[self.categ_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Categories'), 'bold'))
		widget_row[self.desc_index] = QPlainTextEdit(desc)
		widget_row[self.desc_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Description'), 'bold'))
		widget_row[self.desc_index].setReadOnly(True)
		widget_row[self.desc_index].setStyleSheet(f"""
			QWidget {{
				border: none;
			}}""")
		widget_row[self.party_index] = QLabel(party)
		widget_row[self.party_index].setMinimumWidth(DATA_FONT.find_gwidth(tr('Buyer/Seller'), 'bold'))
		widget_row[-1] = edit

		return widget_row


	def process_raw_records(self, dataset:list[Transaction]):
		for transact in dataset:
			processed_record = []
			# -	Including RowID-values so I can later tell which
			#	records are already in the display-table.
			processed_record.insert(0, transact.rowID)

			# - Date is converted from storage-format
			#	('YYYY-MM-DD') to display-format ('YYYY-Mnþ-DD').
			processed_record.insert(self.date_index, transact.date)

			processed_record.insert(self.name_index, transact.itemName)

			# - Expenses and Revenue.
			expen_val = 0.0
			reven_val = 0.0
			if hasattr(transact, 'expense'):
				expen_val = transact.expense
			if hasattr(transact, 'revenue'):
				reven_val = transact.revenue

			processed_record.insert(self.expense_index, expen_val)
			processed_record.insert(self.revenue_index, reven_val)

			# -	Major_Category and Sub_Category, combining into a
			#	single display-column.
			categ_string = self.majcat_interface.title_lookup(transact.categoryId)
			# if hasattr(transact, 'subCategoryId'):
			# 	categ_string += ', '+self.subcat_interface.title_lookup(transact.subCategoryId)
			processed_record.insert(self.categ_index, categ_string)

			# -	Description.
			descript = ''
			if hasattr(transact, 'description'):
				descript = transact.description
			processed_record.insert(self.desc_index, descript)

			# - Second_Party.
			second_party = ''
			if hasattr(transact, 'secondPartyId'):
				second_party = (self.party_interface.name_lookup(transact.secondPartyId))
			processed_record.insert(self.party_index, second_party)

			self.loaded_display_widgets.append(self.format_display_row(processed_record))

		# # - Adding total-row.
		# totalrow = [None] * (len(self.HEADERS)+1)
		# totalrow[0] = 'TOTAL'
		# totalrow[1] = QLabel(tr('Totals:'))
		# totalrow[1].setFont(DATA_FONT.bold())
		# total_revenue = sum([transact.revenue for transact in dataset if hasattr(transact, 'revenue')])
		# totalrow[self.revenue_index] = BalChangeGroup('+', self, total_revenue)
		# total_expense = abs(sum([transact.expense for transact in dataset if hasattr(transact, 'expense')]))
		# totalrow[self.expense_index] = BalChangeGroup('-', self, total_expense)
		# total_balance = total_revenue - total_expense
		# totalrow[self.desc_index] = BalChangeGroup('=', self, total_balance)

		# for x in range(len(totalrow)):
		# 	if totalrow[x] is None:
		# 		totalrow[x] = QLabel('')

		# self.loaded_display_widgets.append(totalrow)

		return

	def open_edit_menu(self, updateCallback:typ.Callable, current_rowid:int):
		# if isinstance(current_rowid, Transaction):
		# 	current_rowid = current_rowid.rowID
		edit_dialog = TransactMaker('update', updateCallback, current_rowid)
		edit_dialog.exec()


	def update_with_record(self, transaction:Transaction):
		print(f'Adding transaction with RowID = {transaction.rowID} to table.')

		old_record = [
			record for record in self.loaded_display_widgets
			if record[0] == transaction.rowID]

		if len(old_record) > 0:
			self.loaded_display_widgets.remove(old_record[0])


		self.process_raw_records([transaction])
		self.populate()

		return


class TransactDisplayer(TransactWidget):
	"""
	- TransactDisplayer is responsible for pulling existing
	records from the 'Transactions' table, and reformatting them
	for display to humans.
	"""
	def __init__(self):
		super().__init__()
		self.expense_sum = 0.0
		self.revenue_sum = 0.0
		self.balance = 0.0

		self.table_interface = TransactionTable()

		# - Making Ledger-select-widget.
		self.ledger_select_area = LedgerSelector(self.load_ledger, True, self)
		self.shape.addWidget(self.ledger_select_area)

		# - Making table-object.
		self.display_grid = TransactionDisplayTable(self,self.load_ledger)
		self.shape.addWidget(self.display_grid)

		# -	Initialize dataset with the 60 most-recent records.
		#	(Number of records loaded can be set differently
		#	by the user.)
		self.loaded_records = self.table_interface.getRecent(ledger=self.ledger_select_area.selector.currentData())
		self.display_grid.process_raw_records(self.loaded_records)

		self.totals_area = QWidget(self)
		self.totals_area.setMinimumHeight(DATA_FONT.regmetrics.lineSpacing()*1.1*3)
		self.totals_area.shape = QVBoxLayout(self.totals_area)
		self.totals_label = QLabel(tr('Totals:'))
		self.totals_label.setFont(DATA_FONT.bold())
		self.totals_area.shape.addWidget(self.totals_label)
		self.revenue_total = BalChangeGroup('+', self.totals_area, 0.00)
		self.totals_area.shape.addWidget(self.revenue_total)
		self.expense_total = BalChangeGroup('-', self.totals_area, 0.00)
		self.totals_area.shape.addWidget(self.expense_total)
		self.balance_total = BalChangeGroup('=', self.totals_area, 0.00)
		self.totals_area.shape.addWidget(self.balance_total)
		self.update_totals()

		self.shape.addWidget(self.totals_area, alignment=Qt.AlignmentFlag.AlignBottom)

		self.new_record_button = QPushButton(tr('Create New Transaction'))
		self.new_record_button.setFont(DATA_FONT.bold())
		self.new_record_button.clicked.connect(self.open_temp_addmenu)
		self.shape.addWidget(self.new_record_button)

		# -	Perform initial table-population.
		self.display_grid.populate()
		return

	def updateDisplay(self):
		self.shape.removeWidget(self.ledger_select_area)
		self.shape.addWidget(self.ledger_select_area)

		# - Asking table to update itself.
		self.shape.removeWidget(self.display_grid)
		self.display_grid = TransactionDisplayTable(self,self.load_ledger)
		self.shape.addWidget(self.display_grid)
		self.display_grid.process_raw_records(self.loaded_records)
		self.display_grid.populate()

		self.shape.removeWidget(self.totals_area)
		self.update_totals()
		self.shape.addWidget(self.totals_area)

		self.shape.removeWidget(self.new_record_button)
		self.shape.addWidget(self.new_record_button)

	def addTransactionCallback(self, transaction:Transaction):
		self.loaded_records.append(transaction)
		self.updateDisplay()
		return

	def updateTransactionCallback(self, transaction:Transaction):
		self.load_ledger()

	def sum_expenses(self):
		return sum([abs(transact.expense)*-1 for transact in self.loaded_records if hasattr(transact, 'expense')])	#@ TODO: The abs()*-1 here shouldn't be necessary; something's weird about the positivity of the values.

	def sum_revenue(self):
		return sum([transact.revenue for transact in self.loaded_records if hasattr(transact, 'revenue')])

	def update_totals(self):
		self.revenue_sum = self.sum_revenue()
		self.expense_sum = self.sum_expenses()
		self.balance = self.revenue_sum + self.expense_sum

		self.revenue_total.value_area.setText(f'{self.revenue_sum:,.2f}'.replace(',',"'"))	#@ TODO: Make this respect the setting controlling whether apostrophes are used.
		self.expense_total.value_area.setText(f'{abs(self.expense_sum):,.2f}'.replace(',',"'"))
		self.balance_total.value_area.setText(f'{self.balance:,.2f}'.replace(',',"'"))

		return

	def load_ledger(self):
		self.loaded_records = self.table_interface.getRecent(ledger=self.ledger_select_area.selector.currentData())
		self.updateDisplay()
		return

	@Slot()
	def open_temp_addmenu(self):
		dialog = TransactMaker('create',self.addTransactionCallback, selected_ledger=self.ledger_select_area.selector.currentData())
		dialog.exec()
		return

	@Slot(int)
	def open_temp_updatemenu(self, rowid):
		print(f'launching edit with {rowid}')
		dialog = TransactMaker('update',self.updateTransactionCallback, current_rowid=rowid)
		dialog.exec()
		return