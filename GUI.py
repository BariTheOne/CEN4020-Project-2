import tkinter as tk
from tkinter import ttk, messagebox
import json # authentication files
import os

# project imports
from DatabaseManager import DatabaseManager
from ExcelManager import ExcelManager
from Actors import User, Student, Instructor, TA, SchedulingCommitteeMember, Dean
from Sections import CourseSection
from schedule import Schedule, MeetingTime

'''
Important Notes: Any student or user added via sign-up is automatically added to DB around line 400 - 420


'''

# Constants
DB_NAME = "BelliniClassesS26"
DB_PATH = DB_NAME + ".db"
EXCEL_FILES = [
    "Bellini Classes S25.xlsx",
    "Bellini Classes S26.xlsx",
    "Bellini Classes F25.xlsx",
]
USER_FILE = "users.json"

# Colors
BG_DARK = "#1e1e2e"
BG_MID = "#2a2a3d"
BG_LIGHT = "#33334d"
FG_TEXT = "#e0e0e0"
FG_DIM = "#a0a0b0"
ACCENT = "#4fc3f7"
ACCENT_HOVER = "#81d4fa"
RED = "#ef5350"
GREEN = "#66bb6a"
GOLD = "#ffd54f"



# Json Authentication Methods
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)


def authenticate(email, password):
    users = load_users()
    if email in users and users[email]["password"] == password:
        return users[email]
    return None


def register_user(name, email, password, role):
    users = load_users()
    if email in users:
        return False
    users[email] = {"name": name, "password": password, "role": role}
    save_users(users)
    return True





# GUI Element Helpers
def make_label(parent, text, size=12, color=FG_TEXT, bold=False):
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                    font=("Segoe UI", size, weight))


def make_entry(parent, show=None, width=30):
    entry = tk.Entry(parent, font=("Segoe UI", 12), width=width,
                     bg=BG_LIGHT, fg=FG_TEXT, insertbackground=FG_TEXT,
                     relief="flat", show=show)
    entry.config(highlightthickness=2, highlightcolor=ACCENT,
                 highlightbackground=BG_MID)
    return entry


def make_button(parent, text, command, color=ACCENT, width=20):
    btn = tk.Button(parent, text=text, command=command,
                    font=("Segoe UI", 11, "bold"), fg=BG_DARK, bg=color,
                    activebackground=ACCENT_HOVER, activeforeground=BG_DARK,
                    relief="flat", cursor="hand2", width=width)
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def make_treeview(parent, columns, height=15):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=BG_MID, foreground=FG_TEXT,
                    fieldbackground=BG_MID, rowheight=28,
                    font=("Segoe UI", 10))
    style.configure("Custom.Treeview.Heading",
                    background=BG_LIGHT, foreground=ACCENT,
                    font=("Segoe UI", 10, "bold"))
    style.map("Custom.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", BG_DARK)])

    frame = tk.Frame(parent, bg=BG_DARK)
    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        height=height, style="Custom.Treeview")
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=130, anchor="center")
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return frame, tree



# Formatting Helpers
def fmt_meeting(section):
    """Format meeting time from a CourseSection object."""
    if section.meeting_time and not section.meeting_time.TBD:
        return str(section.meeting_time)
    return "TBD"


def fmt_time_only(section):
    """Just the time portion."""
    mt = section.meeting_time
    if mt and not mt.TBD:
        return f"{mt.to_hour_minute(mt.start_time)} - {mt.to_hour_minute(mt.end_time)}"
    return "TBD"


def fmt_days(section):
    if section.meeting_time and section.meeting_time.day:
        return section.meeting_time.day
    return "TBD"


def fmt_instructor(db, crn):
    """Get instructor name string for a CRN."""
    instructors = db.getInstructorsFromCRN(crn)
    if instructors:
        return ", ".join(i.name for i in instructors)
    return "TBA"



# Navigation Bar & Sidebar
class NavBar(tk.Frame):
    def __init__(self, parent, app, user_name, role_label):
        super().__init__(parent, bg=BG_MID, height=60)
        self.pack(fill="x")
        self.pack_propagate(False)

        tk.Label(self, text="🎓 Bellini College", bg=BG_MID, fg=ACCENT,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)
        tk.Label(self, text=role_label, bg=BG_MID, fg=GOLD,
                 font=("Segoe UI", 11)).pack(side="left", padx=10)

        make_button(self, "Logout", app.show_login_page, color=RED,
                    width=10).pack(side="right", padx=20, pady=12)
        tk.Label(self, text=f"Welcome, {user_name}", bg=BG_MID, fg=FG_TEXT,
                 font=("Segoe UI", 11)).pack(side="right", padx=10)


class Sidebar(tk.Frame):
    def __init__(self, parent, buttons):
        super().__init__(parent, bg=BG_MID, width=220)
        self.pack(side="left", fill="y")
        self.pack_propagate(False)

        tk.Label(self, text="Menu", bg=BG_MID, fg=ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(pady=(20, 10))
        for label, cmd in buttons:
            btn = tk.Button(self, text=label, command=cmd,
                            font=("Segoe UI", 11), fg=FG_TEXT, bg=BG_LIGHT,
                            activebackground=ACCENT, activeforeground=BG_DARK,
                            relief="flat", cursor="hand2", anchor="w", padx=20)
            btn.pack(fill="x", padx=10, pady=4, ipady=8)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=ACCENT, fg=BG_DARK))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_LIGHT, fg=FG_TEXT))




# Main App Helpers
class BelliniApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bellini College Course Registration System")
        self.attributes("-fullscreen", True)
        self.configure(bg=BG_DARK)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.bind("<F11>", lambda e: self.attributes("-fullscreen", True))

        self.current_user = None
        self.db = None

        # Build DB from Excel using Excel and Database managers if it doesn't exist
        if not os.path.exists(DB_PATH):
            for excel_file in EXCEL_FILES:
                if os.path.exists(excel_file):
                    print(f"Building database from {excel_file}...")
                    try:
                        em = ExcelManager(excel_file)
                        em.addToDatabaseFromSheet(DB_NAME)
                        print("Database created successfully.")
                    except Exception as e:
                        print(f"Error building DB: {e}")
                    break
            else:
                print("WARNING: No Excel file found. Place one of these in this folder:")
                for f in EXCEL_FILES:
                    print(f"  - {f}")

        # Connect to DB
        if os.path.exists(DB_PATH):
            try:
                self.db = DatabaseManager(DB_PATH)
                sections = self.db.getAllSections()
                print(f"Connected to DB: {len(sections)} sections loaded.")
            except Exception as e:
                print(f"DB connection error: {e}")
                self.db = None
        else:
            print("No database available. GUI will run without data.")

        self.container = tk.Frame(self, bg=BG_DARK)
        self.container.pack(fill="both", expand=True)
        self.show_login_page()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_login_page(self):
        self.current_user = None
        self.clear()
        LoginPage(self.container, self)

    def show_signup_page(self):
        self.clear()
        SignUpPage(self.container, self)

    def show_dashboard(self):
        self.clear()
        role = self.current_user["role"]
        pages = {
            "student": StudentDashboard,
            "instructor": InstructorDashboard,
            "ta": TADashboard,
            "committee": CommitteeDashboard,
            "dean": DeanDashboard,
        }
        pages.get(role, StudentDashboard)(self.container, self)



# Login Page UI
class LoginPage:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=BG_DARK)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        make_label(self.frame, "🎓 Bellini College", size=28,
                   color=ACCENT, bold=True).pack(pady=(0, 5))
        make_label(self.frame, "Course Registration System", size=14,
                   color=FG_DIM).pack(pady=(0, 40))

        card = tk.Frame(self.frame, bg=BG_MID, padx=40, pady=30)
        card.pack()

        make_label(card, "Sign In", size=18, bold=True).pack(pady=(0, 20))

        make_label(card, "Email", size=10, color=FG_DIM).pack(anchor="w")
        self.email_entry = make_entry(card)
        self.email_entry.pack(pady=(0, 15), ipady=6)

        make_label(card, "Password", size=10, color=FG_DIM).pack(anchor="w")
        self.pw_entry = make_entry(card, show="•")
        self.pw_entry.pack(pady=(0, 10), ipady=6)

        make_label(card, "Login As", size=10, color=FG_DIM).pack(
            anchor="w", pady=(10, 0))
        self.role_var = tk.StringVar(value="student")
        rf = tk.Frame(card, bg=BG_MID)
        rf.pack(pady=(0, 20))
        
        make_button(card, "Login", self.login).pack(pady=(0, 10))
        self.error_lbl = make_label(card, "", size=10, color=RED)
        self.error_lbl.pack()

        link = tk.Frame(card, bg=BG_MID)
        link.pack(pady=(15, 0))
        make_label(link, "Don't have an account?", size=10,
                   color=FG_DIM).pack(side="left")
        sl = tk.Label(link, text=" Sign Up", bg=BG_MID, fg=ACCENT,
                      font=("Segoe UI", 10, "bold"), cursor="hand2")
        sl.pack(side="left")
        sl.bind("<Button-1>", lambda e: self.app.show_signup_page())
        self.pw_entry.bind("<Return>", lambda e: self.login())

    def login(self):
        email = self.email_entry.get().strip()
        pw = self.pw_entry.get().strip()
        if not email or not pw:
            self.error_lbl.config(text="Please fill in all fields.")
            return
        user = authenticate(email, pw)
        if user:
            self.app.current_user = {
                "name": user["name"], "email": email, "role": user["role"]}
            self.app.show_dashboard()
        else:
            self.error_lbl.config(text="Invalid email or password.")




# Sign Up Page UI
class SignUpPage:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=BG_DARK)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        make_label(self.frame, "Create Account", size=24,
                   color=ACCENT, bold=True).pack(pady=(0, 30))

        card = tk.Frame(self.frame, bg=BG_MID, padx=40, pady=30)
        card.pack()

        make_label(card, "Full Name", size=10, color=FG_DIM).pack(anchor="w")
        self.name_entry = make_entry(card)
        self.name_entry.pack(pady=(0, 15), ipady=6)

        make_label(card, "Email", size=10, color=FG_DIM).pack(anchor="w")
        self.email_entry = make_entry(card)
        self.email_entry.pack(pady=(0, 15), ipady=6)

        make_label(card, "Password", size=10, color=FG_DIM).pack(anchor="w")
        self.pw_entry = make_entry(card, show="•")
        self.pw_entry.pack(pady=(0, 15), ipady=6)

        make_label(card, "Confirm Password", size=10, color=FG_DIM).pack(anchor="w")
        self.confirm_entry = make_entry(card, show="•")
        self.confirm_entry.pack(pady=(0, 10), ipady=6)

        make_label(card, "Register As", size=10, color=FG_DIM).pack(
            anchor="w", pady=(10, 0))
        self.role_var = tk.StringVar(value="student")
        rf = tk.Frame(card, bg=BG_MID)
        rf.pack(pady=(0, 20))
        for text, val in [("Student", "student"), ("Instructor", "instructor"),
                          ("TA", "ta"), ("Committee", "committee"),
                          ("Dean", "dean")]:
            tk.Radiobutton(rf, text=text, variable=self.role_var, value=val,
                           bg=BG_MID, fg=FG_TEXT, selectcolor=BG_LIGHT,
                           activebackground=BG_MID, activeforeground=ACCENT,
                           font=("Segoe UI", 10)).pack(side="left", padx=8)

        bf = tk.Frame(card, bg=BG_MID)
        bf.pack()
        make_button(bf, "Sign Up", self.signup, width=14).pack(side="left", padx=5)
        make_button(bf, "Back", self.app.show_login_page,
                    color=FG_DIM, width=14).pack(side="left", padx=5)

        self.error_lbl = make_label(card, "", size=10, color=RED)
        self.error_lbl.pack(pady=(10, 0))

    def signup(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        pw = self.pw_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        role = self.role_var.get()

        if not all([name, email, pw, confirm]):
            self.error_lbl.config(text="Please fill in all fields.")
            return
        if pw != confirm:
            self.error_lbl.config(text="Passwords do not match.")
            return
        if not register_user(name, email, pw, role):
            self.error_lbl.config(text="Email already registered.")
            return

        # Also add the person to the Bellini DB
        if self.app.db:
            try:
                if role == "student":
                    self.app.db.insertNewPerson(Student(name, email))
                elif role == "instructor":
                    self.app.db.insertNewPerson(Instructor(name, email))
                elif role == "ta":
                    self.app.db.insertNewPerson(TA(name, email))
            except Exception as e:
                print(f"DB insert on signup: {e}")

        messagebox.showinfo("Success", "Account created! Please log in.")
        self.app.show_login_page()




# Student Dashboard
class StudentDashboard:
    def __init__(self, parent, app):
        self.app = app
        self.db = app.db
        self.email = app.current_user["email"]
        self.name = app.current_user["name"]
        self.student = Student(self.name, self.email)

        NavBar(parent, app, self.name, "Student")
        body = tk.Frame(parent, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        Sidebar(body, [
            ("📅 My Schedule", self.show_schedule),
            ("📚 Browse Classes", self.show_browse),
            ("➕ Register", self.show_register),
            ("❌ Drop Class", self.show_drop),
            ("🔍 Filter by Time", self.show_filter),
        ])

        self.content = tk.Frame(body, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.show_schedule()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_schedule(self):
        self.clear_content()
        make_label(self.content, "📅 My Weekly Schedule (UC07 / US10)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        cols = ("CRN", "Course", "Title", "Section", "Days",
                "Time", "Room", "Instructor")
        frame, tree = make_treeview(self.content, cols, height=14)
        tree.column("Title", width=200)
        tree.column("Instructor", width=180)
        frame.pack(fill="both", expand=True)

        if not self.db:
            return
        try:
            schedule = self.db.getScheduleOfPerson(self.student)
            if schedule:
                for s in schedule.get_all_sections():
                    tree.insert("", "end", values=(
                        s.crn, f"{s.subject} {s.number}", s.title,
                        s.section_number, fmt_days(s), fmt_time_only(s),
                        s.meeting_room or "TBA", fmt_instructor(self.db, s.crn)
                    ))
        except Exception as e:
            print(f"Schedule error: {e}")

    def show_browse(self):
        self.clear_content()
        make_label(self.content, "📚 Browse All Classes (UC15)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 10))

        ctrl = tk.Frame(self.content, bg=BG_DARK)
        ctrl.pack(anchor="w", fill="x", pady=(0, 10))

        self.hide_full_var = tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl, text="Hide Full Classes (UC10 / US08)",
                       variable=self.hide_full_var, bg=BG_DARK, fg=FG_TEXT,
                       selectcolor=BG_LIGHT, activebackground=BG_DARK,
                       activeforeground=ACCENT, font=("Segoe UI", 10),
                       command=self.refresh_browse).pack(side="left")

        make_label(ctrl, "  Search:", size=11).pack(side="left", padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_entry = make_entry(ctrl, width=20)
        self.search_entry.pack(side="left")
        make_button(ctrl, "Search", self.refresh_browse,
                    width=8).pack(side="left", padx=5)
        make_button(ctrl, "Clear", self.clear_search,
                    color=FG_DIM, width=8).pack(side="left", padx=5)

        cols = ("CRN", "Course", "Title", "Section", "Days", "Time",
                "Room", "Enrolled", "Capacity", "Status")
        frame, self.browse_tree = make_treeview(self.content, cols, height=14)
        self.browse_tree.column("Title", width=200)
        frame.pack(fill="both", expand=True)
        self.refresh_browse()

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.refresh_browse()

    def refresh_browse(self):
        for row in self.browse_tree.get_children():
            self.browse_tree.delete(row)
        if not self.db:
            return

        sections = self.db.getAllSections()
        if self.hide_full_var.get():
            sections = self.db.filterFullSectionsOut(sections)

        query = self.search_entry.get().strip().upper()

        for s in sections:
            searchable = f"{s.crn} {s.subject} {s.number} {s.title}".upper()
            if query and query not in searchable:
                continue
            status = "Full" if s.is_full() else "Open"
            self.browse_tree.insert("", "end", values=(
                s.crn, f"{s.subject} {s.number}", s.title,
                s.section_number, fmt_days(s), fmt_time_only(s),
                s.meeting_room or "TBA", s.enrolled_count,
                s.capacity, status
            ))

    def show_register(self):
        self.clear_content()
        make_label(self.content, "➕ Register for a Class (UC11)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        row = tk.Frame(self.content, bg=BG_DARK)
        row.pack(anchor="w", pady=(0, 15))
        make_label(row, "Enter CRN:", size=12).pack(side="left", padx=(0, 10))
        self.reg_crn = make_entry(row, width=15)
        self.reg_crn.pack(side="left")
        make_button(row, "Register", self.do_register, width=12).pack(
            side="left", padx=10)

        self.reg_status = make_label(self.content, "", size=11)
        self.reg_status.pack(anchor="w")

    def do_register(self):
        crn_str = self.reg_crn.get().strip()
        if not crn_str:
            self.reg_status.config(text="Please enter a CRN.", fg=RED)
            return
        if not self.db:
            self.reg_status.config(text="Database not available.", fg=RED)
            return
        try:
            crn = int(crn_str)
        except ValueError:
            self.reg_status.config(text="CRN must be a number.", fg=RED)
            return

        section = self.db.getSectionFromCRN(crn)
        if not section:
            self.reg_status.config(text=f"CRN {crn} not found.", fg=RED)
            return
        if section.is_full():
            self.reg_status.config(text=f"CRN {crn} is full.", fg=RED)
            return

        # Ensure student exists in DB
        if self.db._getPersonID(self.student) is None:
            self.db.insertNewPerson(self.student)

        result = self.db.assignStudentToSection(self.student, crn)
        if result is False:
            self.reg_status.config(text="Already registered or error.", fg=RED)
        else:
            self.reg_status.config(
                text=f"✓ Registered for {section.subject} {section.number} (CRN {crn})",
                fg=GREEN)

    def show_drop(self):
        self.clear_content()
        make_label(self.content, "❌ Drop a Class", size=18,
                   color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        row = tk.Frame(self.content, bg=BG_DARK)
        row.pack(anchor="w", pady=(0, 15))
        make_label(row, "Enter CRN:", size=12).pack(side="left", padx=(0, 10))
        self.drop_crn = make_entry(row, width=15)
        self.drop_crn.pack(side="left")
        make_button(row, "Drop", self.do_drop, color=RED, width=12).pack(
            side="left", padx=10)

        self.drop_status = make_label(self.content, "", size=11)
        self.drop_status.pack(anchor="w")

    def do_drop(self):
        crn_str = self.drop_crn.get().strip()
        if not crn_str or not self.db:
            self.drop_status.config(text="Enter a valid CRN.", fg=RED)
            return
        try:
            crn = int(crn_str)
        except ValueError:
            self.drop_status.config(text="CRN must be a number.", fg=RED)
            return

        try:
            self.db.removeStudentFromSection(self.student, crn)
            self.drop_status.config(text=f"✓ Dropped CRN {crn}.", fg=GREEN)
        except Exception as e:
            self.drop_status.config(text=f"Error: {e}", fg=RED)

    def show_filter(self):
        self.clear_content()
        make_label(self.content, "🔍 Filter Classes by Time (UC03 / US09)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        row = tk.Frame(self.content, bg=BG_DARK)
        row.pack(anchor="w", pady=(0, 10))
        self.time_var = tk.StringVar(value="morning")
        for text, val in [("Morning (before 12pm)", "morning"),
                          ("Afternoon (12pm-6pm)", "afternoon"),
                          ("Evening (after 6pm)", "evening")]:
            tk.Radiobutton(row, text=text, variable=self.time_var, value=val,
                           bg=BG_DARK, fg=FG_TEXT, selectcolor=BG_LIGHT,
                           activebackground=BG_DARK, activeforeground=ACCENT,
                           font=("Segoe UI", 11)).pack(side="left", padx=10)

        ctrl2 = tk.Frame(self.content, bg=BG_DARK)
        ctrl2.pack(anchor="w", pady=(0, 10))
        self.filter_hide_full = tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl2, text="Hide Full Classes",
                       variable=self.filter_hide_full, bg=BG_DARK, fg=FG_TEXT,
                       selectcolor=BG_LIGHT, font=("Segoe UI", 10)
                       ).pack(side="left")
        make_button(ctrl2, "Apply Filter", self.apply_filter,
                    width=12).pack(side="left", padx=15)

        cols = ("CRN", "Course", "Title", "Days", "Time",
                "Room", "Enrolled", "Capacity")
        frame, self.filter_tree = make_treeview(self.content, cols, height=12)
        self.filter_tree.column("Title", width=200)
        frame.pack(fill="both", expand=True, pady=(10, 0))

    def apply_filter(self):
        for row in self.filter_tree.get_children():
            self.filter_tree.delete(row)
        if not self.db:
            return
        sections = self.db.getAllSections()
        sections = self.db.filterByTime(sections, self.time_var.get())
        if self.filter_hide_full.get():
            sections = self.db.filterFullSectionsOut(sections)
        for s in sections:
            self.filter_tree.insert("", "end", values=(
                s.crn, f"{s.subject} {s.number}", s.title,
                fmt_days(s), fmt_time_only(s),
                s.meeting_room or "TBA", s.enrolled_count, s.capacity
            ))



# Instructor Dashboard
class InstructorDashboard:
    def __init__(self, parent, app):
        self.app = app
        self.db = app.db
        self.email = app.current_user["email"]
        self.name = app.current_user["name"]
        self.instructor = Instructor(self.name, self.email)

        NavBar(parent, app, self.name, "Instructor")
        body = tk.Frame(parent, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        Sidebar(body, [
            ("📅 Teaching Schedule", self.show_schedule),
            ("👥 Student List", self.show_students),
        ])

        self.content = tk.Frame(body, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.show_schedule()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_schedule(self):
        self.clear_content()
        make_label(self.content, "📅 My Teaching Schedule (UC01 / US03)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        cols = ("CRN", "Course", "Title", "Section", "Days", "Time", "Room")
        frame, tree = make_treeview(self.content, cols, height=14)
        tree.column("Title", width=200)
        frame.pack(fill="both", expand=True)

        if not self.db:
            return
        try:
            schedule = self.db.getScheduleOfPerson(self.instructor)
            if schedule:
                for s in schedule.get_all_sections():
                    tree.insert("", "end", values=(
                        s.crn, f"{s.subject} {s.number}", s.title,
                        s.section_number, fmt_days(s), fmt_time_only(s),
                        s.meeting_room or "TBA"
                    ))
        except Exception as e:
            print(f"Instructor schedule error: {e}")

    def show_students(self):
        self.clear_content()
        make_label(self.content, "👥 Students in My Courses (UC09 / US04)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        row = tk.Frame(self.content, bg=BG_DARK)
        row.pack(anchor="w", pady=(0, 15))
        make_label(row, "Select Course:", size=12).pack(side="left", padx=(0, 10))

        self.crn_combo = ttk.Combobox(row, font=("Segoe UI", 12), width=30,
                                       state="readonly")
        self.crn_combo.pack(side="left")
        make_button(row, "Load Students", self.load_students,
                    width=14).pack(side="left", padx=10)

        # Populate combo
        self.crn_map = {}
        if self.db:
            try:
                schedule = self.db.getScheduleOfPerson(self.instructor)
                if schedule:
                    vals = []
                    for s in schedule.get_all_sections():
                        label = f"{s.crn} - {s.subject} {s.number} ({s.title})"
                        vals.append(label)
                        self.crn_map[label] = s.crn
                    self.crn_combo["values"] = vals
            except Exception:
                pass

        cols = ("Name", "Email")
        frame, self.student_tree = make_treeview(self.content, cols, height=12)
        self.student_tree.column("Name", width=250)
        self.student_tree.column("Email", width=300)
        frame.pack(fill="both", expand=True, pady=(10, 0))

    def load_students(self):
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)
        sel = self.crn_combo.get()
        if not sel or not self.db:
            return
        crn = self.crn_map.get(sel)
        if crn:
            students = self.db.getStudentsFromCRN(crn)
            for s in students:
                self.student_tree.insert("", "end", values=(s.name, s.email))
            if not students:
                self.student_tree.insert("", "end",
                                          values=("No students registered", ""))



# TA Dashboard
class TADashboard:
    def __init__(self, parent, app):
        self.app = app
        self.db = app.db
        self.email = app.current_user["email"]
        self.name = app.current_user["name"]
        self.ta = TA(self.name, self.email)

        NavBar(parent, app, self.name, "Teaching Assistant")
        body = tk.Frame(parent, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        Sidebar(body, [("📅 Work Schedule", self.show_schedule)])

        self.content = tk.Frame(body, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.show_schedule()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_schedule(self):
        self.clear_content()
        make_label(self.content, "📅 My Work Schedule (UC08 / US07)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        cols = ("CRN", "Course", "Title", "Days", "Time", "Room", "Instructor")
        frame, tree = make_treeview(self.content, cols, height=14)
        tree.column("Title", width=200)
        tree.column("Instructor", width=180)
        frame.pack(fill="both", expand=True)

        if not self.db:
            return
        try:
            schedule = self.db.getScheduleOfPerson(self.ta)
            if schedule:
                for s in schedule.get_all_sections():
                    tree.insert("", "end", values=(
                        s.crn, f"{s.subject} {s.number}", s.title,
                        fmt_days(s), fmt_time_only(s),
                        s.meeting_room or "TBA",
                        fmt_instructor(self.db, s.crn)
                    ))
        except Exception as e:
            print(f"TA schedule error: {e}")



# Committee Dashboard
class CommitteeDashboard:
    def __init__(self, parent, app):
        self.app = app
        self.db = app.db
        self.name = app.current_user["name"]

        NavBar(parent, app, self.name, "Scheduling Committee")
        body = tk.Frame(parent, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        Sidebar(body, [
            ("📊 Instructor Workload", self.show_workload),
            ("📝 Assign Classes", self.show_assign),
            ("📋 Generate Report", self.show_report),
            ("📅 All Sections", self.show_all_sections),
            ("➕ Add Section", self.show_add_section),
            ("❌ Delete Section", self.show_delete_section),
        ])

        self.content = tk.Frame(body, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.show_workload()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_workload(self):
        self.clear_content()
        make_label(self.content, "📊 Instructor Workload (UC02 / US05)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        cols = ("Instructor", "Email", "# Classes", "Courses")
        frame, tree = make_treeview(self.content, cols, height=16)
        tree.column("Instructor", width=180)
        tree.column("Email", width=220)
        tree.column("Courses", width=400)
        frame.pack(fill="both", expand=True)

        if not self.db:
            return
        instructors = self.db.getAllInstructors()
        for inst in instructors:
            schedule = self.db.getScheduleOfPerson(inst)
            sections = schedule.get_all_sections() if schedule else []
            courses = ", ".join(f"{s.subject} {s.number}" for s in sections)
            tree.insert("", "end", values=(
                inst.name, inst.email, len(sections), courses or "None"
            ))

    def show_assign(self):
        self.clear_content()
        make_label(self.content, "📝 Assign to Classes (UC12 / US01)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        form = tk.Frame(self.content, bg=BG_DARK)
        form.pack(anchor="w", pady=(0, 15))

        fields = [("CRN:", "crn"), ("Person Email:", "email"),
                  ("Role (student/instructor/ta):", "role")]
        self.assign_entries = {}
        for label_text, key in fields:
            r = tk.Frame(form, bg=BG_DARK)
            r.pack(anchor="w", pady=4)
            lbl = make_label(r, label_text, size=11, color=FG_DIM)
            lbl.config(width=30, anchor="e")
            lbl.pack(side="left", padx=(0, 10))
            entry = make_entry(r, width=25)
            entry.pack(side="left")
            self.assign_entries[key] = entry

        btn_row = tk.Frame(form, bg=BG_DARK)
        btn_row.pack(anchor="w", pady=(15, 0))
        make_button(btn_row, "Assign", self.do_assign, width=14).pack(
            side="left", padx=5)
        make_button(btn_row, "Remove", self.do_remove,
                    color=RED, width=14).pack(side="left", padx=5)

        self.assign_status = make_label(self.content, "", size=11)
        self.assign_status.pack(anchor="w", pady=(10, 0))

    def do_assign(self):
        crn_str = self.assign_entries["crn"].get().strip()
        email = self.assign_entries["email"].get().strip()
        role = self.assign_entries["role"].get().strip().lower()

        if not crn_str or not email or not role:
            self.assign_status.config(text="All fields required.", fg=RED)
            return
        if not self.db:
            return
        try:
            crn = int(crn_str)
        except ValueError:
            self.assign_status.config(text="CRN must be a number.", fg=RED)
            return

        person = None
        if role == "student":
            person = Student("", email)
        elif role == "instructor":
            person = Instructor("", email)
        elif role == "ta":
            person = TA("", email)
        else:
            self.assign_status.config(text="Role must be student/instructor/ta.", fg=RED)
            return

        result = self.db._assignSectionToPerson(person, crn)
        if result:
            self.assign_status.config(text=f"✓ Assigned {email} to CRN {crn}.", fg=GREEN)
        else:
            self.assign_status.config(text="Assignment failed. Check email/CRN.", fg=RED)

    def do_remove(self):
        crn_str = self.assign_entries["crn"].get().strip()
        email = self.assign_entries["email"].get().strip()
        role = self.assign_entries["role"].get().strip().lower()

        if not crn_str or not email or not role:
            self.assign_status.config(text="All fields required.", fg=RED)
            return
        if not self.db:
            return
        try:
            crn = int(crn_str)
        except ValueError:
            self.assign_status.config(text="CRN must be a number.", fg=RED)
            return

        person = None
        if role == "student":
            person = Student("", email)
        elif role == "instructor":
            person = Instructor("", email)
        elif role == "ta":
            person = TA("", email)
        else:
            self.assign_status.config(text="Role must be student/instructor/ta.", fg=RED)
            return

        result = self.db._removeSectionFromPerson(person, crn)
        if result:
            self.assign_status.config(text=f"✓ Removed {email} from CRN {crn}.", fg=GREEN)
        else:
            self.assign_status.config(text="Removal failed.", fg=RED)

    def show_report(self):
        self.clear_content()
        make_label(self.content, "📋 Scheduling Report (UC14 / US02)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        make_button(self.content, "Generate Report", self.do_report,
                    width=18).pack(anchor="w", pady=(0, 15))

        self.report_text = tk.Text(self.content, bg=BG_MID, fg=FG_TEXT,
                                    font=("Consolas", 11), relief="flat",
                                    wrap="word", height=25)
        self.report_text.pack(fill="both", expand=True)

    def do_report(self):
        self.report_text.delete("1.0", "end")
        if not self.db:
            self.report_text.insert("1.0", "Database not available.")
            return

        # Use DatabaseManager's built-in report generator
        report_name = "GUI_Scheduling_Report"
        try:
            clean = self.db.generateReportFromDatabase(file_name=report_name)
            # Read the generated file
            report_file = report_name + f"{self.db._name}.txt"
            if os.path.exists(report_file):
                with open(report_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.report_text.insert("1.0", content)
                if clean:
                    self.report_text.insert("end", "\n\n✓ No conflicts found!")
                else:
                    self.report_text.insert("end", "\n\n⚠ Conflicts detected. Review above.")
            else:
                self.report_text.insert("1.0", "Report file not found.")
        except Exception as e:
            self.report_text.insert("1.0", f"Error generating report: {e}")

    def show_all_sections(self):
        self.clear_content()
        make_label(self.content, "📅 All Class Sections",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 10))

        ctrl = tk.Frame(self.content, bg=BG_DARK)
        ctrl.pack(anchor="w", fill="x", pady=(0, 10))
        make_label(ctrl, "Search:", size=11).pack(side="left", padx=(0, 5))
        self.all_search = make_entry(ctrl, width=20)
        self.all_search.pack(side="left")
        make_button(ctrl, "Search", self.load_all_sections,
                    width=8).pack(side="left", padx=5)
        make_button(ctrl, "Show All", lambda: (
            self.all_search.delete(0, "end"), self.load_all_sections()),
                    color=FG_DIM, width=8).pack(side="left", padx=5)

        cols = ("CRN", "Course", "Title", "Section", "Days", "Time",
                "Room", "Instructor", "Enrolled", "Capacity")
        frame, self.all_tree = make_treeview(self.content, cols, height=16)
        self.all_tree.column("Title", width=200)
        self.all_tree.column("Instructor", width=180)
        frame.pack(fill="both", expand=True)
        self.load_all_sections()

    def load_all_sections(self):
        for row in self.all_tree.get_children():
            self.all_tree.delete(row)
        if not self.db:
            return
        query = self.all_search.get().strip().upper() if hasattr(self, 'all_search') else ""
        sections = self.db.getAllSections()
        for s in sections:
            searchable = f"{s.crn} {s.subject} {s.number} {s.title}".upper()
            if query and query not in searchable:
                continue
            self.all_tree.insert("", "end", values=(
                s.crn, f"{s.subject} {s.number}", s.title,
                s.section_number, fmt_days(s), fmt_time_only(s),
                s.meeting_room or "TBA",
                fmt_instructor(self.db, s.crn),
                s.enrolled_count, s.capacity
            ))

    def show_add_section(self):
        self.clear_content()
        make_label(self.content, "➕ Add New Section",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        form = tk.Frame(self.content, bg=BG_DARK)
        form.pack(anchor="w")

        fields = [
            ("CRN:", "crn"), ("Campus:", "campus"), ("Level (UG/GR):", "level"),
            ("Section Number:", "section"), ("Subject:", "subject"),
            ("Course Number:", "number"), ("Title:", "title"),
            ("Room:", "room"), ("Days (MW/TR/F):", "days"),
            ("Start Time (HH:MM, 24hr):", "start"),
            ("End Time (HH:MM, 24hr):", "end"),
            ("Capacity:", "capacity"),
        ]
        self.add_entries = {}
        for label_text, key in fields:
            r = tk.Frame(form, bg=BG_DARK)
            r.pack(anchor="w", pady=3)
            lbl = make_label(r, label_text, size=10, color=FG_DIM)
            lbl.config(width=28, anchor="e")
            lbl.pack(side="left", padx=(0, 10))
            entry = make_entry(r, width=25)
            entry.pack(side="left")
            self.add_entries[key] = entry

        make_button(form, "Add Section", self.do_add_section,
                    width=14).pack(anchor="w", pady=(15, 0))
        self.add_status = make_label(self.content, "", size=11)
        self.add_status.pack(anchor="w", pady=(10, 0))

    def do_add_section(self):
        v = {k: e.get().strip() for k, e in self.add_entries.items()}
        if not v["crn"] or not v["subject"] or not v["number"] or not v["title"]:
            self.add_status.config(text="CRN, Subject, Number, Title required.", fg=RED)
            return

        mt = None
        if v["days"] and v["start"] and v["end"]:
            mt = MeetingTime(v["days"], v["start"], v["end"])
        else:
            mt = MeetingTime(None, "0:00", "0:00", TBD=True)

        try:
            section = CourseSection(
                crn=int(v["crn"]),
                campus=v["campus"] or "Tampa",
                level=v["level"] or "UG",
                section_number=v["section"] or "001",
                subject=v["subject"],
                number=v["number"],
                title=v["title"],
                meeting_time=mt,
                meeting_room=v["room"] or None,
                enrolled_count=0,
                capacity=int(v["capacity"]) if v["capacity"] else 30,
            )
            result = self.db.insertNewSection(section)
            if result:
                self.add_status.config(text=f"✓ Added CRN {v['crn']}.", fg=GREEN)
            else:
                self.add_status.config(text="Section already exists or error.", fg=RED)
        except Exception as e:
            self.add_status.config(text=f"Error: {e}", fg=RED)

    def show_delete_section(self):
        self.clear_content()
        make_label(self.content, "❌ Delete Section",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        row = tk.Frame(self.content, bg=BG_DARK)
        row.pack(anchor="w", pady=(0, 15))
        make_label(row, "Enter CRN:", size=12).pack(side="left", padx=(0, 10))
        self.del_crn = make_entry(row, width=15)
        self.del_crn.pack(side="left")
        make_button(row, "Delete", self.do_delete_section,
                    color=RED, width=12).pack(side="left", padx=10)

        self.del_status = make_label(self.content, "", size=11)
        self.del_status.pack(anchor="w")

    def do_delete_section(self):
        crn_str = self.del_crn.get().strip()
        if not crn_str or not self.db:
            self.del_status.config(text="Enter a CRN.", fg=RED)
            return
        try:
            crn = int(crn_str)
            if messagebox.askyesno("Confirm", f"Delete CRN {crn}? This cannot be undone."):
                result = self.db.deleteSection(crn)
                if result:
                    self.del_status.config(text=f"✓ Deleted CRN {crn}.", fg=GREEN)
                else:
                    self.del_status.config(text="Section not found or error.", fg=RED)
        except ValueError:
            self.del_status.config(text="CRN must be a number.", fg=RED)



# Dean Dashboard
class DeanDashboard:
    def __init__(self, parent, app):
        self.app = app
        self.db = app.db
        self.name = app.current_user["name"]

        NavBar(parent, app, self.name, "Dean")
        body = tk.Frame(parent, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        Sidebar(body, [
            ("📊 Registration Analysis", self.show_analysis),
            ("📅 All Sections", self.show_all_sections),
        ])

        self.content = tk.Frame(body, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.show_analysis()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_analysis(self):
        self.clear_content()
        make_label(self.content, "📊 Course Registration Analysis (UC04 / US06)",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        make_button(self.content, "Run Analysis", self.do_analysis,
                    width=16).pack(anchor="w", pady=(0, 15))

        cols = ("Course", "Title", "Enrolled", "Capacity",
                "# Sections", "Avg per Section", "Demand")
        frame, self.analysis_tree = make_treeview(self.content, cols, height=16)
        self.analysis_tree.column("Title", width=220)
        frame.pack(fill="both", expand=True)

    def do_analysis(self):
        for row in self.analysis_tree.get_children():
            self.analysis_tree.delete(row)
        if not self.db:
            return

        sections = self.db.getAllSections()

        # Group by course (subject + number)
        data = {}
        for s in sections:
            key = f"{s.subject} {s.number}"
            if key not in data:
                data[key] = {"title": s.title, "enrolled": 0,
                             "capacity": 0, "count": 0}
            data[key]["enrolled"] += s.enrolled_count
            data[key]["capacity"] += s.capacity
            data[key]["count"] += 1

        sorted_data = sorted(data.items(), key=lambda x: x[1]["enrolled"],
                             reverse=True)
        for course, d in sorted_data:
            avg = d["enrolled"] // d["count"] if d["count"] else 0
            if d["enrolled"] >= 100:
                demand = "🔴 High"
            elif d["enrolled"] >= 40:
                demand = "🟡 Medium"
            else:
                demand = "🟢 Low"
            self.analysis_tree.insert("", "end", values=(
                course, d["title"], d["enrolled"], d["capacity"],
                d["count"], avg, demand
            ))

    def show_all_sections(self):
        self.clear_content()
        make_label(self.content, "📅 All Class Sections",
                   size=18, color=ACCENT, bold=True).pack(anchor="w", pady=(0, 15))

        cols = ("CRN", "Course", "Title", "Days", "Time",
                "Room", "Enrolled", "Capacity")
        frame, tree = make_treeview(self.content, cols, height=18)
        tree.column("Title", width=200)
        frame.pack(fill="both", expand=True)

        if not self.db:
            return
        for s in self.db.getAllSections():
            tree.insert("", "end", values=(
                s.crn, f"{s.subject} {s.number}", s.title,
                fmt_days(s), fmt_time_only(s),
                s.meeting_room or "TBA", s.enrolled_count, s.capacity
            ))



# Run the GUI on running the program.
if __name__ == "__main__":
    app = BelliniApp()
    app.protocol("WM_DELETE_WINDOW", lambda: app.destroy())
    app.mainloop()
