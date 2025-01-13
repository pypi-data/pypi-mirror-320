import json, typing as typ

from storage.Database import SQL_Connection
from data.SecondParty import SecondParty

PARTIES_QENV = SQL_Connection()

class SecondPartyTable:

	def get(self, rowID) -> SecondParty:
		PARTIES_QENV.edit.execute(f'SELECT RowID, * FROM SecondParties where RowID=?', (rowID,))
		return self.mapToSecondParty(PARTIES_QENV.edit.fetchone())
	
	def update(self, secondParty:SecondParty):
		#should do this and throw exception if fails
		#errors = transaction.validate()

		query = f'update SecondParties set Name=?'

		params = [secondParty.name,]

		if hasattr(secondParty, 'phone'):
			query += ", Phone=?"
			params.append(secondParty.phone)
		else:
			query += ", Phone=NULL"

		if hasattr(secondParty, 'email'):
			query += ", Email=?"
			params.append(secondParty.email)
		else:
			query += ", Email=NULL"

		if hasattr(secondParty, 'notes'):
			query += ", Notes=?"
			params.append(secondParty.notes)
		else:
			query += ", Notes=NULL"


		query += f' where RowID=?'
		params.append(secondParty.rowID)

		print('update', query)
		PARTIES_QENV.edit.execute(query, tuple(params))
		PARTIES_QENV.edit.connection.commit()	

	def createFromName(self, name: str, isTestData = False) -> int:
		secondParty = SecondParty()
		secondParty.name = name
		return self.create(secondParty, isTestData)
		
	def create(self, secondParty:SecondParty, isTestData = False) -> int:
		#should do this and throw exception if fails
		#errors = transaction.validate()

		#build query
		columns = "(Name"
		values = "(?"
		params = [secondParty.name]
		if hasattr(secondParty, 'phone'):
			columns = columns + ", Phone"
			values = values + ", ?"
			params.append(secondParty.phone)
		if hasattr(secondParty, 'email'):
			columns = columns + ", Email"
			values = values + ", ?"
			params.append(secondParty.email)
		if hasattr(secondParty, 'notes'):
			columns = columns + ", Notes"
			values = values + ", ?"
			params.append(secondParty.notes)
		if isTestData:
			columns = columns + ", Is_Testdata"
			values = values + ", ?"
			params.append(True)
		columns = columns + ")"
		values = values + ")"
		updateStatement = f"INSERT INTO SecondParties {columns} values {values}"
		print('create secondParty', updateStatement)
		PARTIES_QENV.edit.execute(updateStatement, tuple(params))

		PARTIES_QENV.edit.connection.commit()
		return PARTIES_QENV.edit.lastrowid

	def getAll(self) -> list[SecondParty]:
		categories = []
		PARTIES_QENV.edit.execute(f"""
			SELECT RowID, * FROM SecondParties
				ORDER BY Name""")

		records = PARTIES_QENV.edit.fetchall()
		for record in records:
			categories.append(self.mapToSecondParty(record))

		return categories

	def mapToSecondParty(self, record:typ.Any) -> SecondParty:
		secondParty = SecondParty()
		secondParty.rowID = record[0]
		secondParty.name = record[1]
		secondParty.phone = record[2]
		secondParty.email = record[3]
		secondParty.notes = record[4]
		return secondParty


	def name_lookup(self, row_id:int) -> str:
		PARTIES_QENV.edit.execute(f"""
			SELECT Name FROM {"SecondParties"}
				WHERE RowID = {row_id}""")

		result = PARTIES_QENV.edit.fetchall()

		if len(result) == 0:
			raise ValueError('name_lookup() (a non-user-facing method) was called without a matching record to return.')

		return result[0][0]



