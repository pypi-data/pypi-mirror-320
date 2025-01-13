from data.Error import Error

class SecondParty:
    def __init__(self):
        self.rowID:int
        self.name:str
        self.phone:str
        self.email:str
        self.notes:str

    def validate(self, isNew=False):
        errors = []
        if not isNew and self.rowID is None:
            errors.append(Error('not_defined', 'rowID', 'rowID missing for existing Vendor'))
        
        if self.name is None or len(self.name) == 0:
            errors.append(Error('not_defined','name','you must have a name for the Vendor'))

        return errors
