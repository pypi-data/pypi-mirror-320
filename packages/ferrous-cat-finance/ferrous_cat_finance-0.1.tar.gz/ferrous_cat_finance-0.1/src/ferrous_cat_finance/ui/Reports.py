from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ui.Common import *
from ui.Transactions import TransactionDisplayTable	#@TODO!: TransactMaker should probably be in another location.
from storage.Database import FetchOutput
from storage.CategoryTable import CategoryTable
from storage.SecondPartyTable import SecondPartyTable
from storage.record_search import Searcher
from data.report_organizer import ReportOrganizer

class ConstraintSelect(QListWidget):
	def __init__(self, parent:QWidget=None):
		super().__init__(parent=parent)

		self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

	def populate(self, dataset:list[tuple[int,str]]):
		for pair in dataset:
			row_id = pair[0];  name = pair[1]
			item = IndexedListItem(name, self, row_id)
		return


class CashflowConfig(QWidget):
	def __init__(self, categ_access=CategoryTable, parent:QWidget=None):
		super().__init__(parent=parent)

		self.shape = QFormLayout(self)

		self.yearSelect_label = QLabel(tr('Report on Year: '))
		self.yearSelect_entry = QLineEdit(tr(f'{QDate.currentDate().year()}'))
		self.shape.addRow(self.yearSelect_label, self.yearSelect_entry)

		self.ledger_label = QLabel(tr('Report on Ledger: '))
		self.ledger_entry = LedgerSelector(None, True, self)
		self.ledger_entry.label.hide()
		self.shape.addRow(self.ledger_label, self.ledger_entry)

		# self.categSelect_label = QLabel(tr('Divide into \nCategories: '))
		# self.categSelect_entry = ConstraintSelect(self)
		# self.categSelect_entry.populate([(categ.rowID, categ.title) for categ in categ_access.getAll()])


class ReportDialog(GenericPopup):
	def __init__(self):
		super().__init__(tr('Reporting Options'), self.generate_cashflow, tr('Generate'))
		self.search_access = Searcher()
		self.categ_access = CategoryTable()
		self.ledger_access = LedgerTable()

		self.cashflow_parametres = CashflowConfig(self.categ_access, self)

		self.shape.addWidget(self.cashflow_parametres)

		self.shape.addWidget(self.button_area)

		return

	@Slot()
	def generate_cashflow(self):
		ledger = self.cashflow_parametres.ledger_entry.selector.currentData()
		min_date = f"{self.cashflow_parametres.yearSelect_entry.text()}-01-01"
		max_date = f"{self.cashflow_parametres.yearSelect_entry.text()}-12-31"

		query_data = self.search_access.data_search('Transactions', ledger=ledger, date_min=min_date, date_max=max_date)

		if ledger is None:	# All ledgers are selected;
			ledger_info = [(ledger.rowID, ledger.title) for ledger in self.ledger_access.getAll()]
		else:
			ledger_info = [(self.cashflow_parametres.ledger_entry.selector.currentData(), self.cashflow_parametres.ledger_entry.selector.currentText())]

		report_organ = ReportOrganizer(query_data, self.cashflow_parametres.yearSelect_entry.text(), ledger_info)

		return


class SearchReportWidget(QWidget):
	def __init__(self):
		super().__init__()

		self.errors = {}
		self.nonnumeric_error = 'You have entered characters that are not numbers or decimal-points; remove these characters to proceed.'
		self.loaded_records = []
		self.transaction_is_selected = True
		self.categories_is_selected = False
		self.parties_is_selected = False

		self.search_access = Searcher()
		# self.transaction_access = TransactionTable()
		self.category_access = CategoryTable()
		self.party_access = SecondPartyTable()
		self.setAccessibleName('Search/Report')

		self.shape = QVBoxLayout(self)
		self.entry_height = 0.4
		# self.setFixedHeight()

		# - Buttons for selecting which table is queried.
		self.table_select_area = QWidget(self)
		self.table_select_area.shape = QVBoxLayout(self.table_select_area)
		self.shape.addWidget(self.table_select_area)
		self.table_select_label = QLabel(tr('Search In: '))
		self.table_select_label.setFont(DATA_FONT.bold())
		self.table_select_area.shape.addWidget(self.table_select_label)
		self.table_selectors = QHBoxLayout()
		self.table_select_area.shape.addLayout(self.table_selectors)
		self.select_transactions = QPushButton(tr('Transactions'))
		self.select_transactions.clicked.connect(self.mark_transaction_selected)
		self.table_selectors.addWidget(self.select_transactions)
		self.select_categories = QPushButton(tr('Categories'))
		self.select_categories.clicked.connect(self.mark_categories_selected)
		self.table_selectors.addWidget(self.select_categories)
		self.select_parties = QPushButton(tr('Vendors'))
		self.select_parties.clicked.connect(self.mark_parties_selected)
		self.table_selectors.addWidget(self.select_parties)

		self.input_output_columns = QWidget(self)
		self.input_output_columns.shape = QHBoxLayout(self.input_output_columns)
		self.shape.addWidget(self.input_output_columns, alignment=Qt.AlignmentFlag.AlignTop)
		self.input_area = QWidget(self.input_output_columns)
		self.input_area.shape = QVBoxLayout(self.input_area)
		self.input_output_columns.shape.addWidget(self.input_area)

		# - Results-area:
		self.search_results = QWidget(self)
		self.search_results.shape = QVBoxLayout(self.search_results)
		# self.search_results.setFixedHeight((self.height() - self.searchbuttons_area.height()) * (1 - self.entry_height))
		# self.search_results.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.MinimumExpanding)
		self.input_output_columns.shape.addWidget(self.search_results, alignment=Qt.AlignmentFlag.AlignTop)

		self.totals_area = QWidget(self)
		self.totals_area.setMinimumHeight(DATA_FONT.regmetrics.lineSpacing()*1.1)
		self.totals_area.shape = QHBoxLayout(self.totals_area)
		self.totals_label = QLabel(tr('Totals:'))
		self.totals_label.setFont(DATA_FONT.bold())
		self.totals_area.shape.addWidget(self.totals_label)
		self.revenue_total = BalChangeGroup('+', self.totals_area, 0.00)
		self.totals_area.shape.addWidget(self.revenue_total)
		self.expense_total = BalChangeGroup('-', self.totals_area, 0.00)
		self.totals_area.shape.addWidget(self.expense_total)
		self.balance_total = BalChangeGroup('=', self.totals_area, 0.00)
		self.totals_area.shape.addWidget(self.balance_total)
		self.totals_area.hide()

		self.transaction_results:TransactionDisplayTable = None
		self.category_results:CategoryDisplayTable = None
		self.party_results:PartyDisplayTable = None
		# self.search_results.shape.addWidget(self.transaction_results)
		# self.search_results.hide()

		# > Fields for entering WHERE-conditions for queries.
		# - Container for constraints applicable to all tables:
		self.universal_constraintholder = QWidget(self)
		self.universal_constraintholder.shape = QFormLayout(self.universal_constraintholder)
		self.input_area.shape.addWidget(self.universal_constraintholder, alignment=Qt.AlignmentFlag.AlignTop)

		self.stringSearch_label = QLabel(tr('Search for Words: '))
		self.stringSearch_entry = QLineEdit()
		self.universal_constraintholder.shape.addRow(self.stringSearch_label, self.stringSearch_entry)

		# - Container for constraints specific to Transactions.
		self.transactions_constraintholder = QWidget(self)
		self.transactions_constraintholder.shape = QFormLayout(self.transactions_constraintholder)
		self.input_area.shape.addWidget(self.transactions_constraintholder, alignment=Qt.AlignmentFlag.AlignTop)

		self.ledger_label = QLabel(tr('Search in Ledger: '))
		self.ledger_entry = LedgerSelector(None, True, self)
		self.ledger_entry.label.hide()
		self.transactions_constraintholder.shape.addRow(self.ledger_label, self.ledger_entry)

		self.sortbyCateg_label = QLabel(tr('Sort by Category?'))
		self.sortbyCateg_entry = QCheckBox()
		self.transactions_constraintholder.shape.addRow(self.sortbyCateg_label, self.sortbyCateg_entry)
		self.sortbyParty_label = QLabel(tr('Sort by Vendor?'))
		self.sortbyParty_entry = QCheckBox()
		self.transactions_constraintholder.shape.addRow(self.sortbyParty_label, self.sortbyParty_entry)

		self.earliestDate_label = QLabel(tr('Earliest Date: '))
		self.earliestDate_entry = QDateEdit(QDate(y=SETTINGS['default_min_year'], m=1, d=1))
		self.earliestDate_entry.setDisplayFormat('yyyy-MMM-dd')
		self.transactions_constraintholder.shape.addRow(self.earliestDate_label, self.earliestDate_entry)
		self.latestDate_label = QLabel(tr('Latest Date: '))
		self.latestDate_entry = QDateEdit(QDate.currentDate())
		self.latestDate_entry.setDisplayFormat('yyyy-MMM-dd')
		self.transactions_constraintholder.shape.addRow(self.latestDate_label, self.latestDate_entry)
		# self.yearSearch_entry.setToolTip(tr("To return results over multiple years, use either '~' (tilde) or ',' (comma) between two years.\n\tExample 1: 1999 ~ 2003\n\tExample 2: 1999, 2003"))		# self.monthSearch_label = QLabel(tr('Months: '))		# self.monthSearch_label.setFont(DATA_FONT.reg())		# self.monthSearch_list = QListWidget()		# self.monthSearch_list.addItems((		# 	tr('01; January'),		# 	tr('02; February'),		# 	tr('03; March'),		# 	tr('04; April'),		# 	tr('05; May'),		# 	tr('06; June'),		# 	tr('07; July'),		# 	tr('08; August'),		# 	tr('09; September'),		# 	tr('10; October'),		# 	tr('11; November'),		# 	tr('12; December')))		# self.monthSearch_list.setFont(DATA_FONT.reg())
		# self.transactions_constraintholder.shape.addRow(self.monthSearch_label, self.monthSearch_list)

		self.leastExpense_label = QLabel(tr('Smallest Expense \u200A(\u2212):'))
		self.leastExpense_entry = QLineEdit()
		self.transactions_constraintholder.shape.addRow(self.leastExpense_label, self.leastExpense_entry)
		self.greatestExpense_label = QLabel(tr('Greatest Expense \u200A(\u2212):'))
		self.greatestExpense_entry = QLineEdit()
		self.transactions_constraintholder.shape.addRow(self.greatestExpense_label, self.greatestExpense_entry)

		self.leastRevenue_label = QLabel(tr('Smallest Revenue (+):'))
		self.leastRevenue_entry = QLineEdit()
		self.transactions_constraintholder.shape.addRow(self.leastRevenue_label, self.leastRevenue_entry)
		self.greatestRevenue_label = QLabel(tr('Greatest Revenue (+):'))
		self.greatestRevenue_entry = QLineEdit()
		self.transactions_constraintholder.shape.addRow(self.greatestRevenue_label, self.greatestRevenue_entry)

		self.categAccepted_label = QLabel(tr('Restrict to \nCategories: '))
		self.categAccepted_entry = ConstraintSelect(self)
		self.categAccepted_entry.populate([(category.rowID, category.title) for category in self.category_access.getAll()])
		self.transactions_constraintholder.shape.addRow(self.categAccepted_label, self.categAccepted_entry)

		self.partyAccepted_label = QLabel(tr('Restrict to \nVendors: '))
		self.partyAccepted_entry = ConstraintSelect(self)
		self.partyAccepted_entry.populate([(party.rowID, party.name) for party in self.party_access.getAll()])
		self.transactions_constraintholder.shape.addRow(self.partyAccepted_label, self.partyAccepted_entry)


		# > Area for displaying input-error-messages.
		self.error_area = QWidget(self)
		self.error_area.shape = QVBoxLayout(self.error_area)
		# self.error_area.setMaximumWidth(self.width() * 0.4)
		# self.error_area.setMinimumHeight((self.height() - self.table_select_area.height()) * self.entry_height)
		self.shape.addWidget(self.error_area, alignment=Qt.AlignmentFlag.AlignTop)
		self.error_header = QLabel(tr('Errors:'), self.error_area)
		self.error_header.setFont(NAV_FONT.reg())
		self.error_area.shape.addWidget(self.error_header)
		self.error_display = QPlainTextEdit(parent=self.error_area)
		# self.error_display.setFixedHeight(self.error_area.height() - self.error_header.height())
		self.error_area.shape.addWidget(self.error_display)
		self.error_area.hide()


		# > Buttons for searching and opening reports-menu.
		self.searchbuttons_area = QWidget(self)
		self.searchbuttons_area.shape = QHBoxLayout(self.searchbuttons_area)
		self.searchbuttons_area.shape.setSpacing(60)
		self.shape.addWidget(self.searchbuttons_area, alignment=Qt.AlignmentFlag.AlignCenter)
		self.query_button = QPushButton(tr('Search', disambiguation='verb'))
		self.query_button.setFont(NAV_FONT.reg())
		self.query_button.clicked.connect(self.search)
		self.searchbuttons_area.shape.addWidget(self.query_button)
		self.reports_button = QPushButton(tr('Reports'))
		self.reports_button.setFont(NAV_FONT.reg())
		self.reports_button.clicked.connect(self.open_reports_menu)
		self.searchbuttons_area.shape.addWidget(self.reports_button)


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
		self.totals_area.show()


	@Slot()
	def mark_transaction_selected(self):
		self.transaction_is_selected = True
		self.categories_is_selected = False
		self.parties_is_selected = False
		self.transactions_constraintholder.show()

		self.select_transactions.setStyleSheet(f"""
			QWidget {{
				color: {SETTINGS['text-highlight-color']};
			}}""")
		self.select_categories.setStyleSheet(f"""
			QWidget {{
				color: none;
			}}""")
		self.select_parties.setStyleSheet(f"""
			QWidget {{
				color: none;
			}}""")

		return

	@Slot()
	def mark_categories_selected(self):
		self.transaction_is_selected = False
		self.categories_is_selected = True
		self.parties_is_selected = False
		self.transactions_constraintholder.hide()

		self.select_transactions.setStyleSheet(f"""
			QWidget {{
				color: none;
			}}""")
		self.select_categories.setStyleSheet(f"""
			QWidget {{
				color: {SETTINGS['text-highlight-color']};
			}}""")
		self.select_parties.setStyleSheet(f"""
			QWidget {{
				color: none;
			}}""")
		return

	@Slot()
	def mark_parties_selected(self):
		self.transaction_is_selected = False
		self.categories_is_selected = False
		self.parties_is_selected = True
		self.transactions_constraintholder.hide()

		self.select_transactions.setStyleSheet(f"""
			QWidget {{
				color: none;
			}}""")
		self.select_categories.setStyleSheet(f"""
			QWidget {{
				color: none;
			}}""")
		self.select_parties.setStyleSheet(f"""
			QWidget {{
				color: {SETTINGS['text-highlight-color']};
			}}""")
		return

	@Slot()
	def search(self, /):
		sortby_categ = False
		sortby_party = False
		ledger = None
		substring = None
		min_date = None
		max_date = None
		min_expense = None
		max_expense = None
		min_revenue = None
		max_revenue = None
		categories = None
		parties = None

		if self.stringSearch_entry.text() != '':
			substring = self.stringSearch_entry.text()
		if self.transaction_is_selected:
			table = 'Transactions'

			sortby_categ = self.sortbyCateg_entry.isChecked()
			sortby_party = self.sortbyParty_entry.isChecked()

			if self.ledger_entry.selector.currentData() != None:
				ledger = self.ledger_entry.selector.currentData()

			if self.earliestDate_entry.text() != '':
				min_date = decode_date(self.earliestDate_entry.text())

			if self.latestDate_entry.text() != '':
				max_date = decode_date(self.latestDate_entry.text())

			if self.leastExpense_entry.text() != '':
				try:
					min_expense = float(self.leastExpense_entry.text().replace('-',''))*-1
				except ValueError:
					self.errors['Smallest Expense'] = self.nonnumeric_error

			if self.greatestExpense_entry.text() != '':
				try:
					max_expense = float(self.greatestExpense_entry.text().replace('-',''))*-1
				except ValueError:
					self.errors['Greatest Expense'] = self.nonnumeric_error

			if self.leastRevenue_entry.text() != '':
				try:
					min_revenue = float(self.leastRevenue_entry.text().replace('+',''))
				except ValueError:
					self.errors['Smallest Revenue'] = self.nonnumeric_error

			if self.greatestRevenue_entry.text() != '':
				try:
					max_revenue = float(self.greatestRevenue_entry.text().replace('+',''))
				except ValueError:
					self.errors['Smallest Revenue'] = self.nonnumeric_error


			if len(self.categAccepted_entry.selectedItems()) > 0:
				categories = [item.text() for item in self.categAccepted_entry.selectedItems()]

			if len(self.partyAccepted_entry.selectedItems()) > 0:
				parties = [item.text() for item in self.partyAccepted_entry.selectedItems()]

		elif self.categories_is_selected:
			table = 'MajorCategories'
		else:
			table = 'SecondParties'

		if len(self.errors) == 0:
			self.error_area.hide()

			self.loaded_records = self.search_access.data_search(table, substring, ledger, min_date, max_date, categories, parties, min_expense, max_expense, min_revenue, max_revenue, sortby_categ, sortby_party)

			# > Switching out the widgets to reflect new search-results.
			if self.transaction_results in self.search_results.children():
				self.search_results.shape.removeWidget(self.transaction_results)
				self.transaction_results.hide()
			if self.category_results in self.search_results.children():
				self.search_results.shape.removeWidget(self.category_results)
				self.category_results.hide()
			if self.party_results in self.search_results.children():
				self.search_results.shape.removeWidget(self.party_results)
				self.party_results.hide()

			if self.transaction_is_selected:
				# if self.totals_area in self.search_results.children():
				self.search_results.shape.removeWidget(self.totals_area)
				self.transaction_results = TransactionDisplayTable(self, self.search)
				self.transaction_results.process_raw_records(self.loaded_records)
				self.transaction_results.populate()
				self.update_totals()
				self.search_results.shape.addWidget(self.totals_area)
				self.search_results.shape.addWidget(self.transaction_results)
				self.transaction_results.show()

			elif self.categories_is_selected:
				# if self.totals_area in self.search_results.children():
				self.search_results.shape.removeWidget(self.totals_area)
				self.category_results = CategoryDisplayTable(self, self.search)
				self.category_results.process_raw_records(self.loaded_records)
				self.category_results.populate()
				self.search_results.shape.addWidget(self.category_results)
				self.category_results.show()

			else:
				# if self.totals_area in self.search_results.children():
				self.search_results.shape.removeWidget(self.totals_area)
				self.party_results = PartyDisplayTable(self, self.search)
				self.party_results.process_raw_records(self.loaded_records)
				self.party_results.populate()
				self.search_results.shape.addWidget(self.party_results)
				self.party_results.show()

			self.search_results.setFixedWidth(self.width() * 0.7)
			# self.results_table.setFixedHeight(self.search_results.height())
			self.search_results.show()
			# if self.transaction_is_selected:
			# 	self.search_results.shape.addWidget(self.totals_area)
			# self.search_results.shape.addWidget(self.transaction_results)
			# self.transaction_results.process_raw_records(self.loaded_records)
			# self.transaction_results.populate()

			# self.input_error_columns.setFixedHeight((self.height() - self.searchbuttons_area.height())*0.55)

		else:
			self.error_area.show()
			error_text = ""
			for errorpair in self.errors.items():
				error_text += f"\u2022 Error in {errorpair[0]}: {errorpair[1]}\n"

			error_text = error_text.rstrip()

			self.error_display.setPlainText(error_text)
			self.errors.clear()

	@Slot()
	def open_reports_menu(self):
		report_dialog = ReportDialog()
		report_dialog.exec()
		return