from typing import Literal, Any
from ui.Category import tr

PREDEF_LEDGERS:list[
	dict[
		Literal['Title', 'Description'],
		Any]
	] = [
	{'Title': tr('Business'),
  		'Description': tr('Business-transactions.')},

	{'Title': tr('Capital'),
		'Description': tr('Capital purchases or sales.')},

	{'Title': tr('Debt'),
  		'Description': tr('Increase or decrease of debts.')},

	{'Title': tr('Living-Expenses'),
  		'Description': tr('Bills, non-business purchases, etc.')},
]

