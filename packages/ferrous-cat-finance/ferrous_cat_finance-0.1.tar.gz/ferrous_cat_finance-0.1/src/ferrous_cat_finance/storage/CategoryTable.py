import json, typing as typ

from storage.Database import SQL_Connection
from data.Category import Category

CATEGORY_QENV = SQL_Connection()

class CategoryTable:

	def get(self, rowID) -> Category:
		CATEGORY_QENV.edit.execute(f'SELECT RowID, * FROM MajorCategories where RowID=?', (rowID,))
		return self.mapToCategory(CATEGORY_QENV.edit.fetchone())
	
	def update(self, category:Category):
		#should do this and throw exception if fails
		#errors = transaction.validate()

		query = f'update MajorCategories set Title=?'

		params = [category.title,]

		if hasattr(category, 'description'):
			query += ", Description=?"
			params.append(category.description)
		else:
			query += ", Description=NULL"

		query += f' where RowID=?'
		params.append(category.rowID)

		print('update', query)
		CATEGORY_QENV.edit.execute(query, tuple(params))
		CATEGORY_QENV.edit.connection.commit()


	def createFromTitle(self, title: str, isTestData = False) -> int:
		category = Category()
		category.title = title
		return self.create(category, isTestData)

	def create(self, category:Category, isTestData = False) -> int:
		#should do this and throw exception if fails
		#errors = transaction.validate()

		# build query based on
		columns = "(Title"
		values = "(?"
		params = [category.title]
		if hasattr(category, 'description'):
			columns = columns + ", Description"
			values = values + ", ?"
			params.append(category.description)
		if isTestData:
			columns = columns + ", Is_Testdata"
			values = values + ", True"
		columns = columns + ")"
		values = values +")"

		updateStatement = f"INSERT INTO MajorCategories {columns} values {values}"
		print('create category', updateStatement)
		CATEGORY_QENV.edit.execute(updateStatement, tuple(params))

		CATEGORY_QENV.edit.connection.commit()
		return CATEGORY_QENV.edit.lastrowid

	def getAll(self) -> list[Category]:
		categories = []
		CATEGORY_QENV.edit.execute(f"""
			SELECT RowID, * FROM MajorCategories
				ORDER BY Title""")

		records = CATEGORY_QENV.edit.fetchall()
		for record in records:
			categories.append(self.mapToCategory(record))

		return categories

	def mapToCategory(self,record:typ.Any) -> Category:
		category = Category()
		category.rowID = record[0]
		category.title = record[1]
		category.description = record[2]
		return category


	def title_lookup(self, row_id:int) -> str:
		CATEGORY_QENV.edit.execute(f"""
			SELECT Title FROM {"MajorCategories"}
				WHERE RowID = {row_id}""")

		result = CATEGORY_QENV.edit.fetchall()

		if len(result) == 0:
			raise ValueError('title_lookup() (a non-user-facing method) was called without a matching record to return.')

		return result[0][0]

