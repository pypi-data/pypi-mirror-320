from typing import Literal, Any

FELINE_CATEG = [
	{'Title': 'Food',
		'Description': 'To keep residents of the house alive!'},

	{'Title': 'Litter',
		'Description': 'A bathroom-time necessity!'},

	{'Title': 'Repair',
		'Description': 'For when the house needs a refresh to keep up with all the cuties!'},

	{'Title': 'Electricity',
		'Description': "Keeps the lights on, keeps the AC going so I'm not miserable, ... stuff like that!"},

	{'Title': 'Water',
		'Description': 'Drinks and baths for me and my fluffy children! And for non-fluffy ones too, of course!'},

	{'Title': 'Income',
		'Description': 'To pay for everything! `\\^.^/´'},

	{'Title': 'Big Stuff',
  		'Description': 'Upgrades, replacements, etc. Big, exciting stuff!'}
]

FELINE_PARTIES = [
	{'Name': 'FoodCorp/Pets',
		'Phone': '0001-4145-88521',
		'Email': 'foodcorp.pets.consumercontact@zaibatsumail.corp',
		'Notes': "For food! Cat food! ... It doesn't taste good to me, but the adorable little critters love it <3!"},

	{'Name': 'FoodCorp/Grocery',
		'Phone': '0001-4143-88518',
		'Email': 'foodcorp.grocery.consumercontact@zaibatsumail.corp',
		'Notes': 'For me-food!'},

	{'Name': 'GrainCorp/Disposal',
		'Phone': '0001-1172-88591',
		'Email': 'graincorp.disposal.consumercontact@zaibatsumail.corp',
		'Notes': 'Mostly for litter.'},

	{'Name': 'MaintenenceCorp/Residential',
		'Phone': '0001-8412-88130',
		'Email': 'maintenencecorp.residential.consumercontact@zaibatsumail.corp',
		'Notes': None},

	{'Name': 'Tributary/FoodChains/Valhallan',
		'Phone': '0002-2106-88182',
		'Email': 'tributarychain.valhallan.consumercontact@zaibatsumail.corp',
		'Notes': 'They pay me, and have decent food!'},

	{'Name': 'PowerCorp/Residential',
		'Phone': '0001-0205-88914',
		'Email': 'powercorp.residential.consumercontact@zaibatsumail.corp',
		'Notes': None},

	{'Name': 'ApplianceCorp/Transportation',
  		'Phone': None,
		'Email': None,
		'Notes': None},

	{'Name': 'WaterCorp/Residential',
		'Phone': '0001-0607-88921',
		'Email': 'watercorp.residential.consumercontact@zaibatsumail.corp',
		'Notes': None},

	{'Name': 'Tributary/Animal/Kitty Love',
  		'Phone': '0002-2106-88144',
		'Email': 'specialist.kittylove.consumercontact@zaibatusmail.corp',
		'Notes': 'They have very nice things for my children! ... Bit expensive, though.'},
]

FELINE_TRANSACT:list[dict[
	Literal[
		'Date', 'Item_Name', 'Balance_Effect', 'Major_Category',
		'Ledger', 'Description', 'Second_Party'],
	Any]] = [
	{'Date': '2025-11-06',
		'Item_Name': 'Groceries',
		'Balance_Effect': -1127.84,
		'Major_Category': 'Food',
		'Ledger': 'Living-Expenses',
		'Description': 'Mostly potatoes.',
		'Second_Party': 'FoodCorp/Grocery'},

	{'Date': '2025-11-12',
		'Item_Name': 'Wet Food',
		'Balance_Effect': -303.91,
		'Major_Category': 'Food',
		'Ledger': 'Living-Expenses',
		'Description': 'Salmon!',
		'Second_Party': 'FoodCorp/Pets'},

	{'Date': '2025-11-12',
		'Item_Name': 'Dry Food',
		'Balance_Effect': -210.92,
		'Major_Category': 'Food',
		'Ledger': 'Living-Expenses',
		'Description': 'Chicken!',
		'Second_Party': 'FoodCorp/Pets'},

	{'Date': '2025-11-15',
		'Item_Name': 'Litter',
		'Balance_Effect': -98.89,
		'Major_Category': 'Litter',
		'Ledger': 'Living-Expenses',
		'Description': None,
		'Second_Party': 'GrainCorp/Disposal'},

	{'Date': '2025-11-23',
		'Item_Name': 'Carpet-Replacement',
		'Balance_Effect': -426.52,
		'Major_Category': 'Repair',
		'Ledger': 'Living-Expenses',
		'Description': 'Pedro-Martinez got a bit upset! More training for him. :(',
		'Second_Party': 'MaintenenceCorp/Residential'},

	{'Date': '2025-12-01',
		'Item_Name': 'Paycheck',
		'Balance_Effect': 3375.00,
		'Major_Category': 'Income',
		'Ledger': 'Business',
		'Description': None,
		'Second_Party': 'Tributary/FoodChains/Valhallan'},

	{'Date': '2025-12-02',
		'Item_Name': 'Electricity-Bill',
		'Balance_Effect': -572.61,
		'Major_Category': 'Electricity',
		'Ledger': 'Living-Expenses',
		'Description': None,
		'Second_Party': 'PowerCorp/Residential'},

	{'Date': '2025-12-02',
		'Item_Name': 'Water-Bill',
		'Balance_Effect': -632.45,
		'Major_Category': 'Water',
		'Ledger': 'Living-Expenses',
		'Description': None,
		'Second_Party': 'WaterCorp/Residential'},

	{'Date': '2025-01-01',
		'Item_Name': 'Paycheck',
		'Balance_Effect': 600,
		'Major_Category': 'Income',
		'Ledger': 'Business',
		'Description': None,
		'Second_Party': 'Tributary/FoodChains/Valhallan'},

	{'Date': '2025-02-01',
		'Item_Name': 'Paycheck',
		'Balance_Effect': 1112,
		'Major_Category': 'Income',
		'Ledger': 'Business',
		'Description': None,
		'Second_Party': 'Tributary/FoodChains/Valhallan'},

	{'Date': '2025-03-01',
		'Item_Name': 'Paycheck',
		'Balance_Effect': 7777,
		'Major_Category': 'Income',
		'Ledger': 'Business',
		'Description': None,
		'Second_Party': 'Tributary/FoodChains/Valhallan'},

	{'Date': '2025-01-07',
		'Item_Name': 'Fancy Treats',
  		'Balance_Effect': -388.22,
		'Major_Category': 'Food',
		'Ledger': 'Living-Expenses',
		'Description': 'Nice treats for the new year!',
		'Second_Party': 'Tributary/Animal/Kitty Love'},

	{'Date': '2025-03-06',
		'Item_Name': 'Fancy Treats',
  		'Balance_Effect': -422.17,
		'Major_Category': 'Food',
		'Ledger': 'Living-Expenses',
		'Description': 'Treats for a weirdly large paycheck!',
		'Second_Party': 'Tributary/Animal/Kitty Love'},

	{'Date': '2025-03-17',
  		'Item_Name': 'Old Moped Sale',
		'Balance_Effect': 63.99,
		'Major_Category': 'Big Stuff',
		'Ledger': 'Capital',
		'Description': 'Old Fore broke down. Can\'t affort to fix him. :{',
		'Second_Party': 'ApplianceCorp/Transportation'},

	{'Date': '2025-03-17',
  		'Item_Name': 'New Moped',
		'Balance_Effect': -646.99,
		'Major_Category': 'Big Stuff',
		'Ledger': 'Capital',
		'Description': 'Dorothy is my new ride. I\'m sure we\'ll get along eventually. .~.',
		'Second_Party': 'ApplianceCorp/Transportation'},
]
