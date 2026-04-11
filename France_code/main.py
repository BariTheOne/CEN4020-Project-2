from meeting_time import MeetingTime
from course_section import CourseSection
from schedule import Schedule

# Create meeting times
mt1 = MeetingTime("Mon", "09:00", "10:15")
mt2 = MeetingTime("Mon", "10:00", "11:15")  # conflict

# Create sections
cs1 = CourseSection("123", "COP4530", "Dr. A", "Room 1", [mt1])
cs2 = CourseSection("456", "COP4530", "Dr. B", "Room 2", [mt2])

# Create schedule
schedule = Schedule()

# No conflict
print("Adding first section:", schedule.add_section(cs1))

# Conflict
print("Adding second section:", schedule.add_section(cs2))
