# main_window.py - Complete Main Window với tất cả chức năng
"""
GIẢI THÍCH KIẾN TRÚC:

STRUCTURE:
├── Sidebar Navigation (6 pages)
│   ├── Students
│   ├── Subjects
│   ├── Lecturers
│   ├── Classes
│   ├── Enrollments
│   ├── Queries (4 required queries)
│   └── Dashboard (KPIs + Charts)
│
├── Each Page có:
│   ├── Search bar
│   ├── Action buttons (Add, Edit, Delete, Export CSV)
│   ├── Data table
│   └── Pagination controls
│
└── Common Features:
    ├── Validation trước khi save
    ├── Confirmation trước khi delete
    ├── Error handling với user-friendly messages
    ├── Auto-refresh sau CRUD operations
    └── Export to CSV functionality

KEY IMPROVEMENTS so với code gốc:
1. Separation of Concerns: UI logic tách khỏi business logic
2. Reusable Components: BaseTablePage class
3. Full CRUD cho tất cả entities
4. 4 query pages theo yêu cầu
5. Dashboard với KPIs và charts
6. Better error handling
7. Consistent UI/UX
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import sys
import csv
from datetime import datetime

# Import models và dialogs
from models import StudentModel, SubjectModel, LecturerModel, ClassModel, EnrollmentModel
from query_models import QueryModels
from dialogs_complete import SubjectDialog, LecturerDialog, ClassDialog, EnrollmentDialog
from studentdialog_logic import StudentDialog
from validators import ValidationError

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# BASE TABLE PAGE - Reusable component
# ============================================================

class BaseTablePage(QWidget):
    """
    Base class cho tất cả table pages
    
    Provides common functionality:
    - Table setup
    - Search
    - Export CSV
    - Refresh
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup basic UI structure"""
        layout = QVBoxLayout()
        
        # Top bar: Search + Actions
        top_bar = QHBoxLayout()
        
        # Search
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search...")
        self.txt_search.setMaximumWidth(400)
        self.txt_search.textChanged.connect(self.on_search)
        top_bar.addWidget(self.txt_search)
        
        top_bar.addStretch()
        
        # Action buttons
        self.btn_add = QPushButton("Add")
        self.btn_add.setStyleSheet(self.get_button_style("#4CAF50"))
        self.btn_add.clicked.connect(self.on_add)
        top_bar.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setStyleSheet(self.get_button_style("#2196F3"))
        self.btn_edit.clicked.connect(self.on_edit)
        top_bar.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setStyleSheet(self.get_button_style("#f44336"))
        self.btn_delete.clicked.connect(self.on_delete)
        top_bar.addWidget(self.btn_delete)
        
        self.btn_export = QPushButton("Export CSV")
        self.btn_export.setStyleSheet(self.get_button_style("#FF9800"))
        self.btn_export.clicked.connect(self.on_export)
        top_bar.addWidget(self.btn_export)
        
        layout.addLayout(top_bar)
        
        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #34495e;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.table)
        
        # Status bar
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.lbl_status)
        
        self.setLayout(layout)
    
    def get_button_style(self, color):
        """Get consistent button styling"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """
    
    def load_data(self):
        """Override in subclass"""
        pass
    
    def on_search(self):
        """Override in subclass"""
        pass
    
    def on_add(self):
        """Override in subclass"""
        pass
    
    def on_edit(self):
        """Override in subclass"""
        pass
    
    def on_delete(self):
        """Override in subclass"""
        pass
    
    def on_export(self):
        """Export table to CSV"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No data to export!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Headers
                headers = []
                for col in range(self.table.columnCount()):
                    header = self.table.horizontalHeaderItem(col)
                    headers.append(header.text() if header else f"Column{col}")
                writer.writerow(headers)
                
                # Data
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Exported {self.table.rowCount()} rows to:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{e}")
    
    def get_selected_row_data(self, column):
        """Get data from selected row at specific column"""
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.table.item(row, column)
        return item.text() if item else None
    
    def refresh_table(self):
        """Refresh table data"""
        self.load_data()


# ============================================================
# STUDENTS PAGE
# ============================================================

class StudentsPage(BaseTablePage):
    """Students management page"""
    
    def __init__(self):
        super().__init__()
        self.setup_table_columns()
        self.load_data()
    
    def setup_table_columns(self):
        """Setup table columns"""
        columns = ["ID", "First Name", "Last Name", "DOB", "Gender", 
                  "Email", "Phone", "Enrollment Year", "Major"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
    
    def load_data(self, search_term=""):
        """Load students data"""
        try:
            if search_term:
                students = StudentModel.search(search_term)
            else:
                students = StudentModel.list(limit=500)
            
            self.table.setRowCount(len(students))
            
            for row_idx, student in enumerate(students):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(student['StudentID'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(student['FirstName']))
                self.table.setItem(row_idx, 2, QTableWidgetItem(student['LastName']))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(student['DOB'])))
                self.table.setItem(row_idx, 4, QTableWidgetItem(student['Gender']))
                self.table.setItem(row_idx, 5, QTableWidgetItem(student.get('Email', '')))
                self.table.setItem(row_idx, 6, QTableWidgetItem(student.get('Phone', '')))
                self.table.setItem(row_idx, 7, QTableWidgetItem(str(student['EnrollmentYear'])))
                self.table.setItem(row_idx, 8, QTableWidgetItem(student.get('Major', '')))
            
            self.lbl_status.setText(f"Total students: {len(students)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load students: {e}")
    
    def on_search(self):
        """Search students"""
        self.load_data(self.txt_search.text())
    
    def on_add(self):
        """Add new student"""
        dialog = StudentDialog(edit_mode=False)
        if dialog.exec():
            self.refresh_table()
    
    def on_edit(self):
        """Edit selected student"""
        student_id = self.get_selected_row_data(0)
        if not student_id:
            QMessageBox.warning(self, "Warning", "Please select a student to edit!")
            return
        
        dialog = StudentDialog(edit_mode=True, student_id=int(student_id))
        if dialog.exec():
            self.refresh_table()
    
    def on_delete(self):
        """Delete selected student"""
        student_id = self.get_selected_row_data(0)
        if not student_id:
            QMessageBox.warning(self, "Warning", "Please select a student to delete!")
            return
        
        name = f"{self.get_selected_row_data(1)} {self.get_selected_row_data(2)}"
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}' (ID: {student_id})?\n\nThis will also delete all their enrollments!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                StudentModel.delete(int(student_id))
                QMessageBox.information(self, "Success", "Student deleted successfully!")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {e}")


# ============================================================
# SUBJECTS PAGE
# ============================================================

class SubjectsPage(BaseTablePage):
    """Subjects management page"""
    
    def __init__(self):
        super().__init__()
        self.setup_table_columns()
        self.load_data()
    
    def setup_table_columns(self):
        """Setup table columns"""
        columns = ["Subject Code", "Subject Name", "Credits"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
    
    def load_data(self):
        """Load subjects"""
        try:
            subjects = SubjectModel.list()
            self.table.setRowCount(len(subjects))
            
            for row_idx, subject in enumerate(subjects):
                self.table.setItem(row_idx, 0, QTableWidgetItem(subject['SubjectCode']))
                self.table.setItem(row_idx, 1, QTableWidgetItem(subject['SubjectName']))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(subject['Credits'])))
            
            self.lbl_status.setText(f"Total subjects: {len(subjects)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load subjects: {e}")
    
    def on_search(self):
        """Search functionality can be added later"""
        pass
    
    def on_add(self):
        """Add new subject"""
        dialog = SubjectDialog()
        if dialog.exec():
            self.refresh_table()
    
    def on_edit(self):
        """Edit selected subject"""
        code = self.get_selected_row_data(0)
        if not code:
            QMessageBox.warning(self, "Warning", "Please select a subject to edit!")
            return
        
        dialog = SubjectDialog(edit_mode=True, subject_code=code)
        if dialog.exec():
            self.refresh_table()
    
    def on_delete(self):
        """Delete selected subject"""
        code = self.get_selected_row_data(0)
        if not code:
            QMessageBox.warning(self, "Warning", "Please select a subject to delete!")
            return
        
        name = self.get_selected_row_data(1)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}' ({code})?\n\nThis will fail if classes exist for this subject!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                SubjectModel.delete(code)
                QMessageBox.information(self, "Success", "Subject deleted successfully!")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {e}\n\nProbably classes still exist for this subject.")


# ============================================================
# LECTURERS PAGE
# ============================================================

class LecturersPage(BaseTablePage):
    """Lecturers management page"""
    
    def __init__(self):
        super().__init__()
        self.setup_table_columns()
        self.load_data()
    
    def setup_table_columns(self):
        """Setup table columns"""
        columns = ["ID", "First Name", "Last Name", "Email", "Office"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
    
    def load_data(self):
        """Load lecturers"""
        try:
            lecturers = LecturerModel.list()
            self.table.setRowCount(len(lecturers))
            
            for row_idx, lecturer in enumerate(lecturers):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(lecturer['LecturerID'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(lecturer['LecturerFirstName']))
                self.table.setItem(row_idx, 2, QTableWidgetItem(lecturer['LecturerLastName']))
                self.table.setItem(row_idx, 3, QTableWidgetItem(lecturer.get('LecturerEmail', '')))
                self.table.setItem(row_idx, 4, QTableWidgetItem(lecturer.get('Office', '')))
            
            self.lbl_status.setText(f"Total lecturers: {len(lecturers)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load lecturers: {e}")
    
    def on_search(self):
        pass
    
    def on_add(self):
        """Add new lecturer"""
        dialog = LecturerDialog()
        if dialog.exec():
            self.refresh_table()
    
    def on_edit(self):
        """Edit selected lecturer"""
        lecturer_id = self.get_selected_row_data(0)
        if not lecturer_id:
            QMessageBox.warning(self, "Warning", "Please select a lecturer to edit!")
            return
        
        dialog = LecturerDialog(edit_mode=True, lecturer_id=int(lecturer_id))
        if dialog.exec():
            self.refresh_table()
    
    def on_delete(self):
        """Delete selected lecturer"""
        lecturer_id = self.get_selected_row_data(0)
        if not lecturer_id:
            QMessageBox.warning(self, "Warning", "Please select a lecturer to delete!")
            return
        
        name = f"{self.get_selected_row_data(1)} {self.get_selected_row_data(2)}"
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}'?\n\nClasses taught by this lecturer will have NULL lecturer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                LecturerModel.delete(int(lecturer_id))
                QMessageBox.information(self, "Success", "Lecturer deleted successfully!")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {e}")


# ============================================================
# CLASSES PAGE
# ============================================================

class ClassesPage(BaseTablePage):
    """Classes management page"""
    
    def __init__(self):
        super().__init__()
        self.setup_table_columns()
        self.load_data()
    
    def setup_table_columns(self):
        """Setup table columns"""
        columns = ["Class ID", "Subject", "Lecturer", "Class Name", 
                  "Semester", "Year", "Capacity", "Enrolled"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
    
    def load_data(self):
        """Load classes"""
        try:
            classes = ClassModel.list()
            self.table.setRowCount(len(classes))
            
            for row_idx, cls in enumerate(classes):
                lecturer_name = ""
                if cls.get('LecturerFirstName'):
                    lecturer_name = f"{cls['LecturerFirstName']} {cls['LecturerLastName']}"
                
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(cls['ClassID'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(cls.get('SubjectName', '')))
                self.table.setItem(row_idx, 2, QTableWidgetItem(lecturer_name))
                self.table.setItem(row_idx, 3, QTableWidgetItem(cls.get('ClassName', '')))
                self.table.setItem(row_idx, 4, QTableWidgetItem(cls['Semester']))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(cls['Year'])))
                self.table.setItem(row_idx, 6, QTableWidgetItem(str(cls.get('MaxCapacity', ''))))
                self.table.setItem(row_idx, 7, QTableWidgetItem(str(cls.get('EnrolledCount', 0))))
            
            self.lbl_status.setText(f"Total classes: {len(classes)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load classes: {e}")
    
    def on_search(self):
        pass
    
    def on_add(self):
        """Add new class"""
        dialog = ClassDialog()
        if dialog.exec():
            self.refresh_table()
    
    def on_edit(self):
        """Edit selected class"""
        class_id = self.get_selected_row_data(0)
        if not class_id:
            QMessageBox.warning(self, "Warning", "Please select a class to edit!")
            return
        
        dialog = ClassDialog(edit_mode=True, class_id=int(class_id))
        if dialog.exec():
            self.refresh_table()
    
    def on_delete(self):
        """Delete selected class"""
        class_id = self.get_selected_row_data(0)
        if not class_id:
            QMessageBox.warning(self, "Warning", "Please select a class to delete!")
            return
        
        subject = self.get_selected_row_data(1)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete class '{subject}' (ID: {class_id})?\n\nThis will also delete all enrollments!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                ClassModel.delete(int(class_id))
                QMessageBox.information(self, "Success", "Class deleted successfully!")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {e}")
# main_window_part2.py - Continuation: Enrollments, Queries, Dashboard
"""
Phần 2 của Main Window:
- EnrollmentsPage
- 4 Query Pages (theo yêu cầu)
- Dashboard Page với KPIs và Charts
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from main_win import BaseTablePage
from models import EnrollmentModel
from query_models import QueryModels
from dialogs_complete import EnrollmentDialog


# ============================================================
# ENROLLMENTS PAGE
# ============================================================

class EnrollmentsPage(BaseTablePage):
    """Enrollments management page"""
    
    def __init__(self):
        super().__init__()
        self.setup_table_columns()
        self.load_data()
    
    def setup_table_columns(self):
        """Setup table columns"""
        columns = ["Student ID", "Student Name", "Class ID", "Subject", 
                  "Semester", "Year", "Grade", "Grade Letter"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
    
    def load_data(self):
        """Load all enrollments"""
        try:
            # Get comprehensive enrollment data using query
            enrollments = QueryModels.query_complete_enrollment_info()
            
            self.table.setRowCount(len(enrollments))
            
            for row_idx, enr in enumerate(enrollments):
                student_name = f"{enr['StudentFirstName']} {enr['StudentLastName']}"
                
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(enr['StudentID'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(student_name))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(enr['ClassID'])))
                self.table.setItem(row_idx, 3, QTableWidgetItem(enr['SubjectName']))
                self.table.setItem(row_idx, 4, QTableWidgetItem(enr['Semester']))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(enr['Year'])))
                self.table.setItem(row_idx, 6, QTableWidgetItem(str(enr.get('Grade', ''))))
                self.table.setItem(row_idx, 7, QTableWidgetItem(enr.get('GradeLetter', '')))
            
            self.lbl_status.setText(f"Total enrollments: {len(enrollments)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load enrollments: {e}")
    
    def on_search(self):
        pass
    
    def on_add(self):
        """Add new enrollment"""
        dialog = EnrollmentDialog()
        if dialog.exec():
            self.refresh_table()
    
    def on_edit(self):
        """Edit selected enrollment"""
        student_id = self.get_selected_row_data(0)
        class_id = self.get_selected_row_data(2)
        
        if not student_id or not class_id:
            QMessageBox.warning(self, "Warning", "Please select an enrollment to edit!")
            return
        
        dialog = EnrollmentDialog(edit_mode=True, 
                                 student_id=int(student_id), 
                                 class_id=int(class_id))
        if dialog.exec():
            self.refresh_table()
    
    def on_delete(self):
        """Delete selected enrollment"""
        student_id = self.get_selected_row_data(0)
        class_id = self.get_selected_row_data(2)
        
        if not student_id or not class_id:
            QMessageBox.warning(self, "Warning", "Please select an enrollment to delete!")
            return
        
        student_name = self.get_selected_row_data(1)
        subject = self.get_selected_row_data(3)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete enrollment:\n{student_name} -> {subject}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                EnrollmentModel.delete(int(student_id), int(class_id))
                QMessageBox.information(self, "Success", "Enrollment deleted successfully!")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {e}")


# ============================================================
# QUERY PAGES - 4 required queries
# ============================================================

class Query1Page(QWidget):
    """
    Query 1: INNER JOIN - Student name and grade per subject
    
    YÊU CẦU:
    - INNER JOIN students, enrollments, classes, subjects
    - Show student name, subject, grade
    - Export CSV
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Query 1: Student Grades by Subject (INNER JOIN)")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Shows students who have grades. Uses INNER JOIN so only enrolled students appear.")
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Subject:"))
        
        self.combo_subject = QComboBox()
        self.combo_subject.addItem("All Subjects", None)
        # Load subjects will be done in load_data
        self.combo_subject.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.combo_subject)
        
        filter_layout.addStretch()
        
        btn_export = QPushButton("Export CSV")
        btn_export.setStyleSheet(self.get_button_style("#FF9800"))
        btn_export.clicked.connect(self.export_csv)
        filter_layout.addWidget(btn_export)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
        """)
        layout.addWidget(self.table)
        
        # Status
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.lbl_status)
        
        self.setLayout(layout)
    
    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """
    
    def load_data(self):
        """Load query results"""
        try:
            # Load subjects into combo if empty
            if self.combo_subject.count() == 1:
                from models import SubjectModel
                subjects = SubjectModel.list()
                for subject in subjects:
                    self.combo_subject.addItem(
                        f"{subject['SubjectCode']} - {subject['SubjectName']}", 
                        subject['SubjectCode']
                    )
            
            # Get filter
            subject_code = self.combo_subject.currentData()
            
            # Run query
            results = QueryModels.query_student_grades_by_subject(subject_code)
            
            # Setup table
            if results:
                columns = list(results[0].keys())
                self.table.setColumnCount(len(columns))
                self.table.setHorizontalHeaderLabels(columns)
                self.table.setRowCount(len(results))
                
                for row_idx, row_data in enumerate(results):
                    for col_idx, (key, value) in enumerate(row_data.items()):
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value) if value else ''))
            
            self.lbl_status.setText(f"Found {len(results)} records")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Query failed: {e}")
    
    def export_csv(self):
        """Export to CSV"""
        from query_models import export_query_to_csv
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Query 1",
            "query1_student_grades.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            subject_code = self.combo_subject.currentData()
            results = QueryModels.query_student_grades_by_subject(subject_code)
            if export_query_to_csv(results, filename):
                QMessageBox.information(self, "Success", f"Exported to {filename}")


class Query2Page(QWidget):
    """
    Query 2: LEFT JOIN - All students with/without grades
    
    YÊU CẦU:
    - LEFT JOIN để show all students
    - Including students without enrollments
    - Export CSV
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Query 2: All Students Including Without Grades (LEFT JOIN)")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Shows ALL students. LEFT JOIN ensures students without enrollments are included (with NULL grades).")
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Export button
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        
        btn_export = QPushButton("Export CSV")
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        btn_export.clicked.connect(self.export_csv)
        top_bar.addWidget(btn_export)
        
        layout.addLayout(top_bar)
        
        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
        """)
        layout.addWidget(self.table)
        
        # Status
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.lbl_status)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load query results"""
        try:
            results = QueryModels.query_all_students_with_grades()
            
            if results:
                columns = list(results[0].keys())
                self.table.setColumnCount(len(columns))
                self.table.setHorizontalHeaderLabels(columns)
                self.table.setRowCount(len(results))
                
                for row_idx, row_data in enumerate(results):
                    for col_idx, (key, value) in enumerate(row_data.items()):
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value) if value else ''))
            
            self.lbl_status.setText(f"Found {len(results)} records")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Query failed: {e}")
    
    def export_csv(self):
        """Export to CSV"""
        from query_models import export_query_to_csv
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Query 2",
            "query2_all_students.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            results = QueryModels.query_all_students_with_grades()
            if export_query_to_csv(results, filename):
                QMessageBox.information(self, "Success", f"Exported to {filename}")


class Query3Page(QWidget):
    """
    Query 3: Multi-table JOIN - Student-Subject-Grade-Lecturer
    
    YÊU CẦU:
    - Join 3+ tables (5 tables: students, enrollments, classes, subjects, lecturers)
    - Show complete enrollment information
    - Multiple filters
    - Export CSV
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Query 3: Complete Enrollment Info (Multi-table JOIN - 5 tables)")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Joins: Students ⟷ Enrollments ⟷ Classes ⟷ Subjects ⟷ Lecturers")
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Semester:"))
        self.combo_semester = QComboBox()
        self.combo_semester.addItems(["All", "S1", "S2", "S3", "SUMMER"])
        self.combo_semester.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.combo_semester)
        
        filter_layout.addWidget(QLabel("Year:"))
        self.spin_year = QSpinBox()
        self.spin_year.setRange(2020, 2030)
        self.spin_year.setValue(2024)
        self.spin_year.setSpecialValueText("All")
        self.spin_year.valueChanged.connect(self.load_data)
        filter_layout.addWidget(self.spin_year)
        
        filter_layout.addStretch()
        
        btn_export = QPushButton("Export CSV")
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        btn_export.clicked.connect(self.export_csv)
        filter_layout.addWidget(btn_export)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
        """)
        layout.addWidget(self.table)
        
        # Status
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.lbl_status)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load query results"""
        try:
            semester = None if self.combo_semester.currentText() == "All" else self.combo_semester.currentText()
            year = None if self.spin_year.value() == 2020 else self.spin_year.value()
            
            results = QueryModels.query_complete_enrollment_info(semester=semester, year=year)
            
            if results:
                columns = list(results[0].keys())
                self.table.setColumnCount(len(columns))
                self.table.setHorizontalHeaderLabels(columns)
                self.table.setRowCount(len(results))
                
                for row_idx, row_data in enumerate(results):
                    for col_idx, (key, value) in enumerate(row_data.items()):
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value) if value else ''))
            
            self.lbl_status.setText(f"Found {len(results)} records")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Query failed: {e}")
    
    def export_csv(self):
        """Export to CSV"""
        from query_models import export_query_to_csv
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Query 3",
            "query3_complete_enrollment.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            semester = None if self.combo_semester.currentText() == "All" else self.combo_semester.currentText()
            year = None if self.spin_year.value() == 2020 else self.spin_year.value()
            results = QueryModels.query_complete_enrollment_info(semester=semester, year=year)
            if export_query_to_csv(results, filename):
                QMessageBox.information(self, "Success", f"Exported to {filename}")


class Query4Page(QWidget):
    """
    Query 4: Students Above Global Average
    
    YÊU CẦU:
    - Calculate global average grade
    - Find students với average > global average
    - Show difference from average
    - Export CSV
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Query 4: Students Above Global Average")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Shows students whose average grade exceeds the overall average of all students.")
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Filter + Export
        top_bar = QHBoxLayout()
        
        top_bar.addWidget(QLabel("Min Classes:"))
        self.spin_min_classes = QSpinBox()
        self.spin_min_classes.setRange(1, 20)
        self.spin_min_classes.setValue(3)
        self.spin_min_classes.valueChanged.connect(self.load_data)
        top_bar.addWidget(self.spin_min_classes)
        
        top_bar.addStretch()
        
        btn_export = QPushButton("Export CSV")
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        btn_export.clicked.connect(self.export_csv)
        top_bar.addWidget(btn_export)
        
        layout.addLayout(top_bar)
        
        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
        """)
        layout.addWidget(self.table)
        
        # Status
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.lbl_status)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load query results"""
        try:
            min_classes = self.spin_min_classes.value()
            results = QueryModels.query_students_above_average(min_classes)
            
            if results:
                columns = list(results[0].keys())
                self.table.setColumnCount(len(columns))
                self.table.setHorizontalHeaderLabels(columns)
                self.table.setRowCount(len(results))
                
                for row_idx, row_data in enumerate(results):
                    for col_idx, (key, value) in enumerate(row_data.items()):
                        item = QTableWidgetItem(str(value) if value else '')
                        
                        # Highlight positive differences
                        if key == 'DifferenceFromAvg' and value and float(value) > 0:
                            item.setForeground(Qt.GlobalColor.darkGreen)
                        
                        self.table.setItem(row_idx, col_idx, item)
            
            global_avg = results[0]['GlobalAvg'] if results else 0
            self.lbl_status.setText(f"Found {len(results)} students above global average ({global_avg})")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Query failed: {e}")
    
    def export_csv(self):
        """Export to CSV"""
        from query_models import export_query_to_csv
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Query 4",
            "query4_above_average.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            min_classes = self.spin_min_classes.value()
            results = QueryModels.query_students_above_average(min_classes)
            if export_query_to_csv(results, filename):
                QMessageBox.information(self, "Success", f"Exported to {filename}")


# ============================================================
# DASHBOARD PAGE
# ============================================================

class DashboardPage(QWidget):
    """
    Dashboard với KPIs và Charts
    """

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("📊 Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title)

        # KPI Cards
        kpi_layout = QHBoxLayout()
        self.kpi_students = self.create_kpi_card("Students", "0", "#3498db")
        self.kpi_subjects = self.create_kpi_card("Subjects", "0", "#2ecc71")
        self.kpi_classes = self.create_kpi_card("Classes", "0", "#9b59b6")
        self.kpi_avg_grade = self.create_kpi_card("Avg Grade", "0.00", "#e74c3c")
        self.kpi_pass_rate = self.create_kpi_card("Pass Rate", "0%", "#f39c12")

        kpi_layout.addWidget(self.kpi_students)
        kpi_layout.addWidget(self.kpi_subjects)
        kpi_layout.addWidget(self.kpi_classes)
        kpi_layout.addWidget(self.kpi_avg_grade)
        kpi_layout.addWidget(self.kpi_pass_rate)
        main_layout.addLayout(kpi_layout)

        # Content layout
        content_layout = QHBoxLayout()

        # Chart area
        chart_container = QVBoxLayout()
        chart_label = QLabel("Grade Distribution")
        chart_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        chart_container.addWidget(chart_label)

        self.chart_view = QWidget()
        self.chart_view.setLayout(QVBoxLayout())
        chart_container.addWidget(self.chart_view)

        content_layout.addLayout(chart_container)

        # Top student table
        top_container = QVBoxLayout()
        top_label = QLabel("Top 10 Students")
        top_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        top_container.addWidget(top_label)

        self.table_top_students = QTableWidget()
        self.table_top_students.setColumnCount(4)
        self.table_top_students.setHorizontalHeaderLabels(["Rank", "Name", "Avg Grade", "Classes"])
        self.table_top_students.horizontalHeader().setStretchLastSection(True)
        top_container.addWidget(self.table_top_students)

        content_layout.addLayout(top_container)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def create_kpi_card(self, label, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        layout = QVBoxLayout()

        lbl_label = QLabel(label)
        lbl_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        layout.addWidget(lbl_label)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        lbl_value.setObjectName("value")
        layout.addWidget(lbl_value)

        card.setLayout(layout)
        return card

    def load_data(self):
        """Load dashboard data"""
        try:
            kpis = QueryModels.get_dashboard_kpis()

            self.update_kpi(self.kpi_students, str(kpis.get("total_students", 0)))
            self.update_kpi(self.kpi_subjects, str(kpis.get("total_subjects", 0)))
            self.update_kpi(self.kpi_classes, str(kpis.get("total_classes", 0)))
            self.update_kpi(self.kpi_avg_grade, str(kpis.get("avg_grade", 0)))
            self.update_kpi(self.kpi_pass_rate, f"{kpis.get('pass_rate', 0)}%")

            # Grade chart
            grade_data = QueryModels.get_grade_distribution()
            self.load_grade_distribution_chart(grade_data)

            # Top students
            self.load_top_students()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dashboard: {e}")

    def update_kpi(self, card, value):
        lbl_value = card.findChild(QLabel, "value")
        if lbl_value:
            lbl_value.setText(value)

    def load_grade_distribution_chart(self, data):
        try:
            layout = self.chart_view.layout()

            # Clear old charts
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Chart data
            counts = [row["Count"] for row in data]
            categories = [row["GradeRange"] for row in data]
            x_positions = list(range(len(categories)))

            # PyQtGraph plot
            plot = pg.PlotWidget()
            plot.showGrid(x=True, y=True)
            plot.setTitle("Grade Distribution")
            plot.setLabel("left", "Count")
            plot.setLabel("bottom", "Grade Range")

            bar_item = pg.BarGraphItem(
                x=x_positions,
                height=counts,
                width=0.6,
                brush="skyblue"
            )
            plot.addItem(bar_item)

            # X-axis labels
            axis_x = plot.getAxis("bottom")
            axis_x.setTicks([list(zip(x_positions, categories))])

            layout.addWidget(plot)

        except Exception as e:
            print(f"Chart error: {e}")

    def load_top_students(self):
        try:
            top_students = QueryModels.query_top_students(limit=10)
            self.table_top_students.setRowCount(len(top_students))

            for row_idx, student in enumerate(top_students):
                self.table_top_students.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))

                name = f"{student['FirstName']} {student['LastName']}"
                self.table_top_students.setItem(row_idx, 1, QTableWidgetItem(name))

                self.table_top_students.setItem(row_idx, 2, QTableWidgetItem(str(student["AvgGrade"])))
                self.table_top_students.setItem(row_idx, 3, QTableWidgetItem(str(student["TotalClasses"])))

        except Exception as e:
            print(f"Error loading top students: {e}")
