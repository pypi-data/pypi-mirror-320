import typing as typ
import os, platform
from fpdf import FPDF

FONT = 'Helvetica'
LINEHEIGHT = 8
COLUMN_WIDTH = 18.5
FONTSIZE = 11

class CashflowPDF(FPDF):
	def __init__(self, name:str):
		super().__init__('L', format='Letter')
		self.report_name = name
		self.alias_nb_pages()
		self.add_page()
		# self.set_margins(12, 24, 12)
		return


	def header(self):
		self.set_font(FONT, 'B', 15)
		self.cell(268.1, 10, self.report_name, 0, 0, 'C')
		# Line break
		self.ln(8)
		return


	# Page footer
	def footer(self):
		# Position at 1.5 cm from bottom
		self.set_y(-15)
		# Arial italic 8
		self.set_font(FONT, 'I', 9)
		# Page number
		self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')
		return


	def generate(self,
			datagrid:list[list],
			bold_rows:list[int]=[],
			bold_cells:list[tuple[int,int]]=[]):

		self.set_font(FONT, '', FONTSIZE)

		row = 0
		for line in datagrid:
			col = 1

			for item in line:
				bold = False
				endline = 0

				if (col == 1 or row == 0):
				# or row in bold_rows
				# or (row, col-1) in bold_cells):
					bold = True
				if col == len(line):	# Is the last cell in the row; mark to wrap before the next.
					endline = 1

				if bold:	# Set the cell to bold.
					self.set_font(FONT, 'B', FONTSIZE)

				# - Make cell.
				self.cell(COLUMN_WIDTH, LINEHEIGHT, str(item), ln=endline, align='R')

				if bold:	# Reset to non-bold.
					self.set_font(FONT, '', FONTSIZE)

				col += 1
			row += 1

		report_filename = self.report_name.replace(',','').replace(':','').replace(' ','_')
		report_path = f'output-files/{report_filename}.pdf'
		self.output(report_path, 'F')
		if platform.system() == 'Linux':
			os.system(f'evince {report_path}')
		elif platform.system() == 'Darwin':
			os.system(f'open -a Preview {report_path}')


# FPDF_FONT_DIR = '/home/ironheart/.local/share/fonts/verdana/'
# DATA_FONT = 'helvetica'
# # DATA_FONT = '/home/ironheart/.local/share/fonts/verdana/verdana.ttf'

# TEMPLATE_ITEM = dict[	# REFERENCE: https://pyfpdf.readthedocs.io/en/latest/Templates/index.html
# 	typ.Literal[
# 		'name',			# String; serves as identifier for template-item.
# 		'type',			# String; 'T' for text.
# 		'x1',			# Float; x-position of item's upper-left corner. (mm from upper-left corner of non-header page.)
# 		'y1',			# Float; y-position of item's upper-left corner. (mm from upper-left corner of non-header page.)
# 		'x2',			# Float; x-position of item's bottom-right corner. (mm from upper-left corner of non-header page.)
# 		'y2',			# Float; y-position of item's bottom-right corner. (mm from upper-left corner of non-header page.)
# 		'font',			# String; name of font. Requires loading of a font-reference-object for fonts that didn't come with the package.
# 		'size',			# Integer; font-size in pt.
# 		'bold',			# True | None; True if should be bold, unset or None if should be non-bold.
# 		'italic',		# True | None; True if should be italic, unset or None if should be non-italic.
# 		'underline',	# True | None; True if should be underlined, unset or None if should be non-underlined.
# 		'foreground',	# String; text-color in hex-format like '0xAAFFCC'.
# 		'background',	# String; background-color in hex-format like 0xAAFFCC.
# 		'align', 		# String; 'L' for left-aligned, 'C' for centred.
# 		'text', 		# String; displayed value!
# 		'priority',		# Integer; z-index.
# 		'multiline'		# True | None: True if should be multiline, unset or None if should be single-line.
# 		],
# 	typ.Any]

# FELINE_MAJCAT:list[dict[typ.Literal['Title','Description'],str]] = [
# 	{'Title': 'Food',
# 		'Description': 'To keep residents of the house alive!'},

# 	{'Title': 'Litter',
# 		'Description': 'A bathroom-time necessity!'},

# 	{'Title': 'Repair',
# 		'Description': 'For when the house needs a refresh to keep up with all the cuties!'},

# 	{'Title': 'Electricity',
# 		'Description': "Keeps the lights on, keeps the AC going so I'm not miserable, ... stuff like that!"},

# 	{'Title': 'Water',
# 		'Description': 'Drinks and baths for me and my fluffy children! And for non-fluffy ones too, of course!'},

# 	{'Title': 'Income',
# 		'Description': 'To pay for everything! `\\^.^/´'},
# ]

# ORIGIN = {'x': 12.5, 'y': 12.5}
# LINEHEIGHT = 20
# COL_0_WIDTH = 30
# COL_1_WIDTH = 180

# formatted = []
# row = 0
# for record in FELINE_MAJCAT:
# 	title_item:TEMPLATE_ITEM = {}
# 	desc_item:TEMPLATE_ITEM = {}

# 	title_item['name'] = f'row-{row}, title'
# 	title_item['type'] = 'T'
# 	title_item['x1'] = ORIGIN['x']
# 	title_item['y1'] = ORIGIN['y'] + (LINEHEIGHT * row)
# 	title_item['x2'] = ORIGIN['x'] + COL_0_WIDTH
# 	title_item['y2'] = ORIGIN['y'] + (LINEHEIGHT * row) + LINEHEIGHT
# 	title_item['font'] = DATA_FONT
# 	title_item['size'] = 11
# 	title_item['align'] = 'L'
# 	title_item['text'] = record['Title']
# 	title_item['priority'] = 0
# 	formatted.append(title_item)

# 	desc_item['name'] = f'row-{row}, description'
# 	desc_item['type'] = 'T'
# 	desc_item['x1'] = ORIGIN['x'] + COL_0_WIDTH
# 	desc_item['y1'] = ORIGIN['y'] + (LINEHEIGHT * row)
# 	desc_item['x2'] = ORIGIN['x'] + COL_0_WIDTH + COL_1_WIDTH
# 	desc_item['y2'] = ORIGIN['y'] + (LINEHEIGHT * row) + LINEHEIGHT
# 	desc_item['font'] = DATA_FONT
# 	desc_item['size'] = 11
# 	desc_item['align'] = 'L'
# 	desc_item['text'] = record['Description']
# 	desc_item['priority'] = 0
# 	desc_item['multiline'] = True
# 	formatted.append(desc_item)

# 	row+=1

# template = Template(format='Letter', elements=formatted, title='Data-Printout-Test 01')
# template.add_page()

# template.render(outfile='test01.pdf')