class University:
    def __init__(self, name, country, city):
        self.name = name
        self.country = country
        self.city = city
        self.faculties = []
        
    def add_faculty(self, name):
        return Faculty(self, name)
        
    
class Faculty:
    def __init__(self, university, name):
        self.university = university
        self.name = name