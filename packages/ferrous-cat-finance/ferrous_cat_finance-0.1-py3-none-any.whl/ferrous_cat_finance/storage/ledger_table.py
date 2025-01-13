import typing as typ
from storage.Database import SQL_Connection
from data.ledger_object import Ledger

LEDGER_QENV = SQL_Connection()

class LedgerTable:
	def __init__(self):
		pass

	def create(self, ledger:Ledger, isTestdata=False) -> int:
		columns = '(Title'
		values = '(?'
		params = [ledger.title]

		if hasattr(ledger, 'description'):
			columns += ', Description'
			values += ',?'
			params.append(ledger.description)

		if isTestdata:
			columns += ', Is_Testdata'
			values += ', True'

		columns += ')'
		values += ')'

		updateStatement = f"INSERT INTO Ledgers {columns} values {values}"
		print('update', updateStatement)
		LEDGER_QENV.edit.execute(updateStatement, tuple(params))

		LEDGER_QENV.edit.connection.commit()
		return LEDGER_QENV.edit.lastrowid


	def mapToLedger(self, record:list) -> Ledger:
		ledger = Ledger()
		ledger.rowID = record[0]
		ledger.title = record[1]
		ledger.description = record[2]
		return ledger


	def getAll(self) -> list[Ledger]:
		LEDGER_QENV.edit.execute("""
			SELECT RowID, * FROM Ledgers""")

		return [self.mapToLedger(record) for record in LEDGER_QENV.edit.fetchall()]


	def title_lookup(self, rowID:int) -> str:
		LEDGER_QENV.edit.execute("""
			SELECT Title FROM Ledgers
			WHERE RowID == ?""",
			rowID)

		return LEDGER_QENV.edit.fetchall()[0]