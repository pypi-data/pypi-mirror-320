import typing as typ

from storage.Database import SQL_Connection, SETTINGS
from data.Transaction import Transaction

QENV = SQL_Connection()

class TransactionTable:
	def get(self, rowID) -> Transaction:
		QENV.edit.execute(f'SELECT RowID, * FROM Transactions where RowID=?', (rowID,))
		return self.mapToTransaction(QENV.edit.fetchone())

	def delete(self, rowID):
		QENV.edit.execute(f'Delete FROM Transactions where RowID=?', (rowID,))
		QENV.access.commit()

	def update(self, transaction:Transaction):
		#should do this and throw exception if fails
		#errors = transaction.validate()

		query = f'update Transactions set Date=?, Item_Name=?, Balance_Effect=?, Major_Category=?, Ledger_ID=?'

		params = [transaction.date, transaction.itemName]
		if (hasattr(transaction, 'revenue')):
			params.append(transaction.revenue)
		else:
			params.append(abs(transaction.expense)*-1)

		params.append(transaction.categoryId)

		params.append(transaction.ledgerID)


		if hasattr(transaction, 'description'):
			query += ", Description=?"
			params.append(transaction.description)
		else:
			query += ", Description=NULL"

		if hasattr(transaction, 'secondPartyId'):
			query += ", Second_Party=?"
			params.append(transaction.secondPartyId)
		else:
			query += ", Second_Party=NULL"

		query += f' where RowID=?'
		params.append(transaction.rowID)

		print('update', query)
		QENV.edit.execute(query, tuple(params))

		QENV.edit.connection.commit()


	def create(self, transaction:Transaction, isTestData = False) -> int:
		#should do this and throw exception if fails
		#errors = transaction.validate()

		columns = "(Date, Item_Name, Balance_Effect, Major_Category, Ledger_ID"
		values = "(?, ?, ?, ?, ?"
		params = [transaction.date, transaction.itemName]
		if (hasattr(transaction, 'revenue')):
			params.append(transaction.revenue)
		else:
			params.append(abs(transaction.expense)*-1)

		params.append(transaction.categoryId)

		params.append(transaction.ledgerID)

		if hasattr(transaction, 'description'):
			columns += ", Description"
			values += ", ?"
			params.append(transaction.description)
		if hasattr(transaction, 'secondPartyId'):
			columns += ", Second_Party"
			values += ", ?"
			params.append(transaction.secondPartyId)
		if isTestData:
			columns += ", Is_Testdata"
			values += ", True"
		columns += ")"
		values += ")"
		updateStatement = f"INSERT INTO Transactions {columns} values {values}"
		print('update', updateStatement)
		QENV.edit.execute(updateStatement, tuple(params))

		QENV.edit.connection.commit()
		return QENV.edit.lastrowid


	def getRecent(self, count=SETTINGS['initial_load_num'], ledger:int=None) -> list[Transaction]:
		transactions = []

		ledger_select = ''
		arguments = tuple()
		if ledger is not None:
			ledger_select = f'WHERE Ledger_ID == ?'
			arguments = (ledger,)

		QENV.edit.execute(f"""
			SELECT RowID, * FROM Transactions
				{ledger_select}
				ORDER BY Date DESC
				LIMIT {count}""",
			arguments)

		records = QENV.edit.fetchall()
		for record in records:
			transactions.append(self.mapToTransaction(record))

		return transactions


	def mapToTransaction(self, record:list) -> Transaction:
		transaction = Transaction()
		transaction.rowID = record[0]
		transaction.date = record[1]
		transaction.itemName = record[2]
		balance_effect = record[3]
		if balance_effect >= 0:
			transaction.revenue = balance_effect
		else:
			transaction.expense = balance_effect
		transaction.categoryId = record[4]
		transaction.ledgerID = record[5]
		transaction.description = record[6]
		transaction.secondPartyId = record[7]
		return transaction


	def check_existence(rowID: int) -> bool:
		QENV.edit.execute("""
			SELECT RowID FROM Transactions""")

		extant = [row[0] for row in QENV.edit.fetchall()]
		exists = False
		if rowID in extant:
			exists = True

		return exists