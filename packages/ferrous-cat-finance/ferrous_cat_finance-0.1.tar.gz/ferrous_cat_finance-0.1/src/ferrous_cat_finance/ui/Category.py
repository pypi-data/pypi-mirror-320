from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ui.Common import *
from storage.CategoryTable import CategoryTable

class CategMainWidget(QWidget):
	def __init__(self):
		super().__init__()

		self.setAccessibleName('Categories')

		self.layout = QHBoxLayout(self)

		self.display_retired_opt = False	#@ Nothing actually changes this yet.

		self.categ_access = CategoryTable()

		self.categ_main_listing = QFormLayout(self)
		self.layout.addLayout(self.categ_main_listing)
		self.categ_opt_area = QVBoxLayout(self)
		self.layout.addLayout(self.categ_opt_area)

		for group in []:	#@TODO: Make this loop thru actual records.
			major = group[0]
			subs = group[1]
			if (self.display_retired_opt	# If displaying all categories,
			or self.major_activity[major]):		# or this category is active:
				major_title = QPushButton(tr(MAJCAT_TABLE.id_name_map[major]))
				major_title.setFont(DATA_FONT.scaled(1.5))
				#@ major_title.clicked.connect()

				# sub_items = []
				subholder = QWidget()
				subholder.layout = QHBoxLayout(subholder)

				for subcateg in subs:
					if self.sub_activity[subcateg]:
						item = QPushButton(tr(SUBCAT_TABLE.id_name_map[subcateg]), subholder)
						item.setFont(DATA_FONT.reg())
						# @	Here is where the action-setup should
						#	probably go.
						subholder.layout.addWidget(item)
						# sub_items.append(item)

				self.categ_main_listing.addRow(major_title, subholder)

		self.categ_sort_label = QLabel(text=tr('Sort By:'))
		format_headLinewidget(self.categ_sort_label)
		self.categ_sortby_name = QRadioButton(text=tr('Name.'))
		format_linewidget(self.categ_sortby_name)
		self.categ_sortby_frequent = QRadioButton(text=tr('Frequency.'))
		format_linewidget(self.categ_sortby_frequent)
		self.retired_toggle = QPushButton(text=tr('View\nRetired\nCategories'))
		#@ self.retired_toggle.clicked.connect()

		self.categ_opt_area.addWidget(self.categ_sort_label)
		self.categ_opt_area.addWidget(self.categ_sortby_name)
		self.categ_opt_area.addWidget(self.categ_sortby_frequent)
		self.categ_opt_area.addWidget(self.retired_toggle, alignment=Qt.AlignmentFlag.AlignTop)

