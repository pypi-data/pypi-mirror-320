from storage.Database import SQL_Connection, using_testdata, TABLE_LIST, sqlite3, MAIN_TABLE
from storage.CategoryTable import CategoryTable
from storage.SecondPartyTable import SecondPartyTable
from storage.TransactionTable import TransactionTable
from storage.ledger_table import LedgerTable
from data.Category import Category
from data.SecondParty import SecondParty
from data.Transaction import Transaction
from data.ledger_object import Ledger


TABLE_SETUP_SCRIPT = 'db-creation.sql'

QENV = SQL_Connection()

def import_sql_script(filename):
	file = open(filename, 'r')
	script_string = ''
	for line in file:
		script_string += line
	file.close()

	# print(f'\t DEBUG:\n{script_string}')

	return script_string


def insert_testdata():
	QENV.edit.execute(f"""
		SELECT Is_Testdata FROM {MAIN_TABLE}""")
	test_presence = [result[0] for result in QENV.edit.fetchall()]

	if 1 not in test_presence:	# No records are marked as test-records;
		import feline_values

		categoryTable = CategoryTable()
		categoryDict = dict()
		for record in feline_values.FELINE_CATEG:
			category = Category()
			category.title = record['Title']
			category.description = record['Description']
			rowID = categoryTable.create(category, True)
			categoryDict[category.title] = rowID
		print('categoryDict', categoryDict)

		secondPartyTable = SecondPartyTable()
		secondPartyDict = dict()
		for record in feline_values.FELINE_PARTIES:
			secondParty = SecondParty()
			secondParty.email = record['Email']
			secondParty.name = record['Name']
			secondParty.notes = record['Notes']
			secondParty.phone = record['Phone']
			rowID = secondPartyTable.create(secondParty, True)
			secondPartyDict[secondParty.name] = rowID
		print('secondPartyDict', secondPartyDict)

		transactionTable = TransactionTable()
		for record in feline_values.FELINE_TRANSACT:
			transaction = Transaction()
			transaction.categoryId = categoryDict[record['Major_Category']]
			transaction.ledgerID = ledger_dict[record['Ledger']]
			transaction.date = record['Date']
			transaction.description = record['Description']
			if record['Balance_Effect'] > 0:
				transaction.revenue = record['Balance_Effect']
			else:
				transaction.expense = record['Balance_Effect']
			transaction.itemName = record['Item_Name']
			transaction.secondPartyId = secondPartyDict[record['Second_Party']]
			transactionTable.create(transaction, True)

	# test_select_all(MAIN_TABLE)
	return



def test_select_all(table_name:str):
	raw_data = QENV.edit.execute(f"""
		SELECT RowID, * FROM {table_name}""")

	data_output = ''
	for line in raw_data:
		line_string = ''
		for item in line:
			line_string += str(item) + ' | '
		line_string = line_string.rstrip(' | ')
		line_string += '\n'
		data_output += line_string

	print(data_output)
	return


def delete_testdata():
	"""
	- delete_testdata() removes all of the records added by the
	test-data-script from the database before the program ends.
	"""
	if using_testdata:
		try:
			for table in TABLE_LIST:
				QENV.edit.execute(f"""
					DELETE FROM {table}
						WHERE Is_Testdata = 1""")
		except sqlite3.Error as sql_error:
			print(sql_error)

	return

def setup_testdata():
	SETUP_TESTING = (False,)	#@ Remove this for finished version.
	if SETUP_TESTING[0]:
		print('WARNING: SETUP_TESTING is set to True; tables are being cleared on each startup.')
		current_tables = QENV.check_table_presence()
		try:
			for table in current_tables:
				print(f"dropping table {table}")
				QENV.edit.execute(f"""
					DROP TABLE {table}""")
		except sqlite3.Error as sql_error:
			print(sql_error)


	# -	Check whether database-tables have been initialized.
	table_readout = QENV.check_table_presence()
	if len(table_readout) == 0:
		# - If not, run setup-script.
		try:	#@ Don't want to be running try/except in the finished version.
			QENV.edit.executescript(import_sql_script(TABLE_SETUP_SCRIPT))

			import scripts.predefinitions	# @ TODO: Move this out of TestData.

			ledger_table = LedgerTable()
			ledger_dict = {}
			for record in scripts.predefinitions.PREDEF_LEDGERS:
				ledger = Ledger()
				ledger.title = record['Title']
				ledger.description = record['Description']
				ledger_dict[ledger.title] = ledger_table.create(ledger, True)
			print(f'ledger_dict: {ledger_dict}')

		except sqlite3.Error as sql_error:
			print(sql_error)

	if using_testdata:
		insert_testdata()