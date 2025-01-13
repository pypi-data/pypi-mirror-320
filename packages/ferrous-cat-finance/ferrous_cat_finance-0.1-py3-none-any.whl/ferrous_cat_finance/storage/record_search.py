import typing as typ
from storage.TransactionTable import *
from storage.CategoryTable import *
from storage.SecondPartyTable import *
from storage.Database import SQL_Connection, FetchOutput
from sqlite3 import Error as sqlerror

SEARCHER_QENV = SQL_Connection()

class Searcher:
	def __init__(self):
		pass

	def data_search(self,
		table:typ.Literal['Transactions','SecondParties','MajorCategories'],
		text_content:str=None,	# Has name/title/description containing this substring. (All tables.)
		ledger:int=None,	# Is marked as part of ledger with this RowID. (Transactions only.)
		date_min:str=None,	# Has date equal to or after this. (Transactions only.)
		date_max:str=None,	# Has date equal to or earlier than this. (Transactions only).
		accepted_categories:list[str]=None,	# Has one of these categories. (Transactions only.)
		accepted_parties:list[str]=None,	# Has one of these second-parties. (Transactions only.)
		expense_min:float=None,	# Has Expense with an absolute value of equal to or greater than this. (Transactions only.)
		expense_max:float=None,	# Has Expense with an absolute value of equal to or less than this. (Transactions only.)
		revenue_min:float=None,	# Has Revenue with an absolute value of equal to or greater than this. (Transactions only.)
		revenue_max:float=None,	# Has Revenue with an absolute value of equal to or less than this. (Transactions only.)
		sortby_categ:bool=False,# Sort results by category. (Transactions only.)
		sortby_party:bool=False
		) -> list[Transaction]|list[Category]|list[SecondParty]:

		self.tablename = table
		base_query = f'SELECT RowID, * FROM {self.tablename}'
		constraints = []
		arguments = []

		match table:
			case 'Transactions':
				text_constraint = 'lower(Item_Name) LIKE ? OR lower(Description) LIKE ?'
			case 'MajorCategories':
				text_constraint = 'lower(Title) LIKE ? OR lower(Description) LIKE ?'
			case 'SecondParties':
				text_constraint = 'lower(Name) LIKE ? OR lower(Description) LIKE ?'

		ledger_constraint = 'Ledger_ID == ?'
		mindate_constraint = 'date(Date) >= ?'
		maxdate_constraint = 'date(Date) <= ?'
		categories_constraint = 'Major_Category IN (SELECT RowID FROM MajorCategories WHERE Title IN (##))'
		parties_constraint = 'Second_Party IN (SELECT RowID FROM SecondParties WHERE Name IN (##))'
		minexpense_constraint = 'Balance_Effect < ?'
		maxexpense_constraint = 'Balance_Effect < 0 AND Balance_Effect > ?'
		minrevenue_constraint = 'Balance_Effect > ?'
		maxrevenue_constraint = 'Balance_Effect > 0 AND Balance_Effect < ?'

		if text_content is not None:
			constraints.append(text_constraint)

		if table == 'Transactions':

			if ledger is not None:
				constraints.append(ledger_constraint)

			if date_min is not None:
				constraints.append(mindate_constraint)

			if date_max is not None:
				constraints.append(maxdate_constraint)

			if accepted_categories is not None:
				constraints.append(categories_constraint)

			if accepted_parties is not None:
				constraints.append(parties_constraint)

			if expense_min is not None:
				constraints.append(minexpense_constraint)

			if expense_max is not None:
				constraints.append(maxexpense_constraint)

			if revenue_min is not None:
				constraints.append(minrevenue_constraint)

			if revenue_max is not None:
				constraints.append(maxrevenue_constraint)


		# >	Constructing Query.
		full_query = base_query
		revenue_part = None
		expense_part = None

		if len(constraints) > 0:
			print(f"Searcher.search(), constraints = {constraints}")
			full_query += '\n\tWHERE @@'

			if text_constraint in constraints:
				full_query = full_query.replace('@@', f"({text_constraint})")
				arguments.append(f'%{text_content.lower()}%')
				arguments.append(f'%{text_content.lower()}%')

				constraints.remove(text_constraint)
				if len(constraints) > 0:
					full_query += ' AND (@@)'

			if ledger_constraint in constraints:
				full_query = full_query.replace('@@', ledger_constraint)
				arguments.append(ledger)

				constraints.remove(ledger_constraint)
				if len(constraints) > 0:
					full_query += ' AND (@@)'

			if mindate_constraint in constraints and maxdate_constraint in constraints:
				full_query = full_query.replace('@@', f"({mindate_constraint} AND {maxdate_constraint})")
				arguments.append(date_min)
				arguments.append(date_max)

				constraints.remove(mindate_constraint)
				constraints.remove(maxdate_constraint)
				if len(constraints) > 0:
					full_query += ' AND (@@)'

			elif mindate_constraint in constraints:
				full_query = full_query.replace('@@', mindate_constraint)
				arguments.append(date_min)

				constraints.remove(mindate_constraint)
				if len(constraints) > 0:
					full_query += ' AND (@@)'

			elif maxdate_constraint in constraints:
				full_query = full_query.replace('@@', maxdate_constraint)
				arguments.append(date_max)

				constraints.remove(maxdate_constraint)
				if len(constraints) > 0:
					full_query += ' AND (@@)'

			if categories_constraint in constraints:
				full_query = full_query.replace('@@', categories_constraint)
				categ_bindings = ('?,' * len(accepted_categories)).rstrip(',')
				full_query = full_query.replace('##', categ_bindings)
				for item in accepted_categories:
					arguments.append(item)

				constraints.remove(categories_constraint)
				if len(constraints) > 0:
					full_query += " AND (@@)"

			if parties_constraint in constraints:
				full_query = full_query.replace('@@', parties_constraint)
				party_bindings = ('?,' * len(accepted_parties)).rstrip(',')
				full_query = full_query.replace('##', party_bindings)
				for item in accepted_parties:
					arguments.append(item)

				constraints.remove(parties_constraint)
				if len(constraints) > 0:
					full_query += " AND (@@)"

			if minrevenue_constraint in constraints and maxrevenue_constraint in constraints:
				revenue_part = f"({minrevenue_constraint} AND {maxrevenue_constraint})"
				arguments.append(revenue_min)
				arguments.append(revenue_max)
				constraints.remove(minrevenue_constraint)
				constraints.remove(maxrevenue_constraint)

			elif minrevenue_constraint in constraints:
				revenue_part = minrevenue_constraint
				arguments.append(revenue_min)
				constraints.remove(minrevenue_constraint)

			elif maxrevenue_constraint in constraints:
				revenue_part = maxrevenue_constraint
				arguments.append(revenue_max)
				constraints.remove(maxrevenue_constraint)

			if minexpense_constraint in constraints and maxexpense_constraint in constraints:
				expense_part = f"({minexpense_constraint} AND {maxexpense_constraint})"
				arguments.append(expense_min)
				arguments.append(expense_max)
				constraints.remove(minexpense_constraint)
				constraints.remove(maxexpense_constraint)

			elif minexpense_constraint in constraints:
				expense_part = minexpense_constraint
				arguments.append(expense_min)
				constraints.remove(minexpense_constraint)

			elif maxexpense_constraint in constraints:
				expense_part = maxexpense_constraint
				arguments.append(expense_max)
				constraints.remove(maxexpense_constraint)

			if revenue_part is not None and expense_part is not None:
				full_query = full_query.replace('@@', f"{revenue_part} OR {expense_part}")
			elif revenue_part is not None:
				full_query = full_query.replace('@@', revenue_part)
			elif expense_part is not None:
				full_query = full_query.replace('@@', expense_part)


		# - Doing ORDER BY clause.
		full_query += '\n\tORDER BY @@'

		if self.tablename == 'Transactions':
			if sortby_categ or sortby_party:
				if sortby_categ and sortby_party:
					full_query = full_query.replace('@@', 'Major_Category, Second_Party, Date DESC')
				elif sortby_categ:
					full_query = full_query.replace('@@', 'Major_Category, Date DESC')
				else:
					full_query = full_query.replace('@@', 'Second_Party, Date DESC')
			else:
				full_query = full_query.replace('@@', 'Date DESC')

		elif self.tablename == 'SecondParties':
			full_query = full_query.replace('@@', 'Name ASC')

		else:
			full_query = full_query.replace('@@', 'Title ASC')

		# - Running query.
		print(f"Searcher.search(), full_query:\n\t{full_query}")
		print(f"Searcher.search(), arguments:\n\t{arguments}")
		# try:
		SEARCHER_QENV.edit.execute(full_query, tuple(arguments))
		# except sqlerror as err:
		# 	print(err)

		records = SEARCHER_QENV.edit.fetchall()
		if self.tablename == 'Transactions':
			transact_access = TransactionTable()
			return [transact_access.mapToTransaction(record) for record in records]

		elif self.tablename == 'SecondParties':
			party_access = SecondPartyTable()
			return[party_access.mapToSecondParty(record) for record in records]

		elif self.tablename == 'MajorCategories':
			categ_access = CategoryTable()
			return[categ_access.mapToCategory(record) for record in records]

		# else:
		# 	ledger_access = LedgerTable()
		# 	return[ledger_access.mapToLedger(record) for record in records]
