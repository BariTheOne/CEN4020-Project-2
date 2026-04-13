class CourseSection:
    def __init__(self, crn, section_number, enrolled_count, capacity):
        self.crn = crn
        self.section_number = section_number
        self.enrolled_count = enrolled_count
        self.capacity = capacity

    def is_full(self):
        return self.enrolled_count >= self.capacity

    def get_available_seats(self):
        return self.capacity - self.enrolled_count