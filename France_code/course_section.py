class CourseSection:
    def __init__(self, crn, course_code, instructor, room, meeting_times):
        self.crn = crn
        self.course_code = course_code
        self.instructor = instructor
        self.room = room
        self.meeting_times = meeting_times

    def conflicts_with(self, other):
        for mt1 in self.meeting_times:
            for mt2 in other.meeting_times:
                if mt1.overlaps_with(mt2):
                    return True
        return False
        
    def __str__(self):
        return f"{self.course_code} ({self.crn}) - {self.instructor}"
