# dialogs.py - Additional CRUD Dialogs
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import mysql.connector

def db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="lequyen5002",   # sửa theo password MySQL của bạn
        database="student_management"
    )

# ==================== SUBJECT DIALOG ====================
class SubjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Subject")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("e.g., CS101")
        form_layout.addRow("Subject Code *:", self.txt_code)
        
        self.txt_name = QLineEdit()
        form_layout.addRow("Subject Name *:", self.txt_name)
        
        self.spin_credits = QSpinBox()
        self.spin_credits.setRange(1, 10)
        self.spin_credits.setValue(3)
        form_layout.addRow("Credits *:", self.spin_credits)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Add Subject")
        btn_save.clicked.connect(self.save_subject)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def save_subject(self):
        code = self.txt_code.text().strip()
        name = self.txt_name.text().strip()
        credits = self.spin_credits.value()
        
        if not code or not name:
            QMessageBox.warning(self, "Validation Error", "All fields are required!")
            return
        
        query = "INSERT INTO subjects (SubjectCode, SubjectName, Credits) VALUES (%s, %s, %s)"
        result = db.execute_insert(query, (code, name, credits))
        
        if result:
            QMessageBox.information(self, "Success", "Subject added successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add subject! Code might already exist.")

# ==================== LECTURER DIALOG ====================
class LecturerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Lecturer")
        self.setModal(True)
        self.resize(400, 250)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.txt_first_name = QLineEdit()
        form_layout.addRow("First Name *:", self.txt_first_name)
        
        self.txt_last_name = QLineEdit()
        form_layout.addRow("Last Name *:", self.txt_last_name)
        
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("lecturer@example.com")
        form_layout.addRow("Email:", self.txt_email)
        
        self.txt_office = QLineEdit()
        self.txt_office.setPlaceholderText("e.g., B201")
        form_layout.addRow("Office:", self.txt_office)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Add Lecturer")
        btn_save.clicked.connect(self.save_lecturer)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def save_lecturer(self):
        first_name = self.txt_first_name.text().strip()
        last_name = self.txt_last_name.text().strip()
        email = self.txt_email.text().strip()
        office = self.txt_office.text().strip()
        
        if not first_name or not last_name:
            QMessageBox.warning(self, "Validation Error", "First and last name are required!")
            return
        
        query = """
            INSERT INTO lecturers (LecturerFirstName, LecturerLastName, LecturerEmail, Office)
            VALUES (%s, %s, %s, %s)
        """
        result = db.execute_insert(query, (first_name, last_name, email, office))
        
        if result:
            QMessageBox.information(self, "Success", "Lecturer added successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add lecturer!")

# ==================== CLASS DIALOG ====================
class ClassDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Class")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Subject Code (ComboBox)
        self.combo_subject = QComboBox()
        self.load_subjects()
        form_layout.addRow("Subject *:", self.combo_subject)
        
        # Lecturer (ComboBox)
        self.combo_lecturer = QComboBox()
        self.load_lecturers()
        form_layout.addRow("Lecturer:", self.combo_lecturer)
        
        # Class Name
        self.txt_class_name = QLineEdit()
        self.txt_class_name.setPlaceholderText("e.g., Group 1")
        form_layout.addRow("Class Name:", self.txt_class_name)
        
        # Semester
        self.combo_semester = QComboBox()
        self.combo_semester.addItems(["S1", "S2", "S3", "Summer"])
        form_layout.addRow("Semester *:", self.combo_semester)
        
        # Year
        self.spin_year = QSpinBox()
        self.spin_year.setRange(2000, 2030)
        self.spin_year.setValue(2024)
        form_layout.addRow("Year *:", self.spin_year)
        
        # Max Capacity
        self.spin_capacity = QSpinBox()
        self.spin_capacity.setRange(10, 200)
        self.spin_capacity.setValue(60)
        form_layout.addRow("Max Capacity:", self.spin_capacity)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Add Class")
        btn_save.clicked.connect(self.save_class)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_subjects(self):
        query = "SELECT SubjectCode, SubjectName FROM subjects ORDER BY SubjectCode"
        rows = db.execute_query(query)
        if rows:
            for row in rows:
                self.combo_subject.addItem(f"{row['SubjectCode']} - {row['SubjectName']}", row['SubjectCode'])
    
    def load_lecturers(self):
        self.combo_lecturer.addItem("None", None)
        query = "SELECT LecturerID, LecturerFirstName, LecturerLastName FROM lecturers ORDER BY LecturerID"
        rows = db.execute_query(query)
        if rows:
            for row in rows:
                name = f"{row['LecturerFirstName']} {row['LecturerLastName']}"
                self.combo_lecturer.addItem(name, row['LecturerID'])
    
    def save_class(self):
        subject_code = self.combo_subject.currentData()
        lecturer_id = self.combo_lecturer.currentData()
        class_name = self.txt_class_name.text().strip()
        semester = self.combo_semester.currentText()
        year = self.spin_year.value()
        capacity = self.spin_capacity.value()
        
        if not subject_code:
            QMessageBox.warning(self, "Validation Error", "Subject is required!")
            return
        
        query = """
            INSERT INTO classes (SubjectCode, LecturerID, ClassName, Semester, Year, MaxCapacity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        result = db.execute_insert(query, (subject_code, lecturer_id, class_name, semester, year, capacity))
        
        if result:
            QMessageBox.information(self, "Success", "Class added successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add class!")

# ==================== ENROLLMENT DIALOG ====================
class EnrollmentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Enrollment")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Student (ComboBox with search)
        self.combo_student = QComboBox()
        self.combo_student.setEditable(True)
        self.combo_student.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.load_students()
        form_layout.addRow("Student *:", self.combo_student)
        
        # Class (ComboBox)
        self.combo_class = QComboBox()
        self.load_classes()
        form_layout.addRow("Class *:", self.combo_class)
        
        # Grade
        self.spin_grade = QDoubleSpinBox()
        self.spin_grade.setRange(0.0, 10.0)
        self.spin_grade.setSingleStep(0.1)
        self.spin_grade.setDecimals(2)
        form_layout.addRow("Grade (0-10):", self.spin_grade)
        
        # Grade Letter
        self.combo_letter = QComboBox()
        self.combo_letter.addItems(["", "A", "B", "C", "D", "F"])
        form_layout.addRow("Grade Letter:", self.combo_letter)
        
        # Note
        self.txt_note = QLineEdit()
        form_layout.addRow("Note:", self.txt_note)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Add Enrollment")
        btn_save.clicked.connect(self.save_enrollment)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_students(self):
        query = "SELECT StudentID, FirstName, LastName FROM students ORDER BY StudentID"
        rows = db.execute_query(query)
        if rows:
            for row in rows:
                name = f"{row['StudentID']} - {row['FirstName']} {row['LastName']}"
                self.combo_student.addItem(name, row['StudentID'])
    
    def load_classes(self):
        query = """
            SELECT c.ClassID, c.ClassName, c.Semester, c.Year, s.SubjectName
            FROM classes c
            JOIN subjects s ON c.SubjectCode = s.SubjectCode
            ORDER BY c.Year DESC, c.Semester
        """
        rows = db.execute_query(query)
        if rows:
            for row in rows:
                label = f"{row['ClassID']} - {row['SubjectName']} ({row['Semester']} {row['Year']})"
                self.combo_class.addItem(label, row['ClassID'])
    
    def save_enrollment(self):
        student_id = self.combo_student.currentData()
        class_id = self.combo_class.currentData()
        grade = self.spin_grade.value() if self.spin_grade.value() > 0 else None
        grade_letter = self.combo_letter.currentText() or None
        note = self.txt_note.text().strip() or None
        
        if not student_id or not class_id:
            QMessageBox.warning(self, "Validation Error", "Student and Class are required!")
            return
        
        # Validate grade range
        if grade is not None and (grade < 0 or grade > 10):
            QMessageBox.warning(self, "Validation Error", "Grade must be between 0 and 10!")
            return
        
        # Check if enrollment already exists
        check_query = "SELECT 1 FROM enrollments WHERE StudentID=%s AND ClassID=%s"
        exists = db.execute_query(check_query, (student_id, class_id))
        if exists:
            QMessageBox.warning(self, "Duplicate Entry", 
                "This student is already enrolled in this class!")
            return
        
        query = """
            INSERT INTO enrollments (StudentID, ClassID, Grade, GradeLetter, Note)
            VALUES (%s, %s, %s, %s, %s)
        """
        result = db.execute_insert(query, (student_id, class_id, grade, grade_letter, note))
        
        if result:
            QMessageBox.information(self, "Success", "Enrollment added successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add enrollment!")