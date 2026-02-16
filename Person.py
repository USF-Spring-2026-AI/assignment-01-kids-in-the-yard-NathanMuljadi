class Person():
    def __init__(self, year_born, year_died, first_name, last_name, spouse, children=[]):
        self.year_born = year_born
        self.year_died = year_died
        self.first_name = first_name
        self.last_name = last_name
        self.spouse = spouse
        self.children = children