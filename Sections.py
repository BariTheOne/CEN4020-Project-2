class CourseSection:
    def __init__(self, crn, campus, level, section_number, subject, number, title, meeting_time, meeting_room, enrolled_count, capacity):
        self.crn = crn
        self.campus = campus
        self.level = level
        self.section_number = section_number
        self.subject = subject
        self.number = number
        self.title = title
        self.meeting_time = meeting_time
        self.meeting_room = meeting_room
        self.enrolled_count = enrolled_count
        self.capacity = capacity

    def is_full(self):
        return self.enrolled_count >= self.capacity

    def get_available_seats(self):
        return self.capacity - self.enrolled_count
    
    def __str__(self):
        return f"""CRN: {self.crn} | {self.subject} {self.number} - {self.title} (Section {self.section_number})
            Meeting Times: {self.meeting_time.__str__()}"""