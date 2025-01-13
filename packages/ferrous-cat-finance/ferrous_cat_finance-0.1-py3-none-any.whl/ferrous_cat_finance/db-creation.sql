BEGIN;
---	SecondParties holds contact-info for businesses with whom
--	you are performing financial transactions.
CREATE TABLE SecondParties (
	Name TEXT NOT NULL UNIQUE,
	Phone TEXT,
	Email TEXT,
	Notes TEXT,
	Is_Testdata INTEGER DEFAULT 0,
	CHECK (Is_Testdata IN (0,1)));


---	Ledgers groups Transactions into topics such as business,
--  living-expenses, and debt, for the purpose of making reports
--  more useful.
CREATE TABLE Ledgers (
	Title TEXT NOT NULL UNIQUE,
	Description TEXT,
	Is_Testdata INTEGER DEFAULT 0,
	CHECK (Is_Testdata IN (0,1)));


---	MajorCategories contains a list of user-defined categories
--	used to group Tranactions within Ledgers for reports.
---	Usage of Categories is mandatory, as it is important to
--	have easily-delcarable items show up on reports.
CREATE TABLE MajorCategories (
	Title TEXT NOT NULL UNIQUE,
	Description TEXT,
	Active INTEGER DEFAULT 1,
	Is_Testdata INTEGER DEFAULT 0,
	CHECK (Active IN (0,1))
	CHECK (Is_Testdata IN (0,1)));


--- Transactions holds the fields necessary for recording a
--	financial transaction. It holds most of the important data.
CREATE TABLE Transactions (
	Date TEXT NOT NULL,
	Item_Name TEXT NOT NULL,
	Balance_Effect REAL NOT NULL,
	Major_Category INTEGER NOT NULL,
	Ledger_ID INTEGER NOT NULL,
	Description TEXT,
	Second_Party INTEGER,
	Is_Testdata INTEGER DEFAULT 0,
	Is_Capital INTEGER DEFAULT 0,
	FOREIGN KEY (Major_Category) REFERENCES MajorCategories(ROWID),
	FOREIGN KEY (Ledger_ID) REFERENCES Ledgers(ROWID),
	FOREIGN KEY (Second_Party) REFERENCES SecondParties(ROWID),
	CHECK (Is_Testdata IN (0,1)),
	CHECK (Is_Capital IN (0,1)));

COMMIT;