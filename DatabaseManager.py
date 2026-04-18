import sqlite3
from Sections import CourseSection
from schedule import *
from datetime import datetime
from Actors import *

class DatabaseManager:
    def __init__(self, database_filepath : str):
        self._connection = sqlite3.connect(database_filepath)
        self._cursor = self._connection.cursor()

    def __del__(self):
        self._connection.close()

    def insertNewPerson(self, person : User) -> bool:
        """
        Adds a new student, TA, or instructor to the database.
        Returns True on success. False otherwise.

        :person: The person to be added.
        """
        #check if the person already exists
        if self._getPersonID(person) != None:
            print("Error!: This person already exists.")
            return False

        #identify the person
        sql_command = ""
        if isinstance(person, Student):
            sql_command = """
            INSERT INTO "Students" (Name, Email) VALUES (?, ?);
            """
        elif isinstance(person, TA):
            sql_command = """
            INSERT INTO "TeachingAssistants" (Name, Email) VALUES (?, ?);
            """
        elif isinstance(person, Instructor):
            sql_command = """
            INSERT INTO "Instructors" (Name, Email) VALUES (?, ?);
            """
        else:
            print("Error!: This person cannot be added to the database.")
            return False
        
        #query the database
        try:
            self._cursor.execute(
                sql_command,
                (person.name, person.email)
            )
            self._connection.commit()
            return True
        except sqlite3.Error as error:
            print("Error!:", error)
            return False

    def updatePerson(self, person : User) -> bool:
        """
        Updates a student, instructor, or TA in the database.
        Returns True on success. False otherwise.

        :person: the person to be updated
        """

        #check if the person does not exists
        if self._getPersonID(person) == None:
            print("Error!: This person does not exists.")
            return False

        #identify the person
        sql_command = ""
        sql_data = None
        if isinstance(person, Student):
            sql_command = """
            UPDATE Students 
            SET (Name, Email) = (?, ?)
            WHERE Email = ?;
            """
            sql_data = (
                person.name,
                person.email,
                person.email
            )
        elif isinstance(person, TA):
            sql_command = """
            UPDATE TeachingAssistants
            SET (Name, Email, Level) = (?, ?, ?)
            WHERE Email = ?;
            """
            sql_data = (
                person.name,
                person.email,
                person.ta_type,
                person.email
            )
        elif isinstance(person, Instructor):
            sql_command = """
            UPDATE Instructors
            SET (Name, Email) = (?, ?)
            WHERE Email = ?;
            """
            sql_data = (
                person.name,
                person.email,
                person.email
            )
        else:
            print("Error!: This person cannot be updated.")
            return False
        
        #then remove the section by SQL
        try:
            self._cursor.execute(
                sql_command,
                sql_data
            )
            self._connection.commit()
            return True
        except sqlite3.Error as error:
            print("Error!:", error)
            return False

    def deletePerson(self, person : User) -> bool:
        """
        Deletes a student, instructor, or TA from the database.
        Returns True on success. False otherwise.

        :person: The person to be removed
        """

        #check if the person does not exists
        if self._getPersonID(person) == None:
            print("Error!: This person does not exists.")
            return False

        #first get all the courses this person is related to
        schedule = self.getScheduleOfPerson(person).sections

        #iterate through everyone to remove their connection
        for section in schedule:
            self._removeSectionFromPerson(person, section.crn)

        #identify the person
        sql_command = ""
        if isinstance(person, Student):
            sql_command = """
            DELETE FROM "Students" WHERE Email = ?;
            """
        elif isinstance(person, TA):
            sql_command = """
            DELETE FROM "TeachingAssistants" WHERE Email = ?;
            """
        elif isinstance(person, Instructor):
            sql_command = """
            DELETE FROM "Instructors" WHERE Email = ?;
            """
        else:
            print("Error!: This person cannot be deleted.")
            return False
        
        #then remove the section by SQL
        try:
            self._cursor.execute(
                sql_command,
                (person.email, )
            )
            self._connection.commit()
            return True
        except sqlite3.Error as error:
            print("Error!:", error)
            return False

    def insertNewSection(self, section : CourseSection) -> bool:
        """
        Adds a new section to the database.
        Returns True on success. False otherwise.

        :person: The section to be added.
        """
        #check if the person already exists
        if self._checkCRN(section.crn) == True:
            print("Error!: This section already exists.")
            return False

        #check the meeting times
        meeting_day = None
        meeting_start_time = None
        meeting_end_time = None
        meeting_time = section.meeting_time
        if meeting_time != None and meeting_time.TBD == False:
            meeting_day = meeting_time.day
            meeting_start_time = datetime.strptime(meeting_time.to_hour_minute(meeting_time.start_time), "%I:%M %p").isoformat()
            meeting_end_time = datetime.strptime(meeting_time.to_hour_minute(meeting_time.end_time), "%I:%M %p").isoformat()

        #organize the course data
        course_data = (
            section.crn,   #CRN
            section.campus,   #Campus
            section.level,   #Level
            section.section_number,   #Section
            section.subject,   #Subject
            section.number,   #Number
            section.title,   #Title
            section.enrolled_count,   #Enrollment
            section.capacity,            #Capacity
            meeting_day,  #MeetingDays
            meeting_start_time,               #MeetingStartTime
            meeting_end_time,               #MeetingEndTime
            section.meeting_room,  #MeetingRoom
        )

        #query the database
        try:
            self._cursor.execute(
                """
                INSERT INTO "Courses" VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT("CRN") DO NOTHING;
                """,
                course_data
            )
            self._connection.commit()
            return True
        except sqlite3.Error as error:
            print("Error!:", error)
            return False

    def updateSection(self, section : CourseSection) -> bool:
        """
        Deletes a section from the database.
        Returns True on success. False otherwise.

        :crn: Course Registration Number
        """

        #check if the person does not exists
        if self._checkCRN(section.crn) == False:
            print("Error!: This section does not exists.")
            return False
        
        #check the meeting times
        meeting_day = None
        meeting_start_time = None
        meeting_end_time = None
        meeting_time = section.meeting_time
        if meeting_time != None and meeting_time.TBD == False:
            meeting_day = meeting_time.day
            meeting_start_time = datetime.strptime(meeting_time.to_hour_minute(meeting_time.start_time), "%I:%M %p").isoformat()
            meeting_end_time = datetime.strptime(meeting_time.to_hour_minute(meeting_time.end_time), "%I:%M %p").isoformat()

        #organize the course data
        course_data = (
            section.campus,   #Campus
            section.level,   #Level
            section.section_number,   #Section
            section.subject,   #Subject
            section.number,   #Number
            section.title,   #Title
            section.enrolled_count,   #Enrollment
            section.capacity,            #Capacity
            meeting_day,  #MeetingDays
            meeting_start_time,               #MeetingStartTime
            meeting_end_time,               #MeetingEndTime
            section.meeting_room,  #MeetingRoom
            section.crn,            #CRN
        )

        #then update the section by SQL
        try:
            self._cursor.execute(
                """
                UPDATE Courses
                SET (Campus, 
                    Level, 
                    Section, 
                    Subject, 
                    Number, 
                    Title,
                    Enrollment,
                    Capacity,
                    MeetingDays,
                    MeetingStartTime,
                    MeetingEndTime,
                    MeetingRoom) = (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                WHERE CRN = ?;
                """,
                course_data
            )
            self._connection.commit()
            return True
        except sqlite3.Error as error:
            print("Error!:", error)
            return False

    def deleteSection(self, crn : int) -> bool:
        """
        Deletes a section from the database.
        Returns True on success. False otherwise.

        :crn: Course Registration Number
        """

        #check if the person does not exists
        if self._checkCRN(crn) == False:
            print("Error!: This section does not exists.")
            return False

        #first get everyone who is related to that section
        students = self.getStudentsFromCRN(crn)
        instructors = self.getInstructorsFromCRN(crn)
        TAs = self.getTAsFromCRN(crn)

        #iterate through everyone to remove their connection
        for s in students:
            self.removeStudentFromSection(s, crn)
        for i in instructors:
            self.removeInstructorFromSection(i, crn)
        for t in TAs:
            self.removeTAFromSection(t)
        
        #then remove the section by SQL
        try:
            self._cursor.execute(
                """
                DELETE FROM Courses WHERE CRN = ?;
                """,
                (crn, )
            )
            self._connection.commit()
            return True
        except sqlite3.Error as error:
            print("Error!:", error)
            return False

    def getAllSections(self) -> list[CourseSection]:
        """
        Get the corresponding section information from a CRN.
        Returns a CourseSection object.

        :crn: Course Registration Number
        """

        #query the database
        try:
            sql_results = self._cursor.execute(
                """
                SELECT * FROM Courses;
                """
            )
        except sqlite3.Error as error:
            print("Error!:", error)
            return
        course_tuples = sql_results.fetchall()

        #create a list
        result = []

        #fill it with all the sections
        for course_tuple in course_tuples:
            #create a MeetingTime object
            def _safeDateTime(time : str):
                try:
                    datetime.fromisoformat(time)
                    return datetime.fromisoformat(time)
                except:
                    return True
            start_time = _safeDateTime(course_tuple[10])
            end_time = _safeDateTime(course_tuple[11])

            #check if the date is TBD. If so, then mark it as such
            if start_time == True or end_time == True:
                start_time = datetime.now()
                end_time = datetime.now()
                meeting_time = MeetingTime(course_tuple[9], start_time.strftime("%H:%M"), end_time.strftime("%H:%M"), TBD=True)
            else:
                meeting_time = MeetingTime(course_tuple[9], start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))

            #create a CourseSection object
            result.append(CourseSection(
                crn=course_tuple[0],    #CRN
                campus=course_tuple[1],    #Campus
                level=course_tuple[2],    #Level
                section_number=course_tuple[3],    #Section
                subject=course_tuple[4],    #Subject
                number=course_tuple[5],    #Number (goes with above)
                title=course_tuple[6],    #Title
                meeting_time=meeting_time,       #Meeting Time
                meeting_room=course_tuple[12],   #Meeting Room
                enrolled_count=course_tuple[7],
                capacity=course_tuple[8]
            ))

        #return the object
        return result

    def getSectionFromCRN(self, crn : int) -> CourseSection:
        """
        Get the corresponding section information from a CRN.
        Returns a CourseSection object.

        :crn: Course Registration Number
        """

        #check if the CRN exists
        if self._checkCRN(crn) == False:
            print(f"Error!: This CRN [{crn}] does not exist in the database.")
            return

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
            def _safeDateTime(time : str):
                try:
                    datetime.fromisoformat(time)
                    return datetime.fromisoformat(time)
                except:
                    return True
            start_time = _safeDateTime(course_tuple[10])
            end_time = _safeDateTime(course_tuple[11])

            #check if the date is TBD. If so, then mark it as such
            if start_time == True or end_time == True:
                start_time = datetime.now()
                end_time = datetime.now()
                meeting_time = MeetingTime(course_tuple[9], start_time.strftime("%H:%M"), end_time.strftime("%H:%M"), TBD=True)
            else:
                meeting_time = MeetingTime(course_tuple[9], start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))

            #create a CourseSection object
            result = CourseSection(
                crn,
                campus=course_tuple[1],    #Campus
                level=course_tuple[2],    #Level
                section_number=course_tuple[3],    #Section
                subject=course_tuple[4],    #Subject
                number=course_tuple[5],    #Number (goes with above)
                title=course_tuple[6],    #Title
                meeting_time=meeting_time,       #Meeting Time
                meeting_room=course_tuple[12],   #Meeting Room
                enrolled_count=course_tuple[7],
                capacity=course_tuple[8]
            )

            #return the object
            return result

    def getSectionsFromSubject(self, subject : str, number : str = None) -> list[CourseSection]:
        """
        Get the corresponding section information from its subject and its number if provided.
        Returns a list of CourseSection objects.

        :subject: Three letter subject
        :number: Optional number that follows the subject (e.g., CEN 4020)
        """

        #prepare the commands
        sql_command = """
            SELECT * FROM Courses WHERE "Subject" = ?;
        """
        sql_data = (subject, )

        #if the number was specified, then add it to the command
        if number != None:
            sql_command = """
                SELECT * FROM Courses WHERE "Subject" = ? AND "Number" = ?;
            """
            sql_data = (subject, number)
        
        #query the database
        try:
            sql_results = self._cursor.execute(
                sql_command,
                sql_data
            )
        except sqlite3.Error as error:
            print("Error!:", error)
            return
        course_tuples = sql_results.fetchall()

        #create a list
        result = []

        #fill the list
        for course_tuple in course_tuples:
            #otherwise, create a MeetingTime object
            def _safeDateTime(time : str):
                try:
                    datetime.fromisoformat(time)
                    return datetime.fromisoformat(time)
                except:
                    return True
            start_time = _safeDateTime(course_tuple[10])
            end_time = _safeDateTime(course_tuple[11])

            #check if the date is TBD. If so, then mark it as such
            if start_time == True or end_time == True:
                start_time = datetime.now()
                end_time = datetime.now()
                meeting_time = MeetingTime(course_tuple[9], start_time.strftime("%H:%M"), end_time.strftime("%H:%M"), TBD=True)
            else:
                meeting_time = MeetingTime(course_tuple[9], start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))

            #create a CourseSection object
            result.append(CourseSection(
                crn=course_tuple[0],
                campus=course_tuple[1],    #Campus
                level=course_tuple[2],    #Level
                section_number=course_tuple[3],    #Section
                subject=course_tuple[4],    #Subject
                number=course_tuple[5],    #Number (goes with above)
                title=course_tuple[6],    #Title
                meeting_time=meeting_time,       #Meeting Time
                meeting_room=course_tuple[12],   #Meeting Room
                enrolled_count=course_tuple[7],
                capacity=course_tuple[8]
            ))

        #return the object
        return result

    def getAllInstructors(self) -> list[Instructor]:
        """
        Gets all Instructors.
        Returns a list of Instructor objects.
        """
        #query the database
        try:
            sql_results = self._cursor.execute(
                """
                SELECT
                    Instructors.Name,
                    Instructors.Email
                FROM Instructors;
                """
            )
        except sqlite3.Error as error:
            print("Error!", error)
            return []
        instructor_tuples = sql_results.fetchall()

        #create a list
        result = []

        #fill it with all the instructors
        for instructor_tuple in instructor_tuples:
            result.append(Instructor(instructor_tuple[0], instructor_tuple[1]))

        #return the result
        return result

    def getInstructorsFromCRN(self, crn : int) -> list[Instructor]:
        """
        Gets the Instructor from a CRN.
        Returns a list of Instructor objects.

        :crn: Course Registration Number
        """
        #query the database
        try:
            sql_results = self._cursor.execute(
                """
                SELECT
                    Instructors.Name,
                    Instructors.Email
                FROM Instructors
                    JOIN CourseInstructor ON Instructors.ID = CourseInstructor.InstructorID
                WHERE CourseInstructor.CRN = ?;
                """,
                (crn, )
            )
        except sqlite3.Error as error:
            print("Error!", error)
            return []
        instructor_tuples = sql_results.fetchall()

        #create a list
        result = []

        #fill it with all the instructors
        for instructor_tuple in instructor_tuples:
            result.append(Instructor(instructor_tuple[0], instructor_tuple[1]))

        #return the result
        return result
    
    def getAllTAs(self) -> list[TA]:
        """
        Gets all TAs.
        Returns a list of TA objects.
        """
        #query the database
        try:
            sql_results = self._cursor.execute(
                """
                SELECT
                    TeachingAssistants.Name,
                    TeachingAssistants.Email,
                    TeachingAssistants.Level
                FROM TeachingAssistants;
                """
            )
        except sqlite3.Error as error:
            print("Error!", error)
            return []
        ta_tuples = sql_results.fetchall()

        #create a list
        result = []

        #fill it with all the TAs
        for ta_tuple in ta_tuples:
            result.append(TA(ta_tuple[0], ta_tuple[1]))

        #return the result
        return result

    def getTAsFromCRN(self, crn : int) -> list[TA]:
        """
        Gets the TAs from a CRN.
        Returns a list of TA objects.

        :crn: Course Registration Number
        """
        #query the database
        try:
            sql_results = self._cursor.execute(
                """
                SELECT
                    TeachingAssistants.Name,
                    TeachingAssistants.Email,
                    TeachingAssistants.Level
                FROM TeachingAssistants
                    JOIN CourseTA ON TeachingAssistants.ID = CourseTA.TAID
                WHERE CourseTA.CRN = ?;
                """,
                (crn, )
            )
        except sqlite3.Error as error:
            print("Error!", error)
            return []
        ta_tuples = sql_results.fetchall()

        #create a list
        result = []

        #fill it with all the TAs
        for ta_tuple in ta_tuples:
            result.append(TA(ta_tuple[0], ta_tuple[1]))

        #return the result
        return result
    
    def getAllStudents(self) -> list[Student]:
        """
        Gets all Students.
        Returns a list of Student objects.
        """
        #query the database
        try:
            sql_results = self._cursor.execute(
                """
                SELECT
                    Students.Name,
                    Students.Email
                FROM Students;
                """
            )
        except sqlite3.Error as error:
            print("Error!", error)
            return []
        student_tuples = sql_results.fetchall()

        #create a list
        result = []

        #fill it with all the students
        for student_tuple in student_tuples:
            result.append(Student(student_tuple[0], student_tuple[1]))

        #return the result
        return result

    def getStudentsFromCRN(self, crn : int) -> list[Student]:
        """
        Gets the Students from a CRN.
        Returns a list of Student objects.

        :crn: Course Registration Number
        """
        #query the database
        try:
            sql_results = self._cursor.execute(
                """
                SELECT
                    Students.Name,
                    Students.Email
                FROM Students
                    JOIN CourseStudent ON Students.ID = CourseStudent.StudentID
                WHERE CourseStudent.CRN = ?;
                """,
                (crn, )
            )
        except sqlite3.Error as error:
            print("Error!", error)
            return []
        student_tuples = sql_results.fetchall()

        #create a list
        result = []

        #fill it with all the students
        for student_tuple in student_tuples:
            result.append(Student(student_tuple[0], student_tuple[1]))

        #return the result
        return result

    def getScheduleOfPerson(self, person : User) -> Schedule:
        """
        Get the schedule of a student, TA, or instructor.
        Returns a Schedule object.
        
        :person: the person who the schedule belongs to.
        """

        #identify the person
        sql_command = ""
        if isinstance(person, Student):
            sql_command = """
            SELECT
                Courses.CRN,
                Courses.Campus,
                Courses.Level,
                Courses.Section,
                Courses.Subject,
                Courses.Number,
                Courses.Title,
                Courses.Enrollment,
                Courses.Capacity,
                Courses.MeetingDays,
                Courses.MeetingStartTime,
                Courses.MeetingEndTime,
                Courses.MeetingRoom 
            FROM Courses 
                JOIN CourseStudent ON Courses.CRN = CourseStudent.CRN
                JOIN Students ON CourseStudent.StudentID = Students.ID
            WHERE Students.Email = ?;
            """
        elif isinstance(person, TA):
            sql_command = """
            SELECT
                Courses.CRN,
                Courses.Campus,
                Courses.Level,
                Courses.Section,
                Courses.Subject,
                Courses.Number,
                Courses.Title,
                Courses.Enrollment,
                Courses.Capacity,
                Courses.MeetingDays,
                Courses.MeetingStartTime,
                Courses.MeetingEndTime,
                Courses.MeetingRoom 
            FROM Courses 
                JOIN CourseTA ON Courses.CRN = CourseTA.CRN
                JOIN TeachingAssistants ON CourseTA.TAID = TeachingAssistants.ID
            WHERE TeachingAssistants.Email = ?;
            """
        elif isinstance(person, Instructor):
            sql_command = """
            SELECT 
                Courses.CRN,
                Courses.Campus,
                Courses.Level,
                Courses.Section,
                Courses.Subject,
                Courses.Number,
                Courses.Title,
                Courses.Enrollment,
                Courses.Capacity,
                Courses.MeetingDays,
                Courses.MeetingStartTime,
                Courses.MeetingEndTime,
                Courses.MeetingRoom 
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
            course_section = self.getSectionFromCRN(course_section_tuple[0])
            result.add_section(course_section)
        
        #return the schedule
        return result
    
    def _getPersonID(self, person : User) -> int:
        """
        Gets the ID of a student, TA, or instructor
        Returns None if the person is not in the database

        :person: the person in question
        """

        #identify the person
        sql_command = ""
        if isinstance(person, Student):
            sql_command = """
            SELECT "ID" FROM Students WHERE Email = ?;
            """
        elif isinstance(person, TA):
            sql_command = """
            SELECT "ID" FROM TeachingAssistants WHERE Email = ?;
            """
        elif isinstance(person, Instructor):
            sql_command = """
            SELECT "ID" FROM Instructors WHERE Email = ?;
            """
        else:
            #if it's not an acceptable person, quit
            print("Error!: The person is not a student, TA, or instructor. Please try again.")
            return
        
        #query the database
        try:
            sql_results = self._cursor.execute(
                sql_command,
                (person.email, )
            )
        except sqlite3.Error as error:
            print("Error!:", error)
            return
        tuples = sql_results.fetchall()

        #return the result
        if len(tuples) != 1:
            return None
        else:
            return tuples[0][0]

    def _checkCRN(self, crn : int) -> bool:
        """
        Checks if the CRN exists in the database.
        Returns True if so. False otherwise.

        :crn: Course Registration Number
        """

        #query the database
        try:
            sql_results = self._cursor.execute(
                """
                SELECT * FROM Courses WHERE CRN = ?;
                """,
                (crn, )
            )
        except sqlite3.Error as error:
            print("Error!:", error)
            return
        tuples = sql_results.fetchall()

        #return the result
        return len(tuples) > 0

    def _checkSectionAndPerson(self, person : User, crn : int) -> bool:
        """
        Checks if the person is already assigned to this course.
        Returns True if so. False otherwise

        :person: the person in question
        :crn: Course Registration Number
        """

        #identify the person
        sql_command = ""
        if isinstance(person, Student):
            sql_command = """
            SELECT "StudentID" 
            FROM CourseStudent 
                JOIN Students ON CourseStudent.StudentID = Students.ID
            WHERE (CRN, Students.Email) = (?, ?);
            """
        elif isinstance(person, TA):
            sql_command = """
            SELECT "TAID" 
            FROM CourseTA 
                JOIN TeachingAssistants ON CourseTA.TAID = TeachingAssistants.ID
            WHERE (CRN, TeachingAssistants.Email) = (?, ?);
            """
        elif isinstance(person, Instructor):
            sql_command = """
            SELECT "InstructorID" 
            FROM CourseInstructor
                JOIN Instructors ON CourseInstructor.InstructorID = Instructors.ID
            WHERE (CRN, Instructors.Email) = (?, ?);
            """
        else:
            #if it's not an acceptable person, quit
            print("Error!: The person is not a student, TA, or instructor. Please try again.")
            return False
        
        #query the database
        try:
            sql_results = self._cursor.execute(
                sql_command,
                (crn, person.email)
            )
        except sqlite3.Error as error:
            print("Error!:", error)
            return
        tuples = sql_results.fetchall()

        #return the result
        return len(tuples) > 0

    def _assignSectionToPerson(self, person : User, crn : int) -> bool:
        """
        Assigns a course to a student, TA, or instructor.
        Returns True on success. False otherwise
        
        :person: the person who the course belongs to.
        :crn: Course Registration Number
        """

        #check if the person and section do not exist
        id = self._getPersonID(person)
        if id == None:
            print(f"Error!: This person [{person.name}] does not exist in the database.")
            return False

        if self._checkCRN(crn) == False:
            print(f"Error!: This CRN [{crn}] does not exist in the database.")
            return False

        #check if this assignment already exists
        if self._checkSectionAndPerson(person, crn):
            print("Error!: This assignment already exists.")
            return False

        #identify the person
        sql_command = ""
        if isinstance(person, Student):
            sql_command = """
            INSERT INTO "CourseStudent" (CRN, StudentID) VALUES (?, ?);
            """
        elif isinstance(person, TA):
            sql_command = """
            INSERT INTO "CourseTA" (CRN, TAID) VALUES (?, ?);
            """
        elif isinstance(person, Instructor):
            sql_command = """
            INSERT INTO "CourseInstructor" (CRN, InstructorID) VALUES (?, ?);
            """
        else:
            print("Error!: This person cannot be assigned to a section.")
            return False
        
        #query the database
        try:
            self._cursor.execute(
                sql_command,
                (crn, id)
            )
            self._connection.commit()
            return True
        except sqlite3.Error as error:
            print("Error!:", error)
            return False

    def _removeSectionFromPerson(self, person : User, crn : int) -> bool:
        """
        Removes a course from a student, TA, or instructor.
        Returns True on success. False otherwise
        
        :person: the person who the course belongs to.
        :crn: Course Registration Number
        """

        #check if the person and section do not exist
        id = self._getPersonID(person)
        if id == None:
            print(f"Error!: This person [{person.name}] does not exist in the database.")
            return False

        if self._checkCRN(crn) == False:
            print(f"Error!: This CRN [{crn}] does not exist in the database.")
            return False

        #check if this assignment already exists
        if not self._checkSectionAndPerson(person, crn):
            print("Error!: This assignment does not exists.")
            return False

        #identify the person
        sql_command = ""
        if isinstance(person, Student):
            sql_command = """
            DELETE FROM "CourseStudent" WHERE (CRN, StudentID) = (?, ?);
            """
        elif isinstance(person, TA):
            sql_command = """
            DELETE FROM "CourseTA" WHERE (CRN, TAID) = (?, ?);
            """
        elif isinstance(person, Instructor):
            sql_command = """
            DELETE FROM "CourseInstructor" WHERE (CRN, InstructorID) = (?, ?);
            """
        else:
            print("Error!: This person cannot be removed from a section.")
            return False
        
        #query the database
        try:
            self._cursor.execute(
                sql_command,
                (crn, id)
            )
            self._connection.commit()
            return True
        except sqlite3.Error as error:
            print("Error!:", error)
            return False

    def assignInstructorToSection(self, instructor : Instructor, crn : int) -> bool:
        """
        Assigns an instructor to a section.
        Returns True on success. False otherwise.

        :instructor: Instructor
        :crn: Course Registration Number
        """
        return self._assignSectionToPerson(instructor, crn)
    
    def assignTAToSection(self, ta : TA, crn : int) -> bool:
        """
        Assigns a TA to a section.
        Returns True on success. False otherwise.

        :ta: TA
        :crn: Course Registration Number
        """
        return self._assignSectionToPerson(ta, crn)
    
    def assignStudentToSection(self, student : Student, crn : int) -> bool:
        """
        Assigns a student to a section.
        Returns True on success. False otherwise.

        :student: Student
        :crn: Course Registration Number
        """
        
        #get the section in question
        section = self.getSectionFromCRN(crn)

        #if it is not successful, return false
        if not isinstance(section, CourseSection):
            return False
        
        #also fail if the class is full
        if section.is_full():
            print("Error!: This class is full.")
            return False
        
        #otherwise, add to the junction table
        self._assignSectionToPerson(student, crn)

        #and update the enrollment counts
        self._cursor.execute(
            """
            UPDATE Courses
            SET Enrollment = Enrollment + 1
            WHERE CRN = ?;
            """,
            (crn, )
        )
        self._connection.commit()

        del section

    def assignInstructorToSection(self, instructor : Instructor, crn : int) -> bool:
        """
        Removes an instructor from a section.
        Returns True on success. False otherwise.

        :instructor: Instructor
        :crn: Course Registration Number
        """
        return self._removeSectionFromPerson(instructor, crn)
    
    def removeTAFromSection(self, ta : TA, crn : int) -> bool:
        """
        Removes a TA from a section.
        Returns True on success. False otherwise.

        :ta: TA
        :crn: Course Registration Number
        """
        return self._removeSectionFromPerson(ta, crn)
    
    def removeStudentFromSection(self, student : Student, crn : int) -> bool:
        """
        Removes a student from a section.
        Returns True on success. False otherwise.

        :student: Student
        :crn: Course Registration Number
        """
        
        #otherwise, add to the junction table
        self._removeSectionFromPerson(student, crn)

        #and update the enrollment counts
        self._cursor.execute(
            """
            UPDATE Courses
            SET Enrollment = Enrollment - 1
            WHERE CRN = ?;
            """,
            (crn, )
        )
        self._connection.commit()

    def removeInstructorFromSection(self, instructor : Instructor, crn : int) -> bool:
        """
        Removes a instructor from a section.
        Returns True on success. False otherwise.

        :instructor: Instructor
        :crn: Course Registration Number
        """
        return self._removeSectionFromPerson(instructor, crn)

    #The following are filter methods. they do not access the database.
    def filterBySubject(self, section_list : list[CourseSection], subject : str, number : str = None) -> list[CourseSection]:
        """
        Filters a list of CourseSection objects to only the sections of a specific subject (and number) specified.
        Returns a list of CourseSection objects.

        :section_list: A list of CourseSection objects
        :subject: Three letter subject
        :number: Optional number that follows the subject (e.g., CEN 4020)
        """

        #create a list
        result = []

        #iterate through the input list
        for section in section_list:
            if number != None:
                if section.subject == subject and section.number == number:
                    result.append(section)
            else:
                if section.subject == subject:
                    result.append(section)

        #return the result
        return result
    
    def filterFullSectionsOut(self, section_list : list[CourseSection]) -> list[CourseSection]:
        """
        Filters a list of CourseSection objects to only the sections that are open.
        Returns a list of CourseSection objects.

        :section_list: A list of CourseSection objects
        """

        #create a list
        result = []

        #iterate through the input list
        for section in section_list:
            if not section.is_full():
                result.append(section)

        #return the result
        return result
    
    #borrowed from France
    def _to_minutes(self, time_str):
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    def filterByTime(self, section_list : list[CourseSection], time : str) -> list[CourseSection]:
        """
        Filters a list of CourseSection objects to only the sections that are in a time period (morning, afternoon, evening).
        Sections without a meeting time will not show up.
        Returns a list of CourseSection objects.

        :section_list: A list of CourseSection objects
        :time: Either "morning", "afternoon", or "evening"
        """

        #define the cut-off time
        e_cutoff_time = None
        s_cutoff_time = None
        if time == "morning":
            e_cutoff_time = self._to_minutes("12:00")
            s_cutoff_time = self._to_minutes("6:00")
        elif time == "afternoon":
            e_cutoff_time = self._to_minutes("18:00")
            s_cutoff_time = self._to_minutes("12:00")
        elif time == "evening":
            e_cutoff_time = self._to_minutes("6:00")
            s_cutoff_time = self._to_minutes("18:00")
        else:
            print("Error!: Not a recognized time.")
            return []
        
        #create a list
        result = []

        #iterate through the input list
        for section in section_list:
            if section.meeting_time.TBD == False and section.meeting_time.start_time < e_cutoff_time and section.meeting_time.start_time >= s_cutoff_time:
                result.append(section)

        #return the result
        return result


#DEBUGGING
if __name__ == "__main__":
    dbm = DatabaseManager("./BelliniClassesS26.db")

    """
    results = dbm.getSectionFromCRN(14880)
    print(results)
    print("Is this class full?:", results.is_full())
    results = dbm.getInstructorsFromCRN(14880)
    print("The instructors is/are:", results)
    results = dbm.getTAsFromCRN(14880)
    print("The TAs is/are:", results)

    results = dbm.getSectionFromCRN(14330)
    print(results)
    print("Is this class full?:", results.is_full())
    results = dbm.getInstructorsFromCRN(14330)
    print("The instructors is/are:", results)
    results = dbm.getTAsFromCRN(14330)
    print("The TAs is/are:", results)

    results = dbm.getSectionFromCRN(16005)
    print(results)
    print("Is this class full?:", results.is_full())
    results = dbm.getInstructorsFromCRN(16005)
    print("The instructors is/are:", results)
    results = dbm.getTAsFromCRN(16005)
    print("The TAs is/are:", results)


    print("End of first round of testing.\n")

    instructor = Instructor("Hao Zheng", "haozheng@usf.edu")
    test_schedule = dbm.getScheduleOfPerson(instructor)
    print(test_schedule)

    ta = TA("David Salgado Cortes", "davids26@usf.edu")
    test_schedule = dbm.getScheduleOfPerson(ta)
    print(test_schedule)
    """

    """
    cai_sections = dbm.getSectionsFromSubject("CAI", number="5005")
    for c in cai_sections:
        print(c)
    """

    """
    dbm._assignSectionToPerson(instructor, 14)
    dbm._assignSectionToPerson(instructor, 14882)
    """

    """
    print("Instructor Count:", len(dbm.getAllInstructors()))
    print("TA Count:", len(dbm.getAllTAs()))
    print("Student Count:", len(dbm.getAllStudents()))
    print("Section Count:", len(dbm.getAllSections()))
    print()
    """

    """
    student = Student("John Doe", "test@usf.edu")
    dbm.insertNewPerson(student)
    course = dbm.getSectionFromCRN(14330)

    print("John Before Registration")
    course = dbm.getSectionFromCRN(14330)
    print(dbm.getScheduleOfPerson(student))
    print("\tEnrollment:", course.enrolled_count)
    print()

    print("John After Registration")
    dbm.assignStudentToSection(student, 14330)
    course = dbm.getSectionFromCRN(14330)
    print(dbm.getScheduleOfPerson(student))
    print("\tEnrollment:", course.enrolled_count)
    print()

    print("John After Withdrawal")
    dbm.removeStudentFromSection(student, 14330)
    course = dbm.getSectionFromCRN(14330)
    print(dbm.getScheduleOfPerson(student))
    print("\tEnrollment:", course.enrolled_count)
    print()

    student.name = "Johaness W. Doe"
    dbm.updatePerson(student)
    print(dbm.getAllStudents()[0].name)

    dbm.deletePerson(student)
    print(dbm.getAllStudents())

    course = dbm.getSectionFromCRN(14880)
    course.capacity = 1
    dbm.updateSection(course)
    course = dbm.getSectionFromCRN(14880)
    print(course.capacity)
    """

    sections = dbm.getAllSections()
    sections = dbm.filterByTime(sections, "morning")
    sections = dbm.filterFullSectionsOut(sections)
    sections = dbm.filterBySubject(sections, subject="CIS", number="4930")

    for section in sections:
        print(section)

    print("Length of results:", len(sections))

