from ui.Common import tr, MONTH_NOTATION
from data.Transaction import Transaction
from data.pdf_export import *
from storage.CategoryTable import CategoryTable
import copy

LABEL_ROW = [[tr('Category'),'01','02','03','04','05','06','07','08','09','10','11','12',tr('Total')]]
SPACER = [['','','','','','','','','','','','','','']]


class LedgerSection:
	def __init__(self, dataset:list[Transaction], ledger_info:tuple[int,str]):
		self.categ_access = CategoryTable()

		self.id = ledger_info[0]
		self.section_name = ledger_info[1]
		self.dataset = [transact for transact in dataset if transact.ledgerID == self.id]

		self.full_grid = []

		self.revenue_categories = []
		self.expense_categories = []
		self.section_label = [['',tr(self.section_name.upper()),'','','','','','','','','','','','']]
		self.revenue_grid = [[tr('REVENUE:'),'','','','','','','','','','','','','']]
		self.expense_grid = [[tr('EXPENSES:'),'','','','','','','','','','','','','']]
		self.section_totals = [[tr('NET CASH:'),'','','','','','','','','','','','','']]

		self.DATA_START_ROW = 1
		# self.bold_rows = [0, 1]
		# self.bold_cells = []
		for record in self.dataset:
			if hasattr(record, 'revenue'):
				if record.categoryId not in self.revenue_categories:
					self.revenue_categories.append(record.categoryId)
			else:
				if record.categoryId not in self.expense_categories:
					self.expense_categories.append(record.categoryId)

		for categ in self.revenue_categories:
			self.revenue_grid.append([categ, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00])

		for categ in self.expense_categories:
			self.expense_grid.append([categ, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00])

		# - Beginning population of the data-grids.
		self.populate_datagrid(self.revenue_grid)
		self.populate_datagrid(self.expense_grid)

		self.total_for_categories(self.revenue_grid)
		self.total_for_categories(self.expense_grid)

		self.total_for_months(self.revenue_grid)
		self.total_for_months(self.expense_grid)

		self.name_categories(self.revenue_grid)
		self.name_categories(self.expense_grid)

		self.total_for_section()

		# # - Set the total for the revenues to be bolded.
		# self.bold_cells.append( (len(self.revenue_grid[0]), len(self.revenue_grid)) )

		# # - Set the titlerow for expenses to be bolded.
		# self.bold_rows.append(len(self.revenue_grid)+2)

		# # - Set the total for the expenses to be bolded.
		# self.bold_cells.append( (len(self.revenue_grid[0]), (len(self.revenue_grid) + len(self.expense_grid) - 1)) )

		self.full_grid = [] + self.section_label + self.revenue_grid + self.expense_grid + self.section_totals + SPACER

		return


	def populate_datagrid(self, grid_object:list[list]):

		for row in grid_object[self.DATA_START_ROW:]:
			category = row[0]

			for month in LABEL_ROW[0][1:13]:
				month_index = LABEL_ROW[0].index(month)

				for record in self.dataset:
					if record.categoryId == category and record.date.split('-')[1] == month:
						if grid_object == self.revenue_grid and hasattr(record, 'revenue'):
							row[month_index] += record.revenue
						elif grid_object == self.expense_grid and hasattr(record, 'expense'):
							row[month_index] += record.expense

			# - Replacing empty category-row with one populated with data.
			original_row_index = grid_object.index([orig_row for orig_row in grid_object if orig_row[0] == row[0]][0])
			grid_object[original_row_index] = row

		return


	def total_for_categories(self, grid_object:list[list]):
		for row in grid_object[self.DATA_START_ROW:]:
			row.append( round(sum(row[1:]), 2) )
		return


	def total_for_months(self, data_object:list[list]):
		total_row = ['Total']
		for col in range(1,13):
			total_row.append( round(sum([row[col] for row in data_object[self.DATA_START_ROW:]]), 2) )

		total_row.append( round(sum(total_row[1:]), 2) )

		data_object.append(total_row)

		return

	def total_for_section(self):
		revenues = self.revenue_grid[-1][1:13]
		expenses = self.expense_grid[-1][1:13]
		balances = ['']

		for x in range(len(revenues)):
			balances.append(round(revenues[x] - abs(expenses[x]), 2))	# @ TODO: Shouldn't use abs() here.

		balances.append(round(sum(balances[1:]), 2))

		self.section_totals.append(balances)

		return


	def name_categories(self, data_object:list[list]):
		for row in range(len(data_object)):
			if type(data_object[row][0]) == int:
				data_object[row][0] = self.categ_access.title_lookup(data_object[row][0])
		return


class ReportOrganizer:
	"""
	- Takes a list of Transactions and processes them into a
	CSV-file that will be accepted as input for FPDF.
	"""
	def __init__(self,
			dataset:list[Transaction],
			year:str,
			ledger_info:list[tuple[int,str]]):	#@@@: Does ReportOrganizer know the ledgerID? It should.

		self.dataset = dataset
		self.document_title = ''
		self.sections:list[LedgerSection] = []

		self.label_row = copy.deepcopy(LABEL_ROW)
		self.grand_totals = [[tr('GRAND TOTAL:')]]

		# - Generate report-sections, divided by ledger.
		for infopair in ledger_info:
			self.sections.append(LedgerSection(dataset, infopair))

		# - Finalizing display-values.
		self.name_months()
		self.total_for_report()

		# - Compile grid for full report.
		self.full_report = copy.deepcopy(self.label_row)
		for section in self.sections:
			self.full_report += section.full_grid
		self.full_report += self.grand_totals

		# - Call for PDF-creation.
		if len(self.sections) > 1:
			self.document_title = tr('All Ledgers')
		else:
			self.document_title = tr(self.sections[0].section_name)

		out_pdf = CashflowPDF(f'Cashflow-Report: {year}, {self.document_title}')
		out_pdf.generate(self.full_report)

		return


	def name_months(self):
		for col in range(len(LABEL_ROW[0])):
			if self.label_row[0][col] in MONTH_NOTATION.keys():
				self.label_row[0][col] = MONTH_NOTATION[self.label_row[0][col]]
		return


	def total_for_report(self):
		totals = [0.0]*12

		for x in range(len(totals)):
			for section in self.sections:
				totals[x] += section.section_totals[1][x+1]

		totals = [round(val, 2) for val in totals]

		for val in totals:
			self.grand_totals[0].append(val)
		self.grand_totals[0].append(round(sum(totals), 2))

		return