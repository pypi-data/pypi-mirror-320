-- FILE-EXPLANATION:
---	'feline-upheaval.sql' removes all records made by 'feline-
--	values.sql', because that which is both good and natural
--	generally cannot last. (Although, the same could be said abo

BEGIN;

DELETE FROM Transactions
	WHERE (Date = '2025-11-06' AND Second_Party = 'FoodCorp/Grocery')
	OR (Date = '2025-11-12' AND Second_Party = 'FoodCorp/Pets')
	OR (Date = '2025-11-15' AND Second_Party = 'GrainCorp/Disposal')
	OR (Date = '2025-11-23' AND Second_Party = 'MaintenenceCorp/Residential')
	OR (Date = '2025-12-01' AND Second_Party = 'Tributary/FoodChains/Valhallan')
	OR (Date = '2025-12-02' AND Second_Party = 'PowerCorp/Residential')
	OR (Date = '2025-12-02' AND Second_Party = 'WaterCorp/Residential')

DELETE FROM SecondParties
	WHERE Email LIKE '%@zaibatsumail.corp';

DELETE FROM SubCategories
	WHERE (Title = 'Wet' AND Description = 'High water-content. More expensive, but variety is important!')
	OR (Title = 'Dry' AND Description = 'Low water-content. Always affordable, and helps maintain variety!')
	OR (Title = 'Human' AND Description = 'I need to eat, too!')
	OR (Title = 'Job' AND Parent IN (SELECT ROWID FROM MajorCategories WHERE Title = 'Income') AND Description = 'The normal way!');

DELETE FROM MajorCategories
	WHERE (Title = 'Food' AND Description = 'To keep residents of the house alive!')
	OR (Title = 'Litter' AND Description = 'A bathroom-time necessity!')
	OR (Title = 'Repair' AND Description = 'For when the house needs a refresh to keep up with all the cuties!')
	OR (Title = 'Electricity' AND Description = "Keeps the lights on, keeps the AC going so I'm not miserable, ... stuff like that!")
	OR (Title = 'Water' AND Description = 'Drinks and baths for me and my fluffy children! And for non-fluffy ones too, of course!')
	OR (Title = 'Income' AND Description = "To pay for everything! `\^.^/´");

COMMIT;