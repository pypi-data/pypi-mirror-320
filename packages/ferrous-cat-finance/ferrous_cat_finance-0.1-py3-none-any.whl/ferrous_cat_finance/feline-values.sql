-- FILE-EXPLANATION:
---	'feline-values.sql' provides a subtly-themed set of example-
--	values for RotheFinance.db.

BEGIN;

INSERT INTO MajorCategories(Title, Description, Is_Testdata) VALUES
	('Food', 'To keep residents of the house alive!', 1),
	('Litter', 'A bathroom-time necessity!', 1),
	('Repair', 'For when the house needs a refresh to keep up with all the cuties!', 1),
	('Electricity', "Keeps the lights on, keeps the AC going so I'm not miserable, ... stuff like that!", 1),
	('Water', 'Drinks and baths for me and my fluffy children! And for non-fluffy ones too, of course!', 1),
	('Income', "To pay for everything! `\^.^/´", 1);


INSERT INTO SubCategories (Title, Parent, Description, Is_Testdata) VALUES
	('Wet', (SELECT ROWID FROM MajorCategories WHERE Title = 'Food'), 'High water-content. More expensive, but variety is important!', 1),
	('Dry', (SELECT ROWID FROM MajorCategories WHERE Title = 'Food'), 'Low water-content. Always affordable, and helps maintain variety!', 1),
	('Human', (SELECT ROWID FROM MajorCategories WHERE Title = 'Food'), 'I need to eat, too!', 1),
	('Job', (SELECT ROWID FROM MajorCategories WHERE Title = 'Income'), 'The normal way!', 1);


INSERT INTO SecondParties (Name, Phone, Email, Notes, Is_Testdata) VALUES
	('FoodCorp/Pets', '0001-4145-88521', 'foodcorp.pets.consumercontact@zaibatsumail.corp', "For food! Cat food! ... It doesn't taste good to me, but the adorable little critters love it <3!", 1),
	('FoodCorp/Grocery', '0001-4143-88518', 'foodcorp.grocery.consumercontact@zaibatsumail.corp', 'For me-food!', 1),
	('GrainCorp/Disposal', '0001-1172-88591', 'graincorp.disposal.consumercontact@zaibatsumail.corp', 'Mostly for litter.', 1),
	('MaintenenceCorp/Residential', '0001-8412-88130', 'maintenencecorp.residential.consumercontact@zaibatsumail.corp', NULL, 1),
	('Tributary/FoodChains/Valhallan', '0002-2106-88182', 'tributarychain.valhallan.consumercontact@zaibatsumail.corp', 'They pay me, and have decent food!',1 ),
	('PowerCorp/Residential', '0001-0205-88914', 'powercorp.residential.consumercontact@zaibatsumail.corp', NULL, 1),
	('WaterCorp/Residential', '0001-0607-88921', 'watercorp.residential.consumercontact@zaibatsumail.corp', NULL, 1);


INSERT INTO Transactions (
	Date, Item_Name, Balance_Effect, Major_Category, Sub_Category,
	Description, Second_Party, Is_Testdata)
	VALUES
		('2025-11-06', 'Groceries', -1127.84, 'Food', 'Human', 'Mostly potatoes.', 'FoodCorp/Grocery', 1),
		('2025-11-12', 'Wet Food', -303.91, 'Food', 'Wet', 'Salmon!', 'FoodCorp/Pets', 1),
		('2025-11-12', 'Dry Food', -210.92, 'Food', 'Dry', 'Chicken!', 'FoodCorp/Pets', 1),
		('2025-11-15', 'Litter', -98.89, 'Litter', NULL, NULL, 'GrainCorp/Disposal', 1),
		('2025-11-23', 'Carpet-Replacement', -426.52, 'Repair', NULL, 'Pedro-Martinez got a bit upset! More training for him. :(', 'MaintenenceCorp/Residential', 1),
		('2025-12-01', 'Paycheck', 3375.00, 'Income', 'Job', NULL, 'Tributary/FoodChains/Valhallan', 1),
		('2025-12-02', 'Electricity-Bill', -572.61, 'Electricity', NULL, NULL, 'PowerCorp/Residential', 1),
		('2025-12-02', 'Water-Bill', -632.45, 'Water', NULL, NULL, 'WaterCorp/Residential', 1);


COMMIT;