# dialogs_complete.py - Complete CRUD Dialogs cho tất cả entities
"""
GIẢI THÍCH:
- Dialogs cho: Subject, Lecturer, Class, Enrollment
- Support cả Add và Edit mode
- Full validation using validators module
- Load related data từ database (dropdown options)
- Clean error handling và user feedback
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from models import SubjectModel, LecturerModel, ClassModel, EnrollmentModel, StudentModel
from validators import ValidationError, Validators
import logging

logger = logging.getLogger(__name__)


# ============================================================
# SUBJECT DIALOG
# ============================================================

class SubjectDialog(QDialog):
    """
    Dialog for adding/editing subjects
    
    Fields:
    - Subject Code (PK, required)
    - Subject Name (required)
    - Credits (1-10)
    """
    
    def __init__(self, parent=None, edit_mode=False, subject_code=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.subject_code = subject_code
        
        self.setWindowTitle("Edit Subject" if edit_mode else "Add New Subject")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        self.setup_ui()
        
        if edit_mode and subject_code:
            self.load_subject_data()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Edit Subject" if self.edit_mode else "Add New Subject")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Subject Code
        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("e.g., CS101, MATH201")
        if self.edit_mode:
            self.txt_code.setReadOnly(True)
            self.txt_code.setStyleSheet("background-color: #f0f0f0;")
        form_layout.addRow("Subject Code *:", self.txt_code)
        
        # Subject Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g., Introduction to Programming")
        form_layout.addRow("Subject Name *:", self.txt_name)
        
        # Credits
        self.spin_credits = QSpinBox()
        self.spin_credits.setRange(1, 10)
        self.spin_credits.setValue(3)
        self.spin_credits.setSuffix(" credits")
        form_layout.addRow("Credits *:", self.spin_credits)
        
        layout.addLayout(form_layout)
        
        # Info label
        info = QLabel("* Required fields")
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_save = QPushButton("Update Subject" if self.edit_mode else "Add Subject")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.save_subject)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_subject_data(self):
        """Load existing subject data for editing"""
        try:
            subject = SubjectModel.get_by_code(self.subject_code)
            if subject:
                self.txt_code.setText(subject['SubjectCode'])
                self.txt_name.setText(subject['SubjectName'])
                self.spin_credits.setValue(subject['Credits'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load subject: {e}")
    
    def save_subject(self):
        """Save or update subject"""
        try:
            data = {
                'code': self.txt_code.text(),
                'name': self.txt_name.text(),
                'credits': self.spin_credits.value()
            }
            
            if self.edit_mode:
                SubjectModel.update(self.subject_code, data)
                QMessageBox.information(self, "Success", "Subject updated successfully!")
            else:
                SubjectModel.create(data)
                QMessageBox.information(self, "Success", "Subject added successfully!")
            
            self.accept()
            
        except ValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")


# ============================================================
# LECTURER DIALOG
# ============================================================

class LecturerDialog(QDialog):
    """
    Dialog for adding/editing lecturers
    
    Fields:
    - First Name (required)
    - Last Name (required)
    - Email (optional, unique)
    - Office (optional)
    """
    
    def __init__(self, parent=None, edit_mode=False, lecturer_id=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.lecturer_id = lecturer_id
        
        self.setWindowTitle("Edit Lecturer" if edit_mode else "Add New Lecturer")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        self.setup_ui()
        
        if edit_mode and lecturer_id:
            self.load_lecturer_data()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Edit Lecturer" if self.edit_mode else "Add New Lecturer")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        
        self.txt_first_name = QLineEdit()
        self.txt_first_name.setPlaceholderText("John")
        form_layout.addRow("First Name *:", self.txt_first_name)
        
        self.txt_last_name = QLineEdit()
        self.txt_last_name.setPlaceholderText("Smith")
        form_layout.addRow("Last Name *:", self.txt_last_name)
        
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("lecturer@example.com")
        form_layout.addRow("Email:", self.txt_email)
        
        self.txt_office = QLineEdit()
        self.txt_office.setPlaceholderText("e.g., B201")
        form_layout.addRow("Office:", self.txt_office)
        
        layout.addLayout(form_layout)
        
        # Info
        info = QLabel("* Required fields")
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_save = QPushButton("Update Lecturer" if self.edit_mode else "Add Lecturer")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        btn_save.clicked.connect(self.save_lecturer)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_lecturer_data(self):
        """Load existing lecturer data"""
        try:
            lecturer = LecturerModel.get_by_id(self.lecturer_id)
            if lecturer:
                self.txt_first_name.setText(lecturer['LecturerFirstName'])
                self.txt_last_name.setText(lecturer['LecturerLastName'])
                self.txt_email.setText(lecturer.get('LecturerEmail', ''))
                self.txt_office.setText(lecturer.get('Office', ''))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load lecturer: {e}")
    
    def save_lecturer(self):
        """Save or update lecturer"""
        try:
            data = {
                'first_name': self.txt_first_name.text(),
                'last_name': self.txt_last_name.text(),
                'email': self.txt_email.text(),
                'office': self.txt_office.text()
            }
            
            if self.edit_mode:
                LecturerModel.update(self.lecturer_id, data)
                QMessageBox.information(self, "Success", "Lecturer updated successfully!")
            else:
                LecturerModel.create(data)
                QMessageBox.information(self, "Success", "Lecturer added successfully!")
            
            self.accept()
            
        except ValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")


# ============================================================
# CLASS DIALOG
# ============================================================

class ClassDialog(QDialog):
    """
    Dialog for adding/editing classes
    
    Fields:
    - Subject (dropdown, required)
    - Lecturer (dropdown, optional)
    - Class Name (optional)
    - Semester (dropdown, required)
    - Year (spinner, required)
    - Max Capacity (spinner)
    """
    
    def __init__(self, parent=None, edit_mode=False, class_id=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.class_id = class_id
        
        self.setWindowTitle("Edit Class" if edit_mode else "Add New Class")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.load_dropdowns()
        
        if edit_mode and class_id:
            self.load_class_data()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Edit Class" if self.edit_mode else "Add New Class")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        
        # Subject (ComboBox)
        self.combo_subject = QComboBox()
        form_layout.addRow("Subject *:", self.combo_subject)
        
        # Lecturer (ComboBox)
        self.combo_lecturer = QComboBox()
        form_layout.addRow("Lecturer:", self.combo_lecturer)
        
        # Class Name
        self.txt_class_name = QLineEdit()
        self.txt_class_name.setPlaceholderText("e.g., Group 1, Section A")
        form_layout.addRow("Class Name:", self.txt_class_name)
        
        # Semester
        self.combo_semester = QComboBox()
        self.combo_semester.addItems(["S1", "S2", "S3", "SUMMER"])
        form_layout.addRow("Semester *:", self.combo_semester)
        
        # Year
        self.spin_year = QSpinBox()
        self.spin_year.setRange(2000, 2035)
        self.spin_year.setValue(2024)
        form_layout.addRow("Year *:", self.spin_year)
        
        # Max Capacity
        self.spin_capacity = QSpinBox()
        self.spin_capacity.setRange(10, 200)
        self.spin_capacity.setValue(60)
        self.spin_capacity.setSuffix(" students")
        form_layout.addRow("Max Capacity:", self.spin_capacity)
        
        layout.addLayout(form_layout)
        
        # Info
        info = QLabel("* Required fields")
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_save = QPushButton("Update Class" if self.edit_mode else "Add Class")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        btn_save.clicked.connect(self.save_class)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_dropdowns(self):
        """Load subjects and lecturers into dropdowns"""
        try:
            # Load subjects
            subjects = SubjectModel.list()
            for subject in subjects:
                self.combo_subject.addItem(
                    f"{subject['SubjectCode']} - {subject['SubjectName']}", 
                    subject['SubjectCode']
                )
            
            # Load lecturers
            self.combo_lecturer.addItem("None", None)
            lecturers = LecturerModel.list()
            for lecturer in lecturers:
                name = f"{lecturer['LecturerFirstName']} {lecturer['LecturerLastName']}"
                self.combo_lecturer.addItem(name, lecturer['LecturerID'])
                
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load dropdown data: {e}")
    
    def load_class_data(self):
        """Load existing class data"""
        try:
            class_data = ClassModel.get_by_id(self.class_id)
            if class_data:
                # Set subject
                index = self.combo_subject.findData(class_data['SubjectCode'])
                if index >= 0:
                    self.combo_subject.setCurrentIndex(index)
                
                # Set lecturer
                if class_data.get('LecturerID'):
                    index = self.combo_lecturer.findData(class_data['LecturerID'])
                    if index >= 0:
                        self.combo_lecturer.setCurrentIndex(index)
                
                # Set other fields
                self.txt_class_name.setText(class_data.get('ClassName', ''))
                self.combo_semester.setCurrentText(class_data['Semester'])
                self.spin_year.setValue(class_data['Year'])
                self.spin_capacity.setValue(class_data.get('MaxCapacity', 60))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load class: {e}")
    
    def save_class(self):
        """Save or update class"""
        try:
            data = {
                'subject_code': self.combo_subject.currentData(),
                'lecturer_id': self.combo_lecturer.currentData(),
                'class_name': self.txt_class_name.text(),
                'semester': self.combo_semester.currentText(),
                'year': self.spin_year.value(),
                'max_capacity': self.spin_capacity.value()
            }
            
            if self.edit_mode:
                ClassModel.update(self.class_id, data)
                QMessageBox.information(self, "Success", "Class updated successfully!")
            else:
                ClassModel.create(data)
                QMessageBox.information(self, "Success", "Class added successfully!")
            
            self.accept()
            
        except ValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")


# ============================================================
# ENROLLMENT DIALOG
# ============================================================

class EnrollmentDialog(QDialog):
    """
    Dialog for adding/editing enrollments
    
    Fields:
    - Student (searchable dropdown, required)
    - Class (dropdown, required)
    - Grade (0-10, optional)
    - Grade Letter (A-F, optional)
    - Note (optional)
    """
    
    def __init__(self, parent=None, edit_mode=False, student_id=None, class_id=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.student_id = student_id
        self.class_id = class_id
        
        self.setWindowTitle("Edit Enrollment" if edit_mode else "Add New Enrollment")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.load_dropdowns()
        
        if edit_mode and student_id and class_id:
            self.load_enrollment_data()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Edit Enrollment" if self.edit_mode else "Add New Enrollment")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        
        # Student (ComboBox with search)
        self.combo_student = QComboBox()
        self.combo_student.setEditable(True)
        self.combo_student.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        if self.edit_mode:
            self.combo_student.setEnabled(False)
        form_layout.addRow("Student *:", self.combo_student)
        
        # Class (ComboBox)
        self.combo_class = QComboBox()
        if self.edit_mode:
            self.combo_class.setEnabled(False)
        form_layout.addRow("Class *:", self.combo_class)
        
        # Grade
        self.spin_grade = QDoubleSpinBox()
        self.spin_grade.setRange(0.0, 10.0)
        self.spin_grade.setSingleStep(0.1)
        self.spin_grade.setDecimals(2)
        self.spin_grade.setSpecialValueText("Not graded")
        form_layout.addRow("Grade (0-10):", self.spin_grade)
        
        # Grade Letter
        self.combo_letter = QComboBox()
        self.combo_letter.addItems(["", "A", "B", "C", "D", "F"])
        form_layout.addRow("Grade Letter:", self.combo_letter)
        
        # Note
        self.txt_note = QTextEdit()
        self.txt_note.setMaximumHeight(80)
        self.txt_note.setPlaceholderText("Optional notes...")
        form_layout.addRow("Note:", self.txt_note)
        
        layout.addLayout(form_layout)
        
        # Info
        info = QLabel("* Required fields. Cannot change Student/Class after creation.")
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_save = QPushButton("Update Enrollment" if self.edit_mode else "Add Enrollment")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        btn_save.clicked.connect(self.save_enrollment)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_dropdowns(self):
        """Load students and classes"""
        try:
            # Load students
            students = StudentModel.list(limit=500)
            for student in students:
                name = f"{student['StudentID']} - {student['FirstName']} {student['LastName']}"
                self.combo_student.addItem(name, student['StudentID'])
            
            # Load classes
            classes = ClassModel.list()
            for cls in classes:
                label = f"{cls['ClassID']} - {cls.get('SubjectName', '')} ({cls['Semester']} {cls['Year']})"
                self.combo_class.addItem(label, cls['ClassID'])
                
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load dropdown data: {e}")
    
    def load_enrollment_data(self):
        """Load existing enrollment data"""
        try:
            enrollments = EnrollmentModel.get_by_student(self.student_id)
            enrollment = next((e for e in enrollments if e['ClassID'] == self.class_id), None)
            
            if enrollment:
                # Set student
                index = self.combo_student.findData(self.student_id)
                if index >= 0:
                    self.combo_student.setCurrentIndex(index)
                
                # Set class
                index = self.combo_class.findData(self.class_id)
                if index >= 0:
                    self.combo_class.setCurrentIndex(index)
                
                # Set grade
                if enrollment.get('Grade'):
                    self.spin_grade.setValue(enrollment['Grade'])
                
                # Set grade letter
                if enrollment.get('GradeLetter'):
                    self.combo_letter.setCurrentText(enrollment['GradeLetter'])
                
                # Set note
                if enrollment.get('Note'):
                    self.txt_note.setPlainText(enrollment['Note'])
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load enrollment: {e}")
    
    def save_enrollment(self):
        """Save or update enrollment"""
        try:
            grade = self.spin_grade.value() if self.spin_grade.value() > 0 else None
            
            data = {
                'student_id': self.combo_student.currentData(),
                'class_id': self.combo_class.currentData(),
                'grade': grade,
                'grade_letter': self.combo_letter.currentText() or None,
                'note': self.txt_note.toPlainText().strip() or None
            }
            
            if self.edit_mode:
                EnrollmentModel.update(self.student_id, self.class_id, data)
                QMessageBox.information(self, "Success", "Enrollment updated successfully!")
            else:
                EnrollmentModel.create(data)
                QMessageBox.information(self, "Success", "Enrollment added successfully!")
            
            self.accept()
            
        except ValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Test dialogs
    print("Testing dialogs...")
    
    # Test Subject Dialog
    dialog = SubjectDialog()
    dialog.show()
    
    sys.exit(app.exec())