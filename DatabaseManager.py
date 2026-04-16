import sqlite3
from Sections import CourseSection
from schedule import *
from datetime import datetime
from Actors import *

class DatabaseManager:
    def __init__(self, database_filepath : str):
        self._connection = sqlite3.connect(database_filepath)
        self._cursor = self._connection.cursor()

    def retrieveSection(self, crn : int) -> CourseSection:
        """
        Get the corresponding section information from a CRN.
        Returns a CourseSection object.

        :crn: Course Registration Number
        """

        #query the database
        try:
            sql_results = self._cursor.execute(
                """
                SELECT * FROM Courses WHERE "CRN" = ?;
                """,
                (crn,)
            )
        except sqlite3.Error as error:
            print("Error!:", error)
            return

        course_tuple = sql_results.fetchall()

        #check if the list is empty
        if len(course_tuple) < 1:
            print("Error!: No course section was found with that CRN.")
        elif len(course_tuple) > 1:
            print("Error!: More than one course section were found with that CRN.")
        else:
            course_tuple = course_tuple[0]

            #otherwise, create a MeetingTime object
            start_time = datetime.fromisoformat(course_tuple[8])
            end_time = datetime.fromisoformat(course_tuple[9])
            meeting_time = MeetingTime(course_tuple[7], start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))

            #create a CourseSection object
            result = CourseSection(
                crn,
                course_tuple[1],    #Campus
                course_tuple[2],    #Level
                course_tuple[3],    #Section
                course_tuple[4],    #Subject
                course_tuple[5],    #Number (goes with above)
                course_tuple[6],    #Title
                meeting_time,       #Meeting Time
                course_tuple[10],   #Meeting Room
                enrolled_count=0,
                capacity=30
            )

            #return the object
            return result

    def getScheduleOfPerson(self, person : User) -> Schedule:
        """
        Get the schedule of a student, TA, or instructor.
        Returns a Schedule object.
        
        :person: the person who the schedule belongs to.
        """

        #identify the person
        sql_cpmmand = ""
        if isinstance(person, Student):
            sql_command = """
            SELECT
                Courses.CRN,
                Campus,
                Level,
                Section,
                Subject,
                Number,
                Title,
                MeetingDays,
                MeetingStartTime,
                MeetingEndTime,
                MeetingRoom 
            FROM Courses 
                JOIN CourseStudent ON Courses.CRN = CourseStudent.CRN
                JOIN Students ON CourseStudent.StudentID = Students.ID
            WHERE Students.Email = ?;
            """
        elif isinstance(person, TA):
            sql_command = """
            SELECT
                Courses.CRN,
                Campus,
                Level,
                Section,
                Subject,
                Number,
                Title,
                MeetingDays,
                MeetingStartTime,
                MeetingEndTime,
                MeetingRoom
            FROM Courses 
                JOIN CourseTA ON Courses.CRN = CourseTA.CRN
                JOIN TeachingAssistants ON CourseTA.TAID = TeachingAssistants.ID
            WHERE TeachingAssistants.Email = ?;
            """
        elif isinstance(person, Instructor):
            sql_command = """
            SELECT 
                Courses.CRN,
                Campus,
                Level,
                Section,
                Subject,
                Number,
                Title,
                MeetingDays,
                MeetingStartTime,
                MeetingEndTime,
                MeetingRoom
            FROM Courses 
                JOIN CourseInstructor ON Courses.CRN = CourseInstructor.CRN
                JOIN Instructors ON CourseInstructor.InstructorID = Instructors.ID
            WHERE Instructors.Email = ?;
            """
        else:
            #if it's not an acceptable person, quit
            print("Error!: The person is not a student, TA, or instructor. Please try again.")
            return

        #query the database
        try:
            sql_results = self._cursor.execute(
                sql_command,
                (person.email,)
            )
        except sqlite3.Error as error:
            print("Error!:", error)
            return
        course_section_tuples = sql_results.fetchall()

        #create a Schedule object
        result = Schedule()

        #iterate through all the classes
        for course_section_tuple in course_section_tuples:
            course_section = self.retrieveSection(course_section_tuple[0])
            result.add_section(course_section)
        
        #return the schedule
        return result
    
#DEBUGGING
if __name__ == "__main__":
    dbm = DatabaseManager("./BelliniClassesS26.db")
    print("First round of testing.")
    results = dbm.retrieveSection(14880)
    print(results)
    results = dbm.retrieveSection(14881)
    print(results)
    results = dbm.retrieveSection(14882)
    print(results)
    print("End of first round of testing.\n")

    instructor1 = Instructor("Hao Zheng", "haozheng@usf.edu")
    test_schedule = dbm.getScheduleOfPerson(instructor1)
    print(test_schedule)

    instructor2 = Instructor("Suey-Chyun Fang", "fang1@usf.edu")
    test_schedule = dbm.getScheduleOfPerson(instructor2)
    print(test_schedule)