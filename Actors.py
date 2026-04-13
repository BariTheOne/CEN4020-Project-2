# Base user class
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

# Instructor class
class Instructor(User):
    def __init__(self, name, email):
        super().__init__(name, email)
        self.assigned_classes = [] # set to include classes an instructor teaches

# committee member class
class SchedulingCommitteeMember(User):
    def __init__(self, name, email, is_chair=False):
        super().__init__(name, email)
        self.is_chair = is_chair # to differintiate between regular member and chair (User Story 2)

# Student class
class Student(User):
    def __init__(self, name, email):
        super().__init__(name, email)
        self.registered_classes = [] # set to include classes a student registered for

# Dean class
class Dean(User):
    def __init__(self, name, email):
        super().__init__(name, email)

# TA class
class TA(User):
    def __init__(self, name, email, ta_type="UGTA", hours=0):
        super().__init__(name, email)
        self.ta_type = ta_type # UG or G
        self.hours = hours
        self.assigned_classes = [] # set to include classes a TA is assigned
