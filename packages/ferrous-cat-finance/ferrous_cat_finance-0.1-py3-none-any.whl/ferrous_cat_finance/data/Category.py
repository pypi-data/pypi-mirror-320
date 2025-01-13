from data.Error import Error

class Category:
    def __init__(self):
        self.rowID:int
        self.title:str
        self.description:str

    def validate(self, isNew=False):
        errors = []
        if not isNew and self.rowID is None:
            errors.append(Error('not_defined', 'rowID', 'rowID missing for existing category'))
        
        if self.title is None or len(self.title) == 0:
            errors.append(Error('not_defined','title','you must have a title for the category'))

        return errors

class SubCategory:
    def __init__(self):
        self.rowID:int
        self.parent:Category
        self.title:str
        self.description:str

    def validate(self, isNew=False):
        errors = []
        if not isNew and self.rowID is None:
            errors.append(Error('not_defined', 'rowID', 'rowID missing for existing subcategory'))
        
        if self.parent is None:
            errors.append(Error('not_defined','parent','you must have a parent category for the subcategory'))

        if self.title is None:
            errors.append(Error('not_defined','title','you must have a title for the subcategory'))

        return errors