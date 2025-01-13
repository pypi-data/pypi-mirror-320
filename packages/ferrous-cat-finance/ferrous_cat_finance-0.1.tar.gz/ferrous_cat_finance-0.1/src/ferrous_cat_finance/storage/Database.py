import sqlite3, json, typing as typ

SETTINGS_FILE = 'pers_pref.json'
SETTINGS:dict[
	typ.Literal[
		"main_font",
		"main_font_size",
		"head_font",
		"head_font_size",
		"text-highlight-color",
		"display_line_count",
		"openquote_character",
		"closequote_character",
		"initial_load_num",
		"default_min_year",
		"do_alt_power_sep",
		"do_american_date_format",
		"confirm_new_record",
		"mixed_cashflow_allowed"],
	typ.Any] = json.load(open(SETTINGS_FILE, 'r', encoding='utf8'))
lQ = SETTINGS['openquote_character']
rQ = SETTINGS['closequote_character']

DB_NAME = 'ferrous-cat-finance.db'
TABLENAME_PARTY = 'SecondParties'
TABLENAME_MAJCAT = 'MajorCategories'
TABLENAME_SUBCAT = 'SubCategories'
TABLENAME_TRANSACT = 'Transactions'

TYPE_LOCALIZER = {
	'INTEGER' : int,
	'REAL' : float,
	'TEXT' : str}

def global_get_headers(cursor:sqlite3.Cursor) -> list[str]:
	fieldnames = [col_id[0] for col_id in cursor.description]
	return fieldnames


FetchOutput: typ.TypeAlias = list[list[typ.Any]]


### Global toggles
using_testdata = False

### CLASSES ####################################################
class WriteErrors:
	def __init__(self):
		self.ERROR_MESSAGES = {
			# -	Text-messages; are simply displayed in a
			#	display-widget.
			'invalid null': 'You have left at least one required field blank; please fill the highlighted fields.',
			'non-numeric': 'You have entered a value which is not a number into either Expense or Revenue.',
			'unexpected numeric': 'You have entered a number in a field which was expecting text (@FIELD). Is this correct?',
			'future date': 'You have entered a transaction with a date in the future. Is this correct?',

			'missing parent, party': f'The second-party you entered, {lQ}@ATTEMPTED_ENTRY{rQ}, is not an existing second-party. Would you like to create a new second-party named {lQ}@ATTEMPTED_ENTRY{rQ}?',
			'missing parent, subcat': f'The subcategory you entered, {lQ}@ATTEMPTED_ENTRY{rQ}, is not an existing subcategory of the {lQ}@MAJ_CAT{rQ} category. Would you like to create a new subcategory named {lQ}@ATTEMPTED_ENTRY{rQ}?',
			'missing parent, majcat': f'The category you entered, {lQ}@ATTEMPTED_ENTRY{rQ}, is not an existing category. Would you like to create a new category named {lQ}@ATTEMPTED_ENTRY{rQ}?'}

		self.ERROR_SEVERITIES = {
			'invalid null': 'critical',
			'non-numeric': 'critical',
			'unexpected numeric': 'minor',
			'future date': 'minor',
			'missing parent, party': 'critical',
			'missing parent, subact': 'critical',
			'missing parent, majcat': 'critical'}

		return

WRITE_ERRORS = WriteErrors()

class TableInfo:
	"""
	- Provides information on a single table in the database.
	"""
	def __init__(self, tablename: str):
		# self.__temp_access = sqlite3.connect(DB_NAME)
		# self.__temp_access.execute("""pragma foreign_keys = ON""")
		# self.__temp_edit = self.__temp_access.cursor()

		self.name = tablename

		# # -	Fields:
		# self.fields = []
		# self.types = {}
		# self.notnulls = {}
		# self.__get_pragma_tableinfo()
		# self.foreign_keys = {}
		# self.__get_foreign_keys()

		# # -	Records:
		# self.id_name_map = self.map_ids_to_names()

		# self.__temp_access.close()
		pass


	# def __get_pragma_tableinfo(self):
	# 	self.__temp_edit.execute(f"""
	# 		SELECT * FROM pragma_table_info('{self.name}')""")

	# 	for group in self.__temp_edit.fetchall():
	# 		fieldname = group[1]
	# 		fieldtype = group[2]
	# 		notnull = bool(group[3] == 1)
	# 		self.fields.append(fieldname)
	# 		self.types[fieldname] = fieldtype
	# 		self.notnulls[fieldname] = notnull
	# 	return


	# def __get_foreign_keys(self):
	# 	self.__temp_edit.execute(f"""
	# 		SELECT * FROM pragma_foreign_key_list('{self.name}')""")
	# 	#\ print(self.name,": ", self.__temp_edit.fetchall(), sep='')
	# 	for group in self.__temp_edit.fetchall():
	# 		parent_table = group[2]
	# 		foreignkey_field = group[3]
	# 		referenced_field = group[4]
	# 		self.foreign_keys[foreignkey_field] = (parent_table, referenced_field)
	# 	return


	# def map_ids_to_names(self) -> dict[int,str]:
	# 	if self.name == TABLENAME_TRANSACT:
	# 		namefield = self.fields[1]	# 'Transactions' has its record-name-field in the second column.
	# 	else:
	# 		namefield = self.fields[0]	# Others have theirs in the first column.

	# 	self.__temp_edit.execute(f"""
	# 		SELECT RowID, {namefield} FROM {self.name}""")

	# 	pairs = {record[0]:record[1] for record in self.__temp_edit.fetchall()}

	# 	return pairs


	def __str__(self):
		return self.name

PARTY_TABLE = TableInfo(TABLENAME_PARTY)
MAJCAT_TABLE = TableInfo(TABLENAME_MAJCAT)
SUBCAT_TABLE = TableInfo(TABLENAME_SUBCAT)
MAIN_TABLE = TableInfo(TABLENAME_TRANSACT)
TABLE_LIST = (PARTY_TABLE, SUBCAT_TABLE, MAJCAT_TABLE, MAIN_TABLE)

class SQL_Connection:
	def __init__(self):
		self.access = sqlite3.connect(DB_NAME)
		self.edit = self.access.cursor()
		return


	def check_table_presence(self) -> list[str]:
		"""
		- Returns a list of the tables currently in the database.
		- Is used for checking whether the database has had its
		tables initially defined at startup; for an iteratable
		list of tablenames, use the global constant TABLE_LIST.
		"""
		self.edit.execute("""
			SELECT name FROM sqlite_master
				WHERE type = 'table'""")
		db_tables = []
		for table in self.edit.fetchall():
			db_tables.append(table[0])

		return db_tables


class SQL_Environment (SQL_Connection):
	def __init__(self):
		super().__init__()
		# - Generating mapping-dictionaries for navigating the
		#	one-to-many relationship between MajorCategories and
		#	SubCategories.
		categ_analysis = self.__initial_categ_relations()
		self.CATEG_GROUPS = categ_analysis[0]	# Lists the child-subcategories of each major category.
		self.CATEG_PARENT_FINDER = categ_analysis[1]	# Maps SubCategories.RowID keys to their parent MajorCategories.RowID values.
		del categ_analysis

		return


	def get_headers(self) -> list[str]:
		"""
		- Returns the fieldnames of the most-recently-run query.
		"""
		return global_get_headers(self.edit)


	def rowID_lookup(self, table:TableInfo, field:str, display_val:float|str) -> int|None:
		self.edit.execute(f"""
			SELECT RowID FROM {table}
			WHERE {field} = {display_val}""")
		result = self.edit.fetchall()
		if len(result) > 1:
			raise ValueError("Error in SQL_Environment.rowID_lookup():\n- Non-unique results found when searching for RowID by display-value.")
		elif len(result == 0):
			return None
		else:
			return result[0]


	def report_generic_categ_activity(self, categ_table:TableInfo) -> dict[int,bool]:
		self.edit.execute(f"""
			SELECT RowID, Active FROM {categ_table}""")
		activity_stats = {row[0]:bool(row[1] == 1) for row in self.edit.fetchall()}
		return activity_stats

	def report_majorcateg_activity(self):
		return self.report_generic_categ_activity(MAJCAT_TABLE)

	def report_subcateg_activity(self):
		return self.report_generic_categ_activity(SUBCAT_TABLE)


	def __initial_categ_relations(self) -> tuple[dict[int,list[int]], dict[int,int]]:
		"""
		- Provides dictionaries describing the one-to-many
		relationship between MajorCategories and SubCategories.
		"""
		self.edit.execute(f"""
			SELECT RowID FROM {MAJCAT_TABLE}""")
		majors = self.edit.fetchall()

		self.edit.execute(f"""
			SELECT RowID, Parent FROM {SUBCAT_TABLE}""")
		subs = self.edit.fetchall()

		child_listing = {record[0]:[] for record in majors}

		for record in subs:
			child_id = record[0]
			parent_id = record[1]
			child_listing[parent_id].append(child_id)

		parent_finder = {record[0]:record[1] for record in subs}

		return (child_listing, parent_finder)


	#\ def generate_placeholds(self, count:int) -> str:
	# 	"""
	# 	- Generates a number of comma-separated SQLite
	# 	placeholders equal to (count). Must be concatenated into
	# 	a .execute() command, which kind of defeats the purpose,
	# 	but...
	# 	"""
	# 	raw = '?,' * count
	# 	proc = raw.rstrip(',')
	# 	return proc


	def unwrap_fields(self, fieldlist:list[str]) -> str:
		"""
		- Takes a list of strings into a comma-separated,
		textual list with parentheses around it, as is the
		syntax for specifying fields within a table in an
		SQLite query.
		"""
		fieldstring = '('
		for fieldname in fieldlist:
			fieldstring += fieldname + ', '
		fieldstring = fieldstring.rstrip(', ')
		fieldstring += ')'

		return fieldstring


	def compile_args(self, arg_pairs:dict[str,typ.Any], indices:dict[str,int]) -> tuple[typ.Any]:
		"""
		- Makes the tuple of values to be passed into a set of
		SQLite placeholders.
		- Takes two arguments;
			- The first is a dict mapping the field-aliases to the
			values to be inserted into those fields.
			- The second is a dict mapping those field-aliases to
			the correct column-positions in the table, so the
			values are entered into the correct fields.
		"""

		values = [None] * len(arg_pairs)

		for field in arg_pairs.keys():
			values[indices[field]] = arg_pairs[field]

		return tuple(values)

# class DataToWrite:
# 	def __init__(self,
# 		input_vals: tuple[typ.Any],
# 		table: TableInfo,
# 		isUpdate: bool):

# 		self.INPUTS = input_vals
# 		self.TABLE = table
# 		self.isUpdate = isUpdate

# 		self.write_vals = self.make_writeDict()

# 		self.ERROR_MESSAGES = {
# 			# -	Text-messages; are simply displayed in a
# 			#	display-widget.
# 			'invalid null': 'You have left at least one required field blank; please fill the highlighted fields.',
# 			'non-numeric': 'You have entered a value which is not a number into either Expense or Revenue.',
# 			'future date': 'You have entered a transaction with a date in the future. Is this correct?',

# 			'missing parent, party': f'The second-party you entered, {lQ}@ATTEMPTED_ENTRY{rQ}, is not an existing second-party. Would you like to create a new second-party named {lQ}@ATTEMPTED_ENTRY{rQ}?',
# 			'missing parent, subcat': f'The subcategory you entered, {lQ}@ATTEMPTED_ENTRY{rQ}, is not an existing subcategory of the {lQ}@MAJ_CAT{rQ} category. Would you like to create a new subcategory named {lQ}@ATTEMPTED_ENTRY{rQ}?',
# 			'missing parent, majcat': f'The category you entered, {lQ}@ATTEMPTED_ENTRY{rQ}, is not an existing category. Would you like to create a new category named {lQ}@ATTEMPTED_ENTRY{rQ}?',
# 		}

# 		self.errors = {}
# 		self.call_for_checking()
# 		# @	Validate the data.
# 		#	  ,	Check if any required fields are NULL.
# 		#		  -	If they are, append to self.error_list an
# 		#			'invalid_null' error, along with what fields
# 		#			it concerns.
# 		#	  ,	Check for missing parents.
# 		#	  @ Check if data-types are correct.
# 		# @	If all checks are satisfied, prepare data for
# 		#	writing.
# 		# @	Write data.


# 	def make_writeDict(self) -> dict[str,typ.Any]:
# 		"""
# 		- Makes a dictionary out of the fields in the input
# 		table and the values in the input-value-tuple.
# 		"""
# 		writeDict = {}
# 		if self.isUpdate:
# 			# -	If doing an update, RowID will have been read
# 			#	from the existing record, and the writeDict
# 			#	needs to accommodate that.
# 			writeDict['RowID'] = self.INPUTS[0]
# 			i = 1
# 		else:
# 			i = 0

# 		for field in self.TABLE.fields:
# 			writeDict[field] = self.INPUTS[i]
# 			i += 1

# 		return writeDict


# 	def handle_missing_parent(self, parentless:tuple[str,typ.Any], majCat_val=''):
# 		"""
# 		- If the user has entered a value which violates a
# 		foreign-key-constraint, this function figures out what
# 		message to display informing them of that, and what
# 		prompt to show to give them the chance to create a
# 		minimal record in the parent table to satify the
# 		constraint.
# 		- The contents of the 'parentless' parametre are:
# 			- [0] The fieldname of the value in question.
# 			- [1] The value the user has attempted to enter into
# 			that field.
# 		- The majCat_val parametre is required if the
# 		parentless value is in the Sub_Category field.
# 		"""

# 		if (self.TABLE == MAIN_TABLE
# 		and parentless[0] == PARTY_TABLE):
# 			errortext = tr(self.ERROR_MESSAGES['missing parent, party'].replace('@ATTEMPTED_ENTRY', str(parentless[1])))
# 			handle = HandlerPopup('missing parent, party', errortext, 'y/n', parentless[1])

# 		elif (self.TABLE == MAIN_TABLE
# 		and parentless[0] == SUBCAT_TABLE):
# 			if majCat_val == '':
# 				raise ValueError('No argument for majCat_val was provided, despite the parentless value being in the Sub_Category field.')
# 			errortext = tr(self.ERROR_MESSAGES['missing parent, subcat'].replace('@ATTEMPTED_ENTRY', parentless[1]).replace('@MAJ_CAT', majCat_val))
# 			handle = HandlerPopup('missing parent, subcat', errortext, 'y/n', parentless[1], majCat_val)

# 		else:	# Will be missing a Major_Category in either Transactions or SubCategories.
# 			errortext = tr(self.ERROR_MESSAGES['missing parent, majcat'].replace('@ATTEMPTED_ENTRY', parentless[1]))
# 			handle = HandlerPopup('missing parent, majcat', errortext, 'y/n', parentless[1])

# 		choice = handle.exec()

# 		return bool(choice)


# 	def check_invalid_null(self) -> bool:
# 		col = 0	#@ Does this need to change respective of .isUpdate?
# 		overall_valid_nulls = True
# 		for value in self.INPUTS:
# 			if (value == None
# 			and self.TABLE.notnulls[self.TABLE.fields[col]]):
# 				self.errors[col] = 'invalid null'
# 				overall_valid_nulls = False
# 			col += 1
# 		return overall_valid_nulls


# 	def check_foreignkeys(self) -> bool:
# 		foreignkeys_satisfied = True
# 		col = 0
# 		for value in self.INPUTS:
# 			val_field = self.TABLE.fields[col]
# 			if val_field in self.TABLE.foreign_keys.keys():
# 				reference = self.TABLE.foreign_keys[val_field]
# 				ref_table = reference[0];  ref_field = reference[1]
# 				storage_val = QENV.rowID_lookup(ref_table, ref_field, value)

# 				if storage_val == None:
# 					if val_field == 'Sub_Category':
# 						majCat_val = QENV.rowID_lookup(self.INPUTS[MAJCAT_TABLE.fields.index['Major_Category']])
# 						choice = self.handle_missing_parent((ref_table, value), majCat_val)
# 					else:
# 						choice = self.handle_missing_parent((ref_table, value))

# 					# - Set to True if user has chosen to make a
# 					#   new minimal record to satisfy a missing
# 					#   foreign-key;
# 					foreignkeys_satisfied = choice
# 		return foreignkeys_satisfied


# 	def check_datatypes(self) -> bool:
# 		col = 0
# 		for value in self.INPUTS:
# 			val_field = self.TABLE.fields[col]
# 			field_type = self.TABLE.types[val_field]
# 			if type(value) != TYPE_LOCALIZER[field_type.upper()]:
# 				if type(value) == str:
# 					#@ This is a significant problem; there isn't a number where there should be.
# 					pass
# 				else:
# 					#@ This is a minor issue; display a disablable confirmation-prompt.
# 					pass


# 	def call_for_checking(self):
# 		all_passed = self.check_invalid_null()
# 		all_passed = self.check_foreignkeys()
# 		all_passed = self.check_datatypes()

# 		if not all_passed:
# 			pass

# 	def shutdown(self):
# 		delete_testdata()
# 		self.access.close()
