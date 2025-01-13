from data.Error import Error

class Transaction:
    def __init__(self):
        self.rowID: int
        self.itemName:str
        self.categoryId:int
        self.ledgerID:int
        self.description:str
        self.secondPartyId:int
        self.expense:float
        self.revenue:float
        self.date:str

    def validate(self, isNew=False):
        errors = []
        if not isNew and self.rowID is None:
            errors.append(Error('not_defined', 'rowID', 'rowID missing for existing transaction'))

        if not hasattr(self, 'expense') and not hasattr(self, 'revenue'):
            errors.append(Error('expense_revenue_not_defined','revenue,expense','must enter either expense or revenue'))

        if hasattr(self, 'expense') and hasattr(self, 'revenue'):
            errors.append(Error('expense_revenue_both_defined','revenue,expense','you can only enter either expense or revenue'))

        if self.categoryId is None:
            errors.append(Error('not_defined','category','you must have a category for the transaction'))

        if self.itemName is None or len(self.itemName) == 0:
            errors.append(Error('not_defined','itemName','you must have an item name for the transaction'))

        if self.date is None:
            errors.append(Error('not_defined','date','you must have an date for the transaction'))

        return errors