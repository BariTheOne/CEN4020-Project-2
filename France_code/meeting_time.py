class MeetingTime:
    def __init__(self, day, start_time, end_time):
        self.day = day
        self.start_time = self.to_minutes(start_time)
        self.end_time = self.to_minutes(end_time)

    def to_minutes(self, time_str):
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    def overlaps_with(self, other):
        if self.day != other.day:
            return False
        return self.start_time < other.end_time and self.end_time > other.start_time
