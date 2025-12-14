# main_app.py - Complete Student Management System
import sys
import csv
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon
from db_connection import db
from student_crud import StudentCRUDDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Connect to database
        if not db.connect():
            QMessageBox.critical(self, "Database Error", "Cannot connect to database!")
            sys.exit(1)
        
        self.init_ui()
        self.load_all_data()

    def init_ui(self):
        # Central widget with tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.create_students_tab()
        self.create_subjects_tab()
        self.create_lecturers_tab()
        self.create_classes_tab()
        self.create_enrollments_tab()
        self.create_queries_tab()
        self.create_dashboard_tab()

    # ==================== STUDENTS TAB ====================
    def create_students_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Search and buttons
        top_layout = QHBoxLayout()
        self.student_search = QLineEdit()
        self.student_search.setPlaceholderText("Search by name or email...")
        self.student_search.textChanged.connect(self.search_students)
        
        btn_add = QPushButton("Add Student")
        btn_add.clicked.connect(self.add_student)
        btn_edit = QPushButton("Edit")
        btn_edit.clicked.connect(self.edit_student)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_student)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_students)
        btn_export = QPushButton("Export CSV")
        btn_export.clicked.connect(lambda: self.export_table_to_csv(self.student_table, "students"))
        
        top_layout.addWidget(QLabel("Search:"))
        top_layout.addWidget(self.student_search)
        top_layout.addWidget(btn_add)
        top_layout.addWidget(btn_edit)
        top_layout.addWidget(btn_delete)
        top_layout.addWidget(btn_refresh)
        top_layout.addWidget(btn_export)
        
        # Table
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(10)
        self.student_table.setHorizontalHeaderLabels([
            "ID", "First Name", "Last Name", "DOB", "Gender", 
            "Address", "Phone", "Email", "Enrollment", "Major"
        ])
        self.student_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.student_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addLayout(top_layout)
        layout.addWidget(self.student_table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Students")

    def load_students(self, search_term=""):
        query = """
            SELECT StudentID, FirstName, LastName, DOB, Gender, 
                   Address, Phone, Email, EnrollmentYear, Major
            FROM students
            WHERE FirstName LIKE %s OR LastName LIKE %s OR Email LIKE %s
            ORDER BY StudentID
        """
        search = f"%{search_term}%"
        rows = db.execute_query(query, (search, search, search))
        
        if rows:
            self.student_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                self.student_table.setItem(i, 0, QTableWidgetItem(str(row['StudentID'])))
                self.student_table.setItem(i, 1, QTableWidgetItem(row['FirstName']))
                self.student_table.setItem(i, 2, QTableWidgetItem(row['LastName']))
                self.student_table.setItem(i, 3, QTableWidgetItem(str(row['DOB'])))
                self.student_table.setItem(i, 4, QTableWidgetItem(row['Gender']))
                self.student_table.setItem(i, 5, QTableWidgetItem(row.get('Address', '')))
                self.student_table.setItem(i, 6, QTableWidgetItem(row.get('Phone', '')))
                self.student_table.setItem(i, 7, QTableWidgetItem(row.get('Email', '')))
                self.student_table.setItem(i, 8, QTableWidgetItem(str(row['EnrollmentYear'])))
                self.student_table.setItem(i, 9, QTableWidgetItem(row.get('Major', '')))
        else:
            self.student_table.setRowCount(0)

    def search_students(self):
        self.load_students(self.student_search.text())

    def add_student(self):
        dialog = StudentCRUDDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_students()

    def edit_student(self):
        current_row = self.student_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a student to edit!")
            return
        
        student_id = int(self.student_table.item(current_row, 0).text())
        dialog = StudentCRUDDialog(self, student_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_students()

    def delete_student(self):
        current_row = self.student_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a student to delete!")
            return
        
        student_id = int(self.student_table.item(current_row, 0).text())
        student_name = f"{self.student_table.item(current_row, 1).text()} {self.student_table.item(current_row, 2).text()}"
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete '{student_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM students WHERE StudentID = %s"
            result = db.execute_query(query, (student_id,), fetch=False)
            if result is not None:
                QMessageBox.information(self, "Success", "Student deleted successfully!")
                self.load_students()

    # ==================== SUBJECTS TAB ====================
    def create_subjects_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Subject")
        btn_add.clicked.connect(self.add_subject)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_subject)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_subjects)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        
        # Table
        self.subject_table = QTableWidget()
        self.subject_table.setColumnCount(3)
        self.subject_table.setHorizontalHeaderLabels(["Subject Code", "Subject Name", "Credits"])
        self.subject_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.subject_table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Subjects")

    def load_subjects(self):
        query = "SELECT * FROM subjects ORDER BY SubjectCode"
        rows = db.execute_query(query)
        
        if rows:
            self.subject_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                self.subject_table.setItem(i, 0, QTableWidgetItem(row['SubjectCode']))
                self.subject_table.setItem(i, 1, QTableWidgetItem(row['SubjectName']))
                self.subject_table.setItem(i, 2, QTableWidgetItem(str(row['Credits'])))
        else:
            self.subject_table.setRowCount(0)

    def add_subject(self):
        dialog = SubjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_subjects()

    def delete_subject(self):
        current_row = self.subject_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a subject!")
            return
        
        code = self.subject_table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Delete subject '{code}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM subjects WHERE SubjectCode = %s"
            db.execute_query(query, (code,), fetch=False)
            self.load_subjects()

    # ==================== LECTURERS TAB ====================
    def create_lecturers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Lecturer")
        btn_add.clicked.connect(self.add_lecturer)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_lecturer)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_lecturers)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        
        self.lecturer_table = QTableWidget()
        self.lecturer_table.setColumnCount(5)
        self.lecturer_table.setHorizontalHeaderLabels([
            "ID", "First Name", "Last Name", "Email", "Office"
        ])
        self.lecturer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.lecturer_table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Lecturers")

    def load_lecturers(self):
        query = "SELECT * FROM lecturers ORDER BY LecturerID"
        rows = db.execute_query(query)
        
        if rows:
            self.lecturer_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                self.lecturer_table.setItem(i, 0, QTableWidgetItem(str(row['LecturerID'])))
                self.lecturer_table.setItem(i, 1, QTableWidgetItem(row['LecturerFirstName']))
                self.lecturer_table.setItem(i, 2, QTableWidgetItem(row['LecturerLastName']))
                self.lecturer_table.setItem(i, 3, QTableWidgetItem(row.get('LecturerEmail', '')))
                self.lecturer_table.setItem(i, 4, QTableWidgetItem(row.get('Office', '')))
        else:
            self.lecturer_table.setRowCount(0)

    def add_lecturer(self):
        dialog = LecturerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_lecturers()

    def delete_lecturer(self):
        current_row = self.lecturer_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a lecturer!")
            return
        
        lecturer_id = int(self.lecturer_table.item(current_row, 0).text())
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Delete this lecturer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM lecturers WHERE LecturerID = %s"
            db.execute_query(query, (lecturer_id,), fetch=False)
            self.load_lecturers()

    # ==================== CLASSES TAB ====================
    def create_classes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Class")
        btn_add.clicked.connect(self.add_class)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_class)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_classes)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        
        self.class_table = QTableWidget()
        self.class_table.setColumnCount(7)
        self.class_table.setHorizontalHeaderLabels([
            "Class ID", "Subject Code", "Lecturer ID", "Class Name", 
            "Semester", "Year", "Max Capacity"
        ])
        self.class_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.class_table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Classes")

    def load_classes(self):
        query = "SELECT * FROM classes ORDER BY Year DESC, Semester"
        rows = db.execute_query(query)
        
        if rows:
            self.class_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                self.class_table.setItem(i, 0, QTableWidgetItem(str(row['ClassID'])))
                self.class_table.setItem(i, 1, QTableWidgetItem(row['SubjectCode']))
                self.class_table.setItem(i, 2, QTableWidgetItem(str(row.get('LecturerID', ''))))
                self.class_table.setItem(i, 3, QTableWidgetItem(row.get('ClassName', '')))
                self.class_table.setItem(i, 4, QTableWidgetItem(row['Semester']))
                self.class_table.setItem(i, 5, QTableWidgetItem(str(row['Year'])))
                self.class_table.setItem(i, 6, QTableWidgetItem(str(row.get('MaxCapacity', ''))))
        else:
            self.class_table.setRowCount(0)

    def add_class(self):
        dialog = ClassDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_classes()

    def delete_class(self):
        current_row = self.class_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a class!")
            return
        
        class_id = int(self.class_table.item(current_row, 0).text())
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Delete this class?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM classes WHERE ClassID = %s"
            db.execute_query(query, (class_id,), fetch=False)
            self.load_classes()

    # ==================== ENROLLMENTS TAB ====================
    def create_enrollments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Enrollment")
        btn_add.clicked.connect(self.add_enrollment)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_enrollment)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_enrollments)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        
        self.enrollment_table = QTableWidget()
        self.enrollment_table.setColumnCount(6)
        self.enrollment_table.setHorizontalHeaderLabels([
            "Student ID", "Student Name", "Class ID", "Grade", "Grade Letter", "Note"
        ])
        self.enrollment_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.enrollment_table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Enrollments")

    def load_enrollments(self):
        query = """
            SELECT e.StudentID, CONCAT(s.FirstName, ' ', s.LastName) as Name,
                   e.ClassID, e.Grade, e.GradeLetter, e.Note
            FROM enrollments e
            JOIN students s ON e.StudentID = s.StudentID
            ORDER BY e.StudentID, e.ClassID
        """
        rows = db.execute_query(query)
        
        if rows:
            self.enrollment_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                self.enrollment_table.setItem(i, 0, QTableWidgetItem(str(row['StudentID'])))
                self.enrollment_table.setItem(i, 1, QTableWidgetItem(row['Name']))
                self.enrollment_table.setItem(i, 2, QTableWidgetItem(str(row['ClassID'])))
                self.enrollment_table.setItem(i, 3, QTableWidgetItem(str(row.get('Grade', ''))))
                self.enrollment_table.setItem(i, 4, QTableWidgetItem(row.get('GradeLetter', '')))
                self.enrollment_table.setItem(i, 5, QTableWidgetItem(row.get('Note', '')))
        else:
            self.enrollment_table.setRowCount(0)

    def add_enrollment(self):
        dialog = EnrollmentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_enrollments()

    def delete_enrollment(self):
        current_row = self.enrollment_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an enrollment!")
            return
        
        student_id = int(self.enrollment_table.item(current_row, 0).text())
        class_id = int(self.enrollment_table.item(current_row, 2).text())
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Delete this enrollment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM enrollments WHERE StudentID=%s AND ClassID=%s"
            db.execute_query(query, (student_id, class_id), fetch=False)
            self.load_enrollments()

    # ==================== QUERIES TAB ====================
    def create_queries_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        query_tabs = QTabWidget()
        
        # Query 1: INNER JOIN
        q1_tab = self.create_query_tab(
            "Student Grades per Subject",
            """
            SELECT s.StudentID, CONCAT(s.FirstName, ' ', s.LastName) as StudentName,
                   sub.SubjectName, e.Grade, e.GradeLetter
            FROM enrollments e
            INNER JOIN students s ON e.StudentID = s.StudentID
            INNER JOIN classes c ON e.ClassID = c.ClassID
            INNER JOIN subjects sub ON c.SubjectCode = sub.SubjectCode
            WHERE e.Grade IS NOT NULL
            ORDER BY s.StudentID, sub.SubjectName
            """,
            ["Student ID", "Student Name", "Subject", "Grade", "Letter"]
        )
        query_tabs.addTab(q1_tab, "Q1: Inner Join")
        
        # Query 2: LEFT JOIN
        q2_tab = self.create_query_tab(
            "All Students with Grades",
            """
            SELECT s.StudentID, CONCAT(s.FirstName, ' ', s.LastName) as StudentName,
                   s.Major, e.Grade
            FROM students s
            LEFT JOIN enrollments e ON s.StudentID = e.StudentID
            ORDER BY s.StudentID
            """,
            ["Student ID", "Student Name", "Major", "Grade"]
        )
        query_tabs.addTab(q2_tab, "Q2: Left Join")
        
        # Query 3: Multi-table JOIN
        q3_tab = self.create_query_tab(
            "Student-Subject-Grade-Lecturer",
            """
            SELECT s.StudentID, CONCAT(s.FirstName, ' ', s.LastName) as StudentName,
                   sub.SubjectName, e.Grade,
                   CONCAT(l.LecturerFirstName, ' ', l.LecturerLastName) as LecturerName
            FROM enrollments e
            INNER JOIN students s ON e.StudentID = s.StudentID
            INNER JOIN classes c ON e.ClassID = c.ClassID
            INNER JOIN subjects sub ON c.SubjectCode = sub.SubjectCode
            LEFT JOIN lecturers l ON c.LecturerID = l.LecturerID
            WHERE e.Grade IS NOT NULL
            ORDER BY s.StudentID
            """,
            ["Student ID", "Student Name", "Subject", "Grade", "Lecturer"]
        )
        query_tabs.addTab(q3_tab, "Q3: Multi-Table")
        
        # Query 4: Above Average
        q4_tab = self.create_query_tab(
            "Students Above Average Grade",
            """
            SELECT s.StudentID, CONCAT(s.FirstName, ' ', s.LastName) as StudentName,
                   ROUND(AVG(e.Grade), 2) as AvgGrade
            FROM students s
            JOIN enrollments e ON s.StudentID = e.StudentID
            WHERE e.Grade IS NOT NULL
            GROUP BY s.StudentID
            HAVING AvgGrade > (SELECT AVG(Grade) FROM enrollments WHERE Grade IS NOT NULL)
            ORDER BY AvgGrade DESC
            """,
            ["Student ID", "Student Name", "Average Grade"]
        )
        query_tabs.addTab(q4_tab, "Q4: Above Average")
        
        layout.addWidget(query_tabs)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Queries")

    def create_query_tab(self, title, query, headers):
        tab = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"<b>{title}</b>"))
        
        btn_layout = QHBoxLayout()
        btn_run = QPushButton("Run Query")
        btn_export = QPushButton("Export CSV")
        btn_layout.addWidget(btn_run)
        btn_layout.addWidget(btn_export)
        btn_layout.addStretch()
        
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.horizontalHeader().setStretchLastSection(True)
        
        def run_query():
            rows = db.execute_query(query)
            if rows:
                table.setRowCount(len(rows))
                for i, row in enumerate(rows):
                    for j, key in enumerate(row.keys()):
                        table.setItem(i, j, QTableWidgetItem(str(row[key])))
            else:
                table.setRowCount(0)
        
        btn_run.clicked.connect(run_query)
        btn_export.clicked.connect(lambda: self.export_table_to_csv(table, title))
        
        layout.addLayout(btn_layout)
        layout.addWidget(table)
        tab.setLayout(layout)
        
        return tab

    # ==================== DASHBOARD TAB ====================
    def create_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<h2>Dashboard - KPIs</h2>"))
        
        # KPI Grid
        kpi_layout = QGridLayout()
        
        self.lbl_total_students = QLabel("Students: 0")
        self.lbl_total_subjects = QLabel("Subjects: 0")
        self.lbl_total_classes = QLabel("Classes: 0")
        self.lbl_avg_grade = QLabel("Avg Grade: 0.00")
        
        kpi_layout.addWidget(self.create_kpi_widget("Total Students", self.lbl_total_students), 0, 0)
        kpi_layout.addWidget(self.create_kpi_widget("Total Subjects", self.lbl_total_subjects), 0, 1)
        kpi_layout.addWidget(self.create_kpi_widget("Total Classes", self.lbl_total_classes), 1, 0)
        kpi_layout.addWidget(self.create_kpi_widget("Average Grade", self.lbl_avg_grade), 1, 1)
        
        layout.addLayout(kpi_layout)
        
        # Top students
        layout.addWidget(QLabel("<h3>Top 10 Students by Average Grade</h3>"))
        self.top_students_table = QTableWidget()
        self.top_students_table.setColumnCount(3)
        self.top_students_table.setHorizontalHeaderLabels(["Rank", "Student Name", "Avg Grade"])
        self.top_students_table.setMaximumHeight(300)
        layout.addWidget(self.top_students_table)
        
        # Refresh button
        btn_refresh = QPushButton("Refresh Dashboard")
        btn_refresh.clicked.connect(self.load_dashboard)
        layout.addWidget(btn_refresh)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Dashboard")

    def create_kpi_widget(self, title, label):
        widget = QWidget()
        widget.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 10px;")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>{title}</b>"))
        label.setStyleSheet("font-size: 24px; color: #2196F3;")
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    def load_dashboard(self):
        # Total students
        result = db.execute_query("SELECT COUNT(*) as cnt FROM students")
        if result:
            self.lbl_total_students.setText(str(result[0]['cnt']))
        
        # Total subjects
        result = db.execute_query("SELECT COUNT(*) as cnt FROM subjects")
        if result:
            self.lbl_total_subjects.setText(str(result[0]['cnt']))
        
        # Total classes
        result = db.execute_query("SELECT COUNT(*) as cnt FROM classes")
        if result:
            self.lbl_total_classes.setText(str(result[0]['cnt']))
        
        # Average grade
        result = db.execute_query("SELECT ROUND(AVG(Grade), 2) as avg FROM enrollments WHERE Grade IS NOT NULL")
        if result and result[0]['avg']:
            self.lbl_avg_grade.setText(str(result[0]['avg']))
        
        # Top 10 students
        query = """
            SELECT CONCAT(s.FirstName, ' ', s.LastName) as Name,
                   ROUND(AVG(e.Grade), 2) as AvgGrade
            FROM students s
            JOIN enrollments e ON s.StudentID = e.StudentID
            WHERE e.Grade IS NOT NULL
            GROUP BY s.StudentID
            ORDER BY AvgGrade DESC
            LIMIT 10
        """
        rows = db.execute_query(query)
        if rows:
            self.top_students_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                self.top_students_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                self.top_students_table.setItem(i, 1, QTableWidgetItem(row['Name']))
                self.top_students_table.setItem(i, 2, QTableWidgetItem(str(row['AvgGrade'])))

    # ==================== UTILITY FUNCTIONS ====================
    def load_all_data(self):
        self.load_students()
        self.load_subjects()
        self.load_lecturers()
        self.load_classes()
        self.load_enrollments()
        self.load_dashboard()

    def export_table_to_csv(self, table, filename):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", f"{filename}.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Headers
                headers = []
                for col in range(table.columnCount()):
                    headers.append(table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Data
                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Data exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:" )