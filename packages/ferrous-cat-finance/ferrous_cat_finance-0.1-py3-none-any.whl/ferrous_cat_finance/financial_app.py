# PROGRAM-INFO:
# -	File: financial_app.py.
# -	Author: Isaac Erb.
# - Date Created: 2024-Jul-01.

### IMPORTS ####################################################
import sys, json
from platform import system

# custom modules
from storage.TestData import setup_testdata, delete_testdata
from storage.Database import SQL_Connection


### CONSTANTS ##################################################

SETTINGS_FILE = 'pers_pref.json'
SETTINGS = json.load(open(SETTINGS_FILE, 'r', encoding='utf8'))


###	SQL_Environment-Class Constant:
QENV = SQL_Connection()	# 'QENV' for 'Query-ENVironment'. Pronounced as "ˈkɛnv".

def pathing_localizer(linux_path:str) -> str:
	"""
	- Reformats the correct pathing-notation to that usable by
	Windows OS.
	"""
	if system() == 'Windows':
		local_path = linux_path.replace('/','\\')
	else:
		local_path = linux_path
	return local_path


def on_exit():
	json.dump(SETTINGS, SETTINGS_FILE)
	delete_testdata()
	QENV.access.close()
	exit()


def program():
	setup_testdata()

	from ui.Main import CoreWidget, MenuShell, QApplication, QCoreApplication, QLocale, QTranslator
	GUI_SESSION = QApplication()
	# - Set up translation features(?).
	TRANSLING = QTranslator()
	if TRANSLING.load(QLocale(), pathing_localizer('rothe-finance-app/translation/'), ):
		QCoreApplication.installTranslator(TRANSLING)

	CORE = CoreWidget()
	SHELL = MenuShell()
	SHELL.setCentralWidget(CORE)

	# - Opening the GUI.
	SHELL.show()

	# - Setting max size of the app-window to its initial size.
	match system():
		case 'Linux':
			pass
		case 'Darwin':
			CORE.setMaximumHeight(CORE.height())
			CORE.setMaximumWidth(CORE.width())

	sys.exit(GUI_SESSION.exec())
	# QEventLoop(GUI_SESSION)


program()
on_exit()	#@ Doesn't run!
