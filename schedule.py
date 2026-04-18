class MeetingTime:
    def __init__(self, day, start_time, end_time, TBD=False):
        self.day = day
        self.start_time = self.to_minutes(start_time)
        self.end_time = self.to_minutes(end_time)
        self.TBD = TBD

    def to_minutes(self, time_str):
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes
    
    def to_hour_minute(self, minutes : int) -> str:
        am_pm = "AM" if (((minutes//60))//12 == 0) else "PM"
        return f"{12 if ((minutes//60)%12 == 0) else (minutes//60)%12}:{minutes%60:02d} {am_pm}"

    def overlaps_with(self, other):
        if self.day != other.day:
            return False
        return self.start_time < other.end_time and self.end_time > other.start_time
    
    def __str__(self):
        if not self.TBD:
            return f"""{self.day} {self.to_hour_minute(self.start_time)} - {self.to_hour_minute(self.end_time)}"""
        else:
            return """TBD"""

"""
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
"""


class Schedule:
    def __init__(self):
        self.sections = []

    def add_section(self, new_section):
        #if self.has_conflict(new_section):
        #    return False
        self.sections.append(new_section)
        return True

    def has_conflict(self, new_section):
        for existing_section in self.sections:
            if existing_section.conflicts_with(new_section):
                return True
        return False

    def remove_section(self, crn):
        for section in self.sections:
            if section.crn == crn:
                self.sections.remove(section)
                return True
        return False

    def get_all_sections(self):
        return self.sections
    
    def __str__(self):
        result = "---START OF SCHEDULE---\n"
        for section in self.sections:
            result += section.__str__() + "\n"
        result += "----END OF SCHEDULE----"
        return result