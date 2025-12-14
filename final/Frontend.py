# Frontend.py - Integrated with your existing design.py
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt6.QtCore import QDate
from design import Ui_MainWindow  
from studentdialog_logic import StudentDialog
import mysql.connector
from mysql.connector import Error
import csv

class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Kết nối database
        self.db = DatabaseManager()
        self.db.create_connect()

        # Kết nối nút với phương thức đổi page
        self.pushButton.clicked.connect(self.show_students_page)
        self.pushButton_2.clicked.connect(self.show_teachers_page)
        self.pushButton_4.clicked.connect(self.show_classes_page)
        self.pushButton_3.clicked.connect(self.show_subjects_page)
        
        # Student operations
        self.pushButton_5.clicked.connect(self.show_student_dialog)
        self.pushButton_7.clicked.connect(self.edit_student)
        self.pushButton_6.clicked.connect(self.delete_student)
        
        # Export CSV button (Confirm_3)
        if hasattr(self, 'Confirm_3'):
            self.Confirm_3.clicked.connect(self.export_students_csv)
        
        # Search functionality
        if hasattr(self, 'lineEdit_2'):
            self.lineEdit_2.textChanged.connect(self.search_students)
        
        # Load initial data
        self.load_students_table()

    # ==================== PAGE NAVIGATION ====================
    def show_student_dialog(self):
        """Show add student dialog"""
        dialog = StudentDialog()
        if dialog.exec():  # If dialog accepted (student added)
            self.load_students_table()  # Refresh table
            QMessageBox.information(self, "Success", "Student added! Table refreshed.")
        
    def show_students_page(self):
        self.stackedWidget.setCurrentWidget(self.Students)
        self.load_students_table()  # Refresh when showing page

    def show_teachers_page(self):
        self.stackedWidget.setCurrentWidget(self.Teachers)

    def show_classes_page(self):
        self.stackedWidget.setCurrentWidget(self.Classes)

    def show_subjects_page(self):
        self.stackedWidget.setCurrentWidget(self.Subjects)

    # ==================== STUDENT CRUD OPERATIONS ====================
    def load_students_table(self, search_term=""):
        """Load students from database into table"""
        try:
            if search_term:
                query = """
                    SELECT StudentID, FirstName, LastName, Address, Email, Phone, 
                           DOB, EnrollmentYear, Gender, Major
                    FROM students
                    WHERE FirstName LIKE %s OR LastName LIKE %s OR Email LIKE %s
                    ORDER BY StudentID
                """
                search = f"%{search_term}%"
                self.db.cursor.execute(query, (search, search, search))
            else:
                query = """
                    SELECT StudentID, FirstName, LastName, Address, Email, Phone, 
                           DOB, EnrollmentYear, Gender, Major
                    FROM students
                    ORDER BY StudentID
                """
                self.db.cursor.execute(query)
            
            rows = self.db.cursor.fetchall()
            
            if rows:
                self.tableWidget.setRowCount(len(rows))
                for row_idx, row_data in enumerate(rows):
                    for col_idx, value in enumerate(row_data):
                        self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                
                # Resize columns to content
                self.tableWidget.resizeColumnsToContents()
            else:
                self.tableWidget.setRowCount(0)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load students: {str(e)}")

    def search_students(self):
        """Search students as user types"""
        if hasattr(self, 'lineEdit_2'):
            search_term = self.lineEdit_2.text().strip()
            self.load_students_table(search_term)

    def delete_student(self):
        """Delete selected student"""
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a student to delete!")
            return
        
        # Get StudentID from selected row (column 0)
        row = selected_items[0].row()
        student_id = self.tableWidget.item(row, 0).text()
        student_name = f"{self.tableWidget.item(row, 1).text()} {self.tableWidget.item(row, 2).text()}"

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{student_name}' (ID: {student_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute("DELETE FROM students WHERE StudentID=%s", (student_id,))
                self.db.connection.commit()
                QMessageBox.information(self, "Deleted", "Student deleted successfully.")
                self.load_students_table()  # Refresh table
            except Exception as e:
                self.db.connection.rollback()
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")

    def edit_student(self):
        """Edit selected student"""
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a student to edit!")
            return
        
        row = selected_items[0].row()
        student_id = self.tableWidget.item(row, 0).text()

        # Get existing data
        first_name = self.tableWidget.item(row, 1).text()
        last_name = self.tableWidget.item(row, 2).text()
        address = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else ""
        email = self.tableWidget.item(row, 4).text()
        phone = self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else ""
        dob = self.tableWidget.item(row, 6).text()
        enrollment_year = self.tableWidget.item(row, 7).text()
        gender = self.tableWidget.item(row, 8).text()
        major = self.tableWidget.item(row, 9).text() if self.tableWidget.item(row, 9) else ""

        # Create edit dialog
        dialog = StudentDialog(edit_mode=True, student_id=student_id)
        
        # Pre-fill form with existing data
        dialog.ui.lineEdit.setText(student_id)
        dialog.ui.lineEdit.setReadOnly(True)  # ID cannot be changed
        dialog.ui.lineEdit_4.setText(f"{first_name} {last_name}")
        dialog.ui.lineEdit_3.setText(address)
        dialog.ui.lineEdit_5.setText(phone)
        dialog.ui.lineEdit_6.setText(email)
        dialog.ui.dateEdit.setDate(QDate.fromString(dob, "yyyy-MM-dd"))
        
        # Set gender
        if gender == 'M':
            dialog.ui.comboBox.setCurrentText("Male")
        elif gender == 'F':
            dialog.ui.comboBox.setCurrentText("Female")
        
        dialog.ui.comboBox_2.setCurrentText(major)

        if dialog.exec():  # When Confirm is clicked
            self.load_students_table()  # Refresh table
            QMessageBox.information(self, "Success", "Student updated successfully!")

    def export_students_csv(self):
        """Export students table to CSV"""
        if self.tableWidget.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No data to export!")
            return
        
        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Students to CSV",
            "students_export.csv",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write headers
                headers = []
                for col in range(self.tableWidget.columnCount()):
                    header_item = self.tableWidget.horizontalHeaderItem(col)
                    headers.append(header_item.text() if header_item else f"Column{col}")
                writer.writerow(headers)
                
                # Write data rows
                for row in range(self.tableWidget.rowCount()):
                    row_data = []
                    for col in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Data exported successfully to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")

    # ==================== CLEANUP ====================
    def closeEvent(self, event):
        """Close database connection when window closes"""
        if self.db.connection and self.db.connection.is_connected():
            self.db.cursor.close()
            self.db.connection.close()
            print("Database connection closed")
        event.accept()


# ==================== DATABASE MANAGER ====================
class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def create_connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='lequyen5002',
                database='student_management'   
            )
            if self.connection.is_connected():
                print("✓ Kết nối MySQL thành công!")
                self.cursor = self.connection.cursor()
                return True
        except Error as e:
            print(f"✗ Lỗi kết nối MySQL: {e}")
            self.connection = None
            self.cursor = None
            return False

    def fetch_query(self, query, params=None):
        """Execute query and fetch results"""
        if self.cursor is None:
            print("Chưa kết nối database.")
            return None
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"Query error: {e}")
            return None

    def execute_update(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE queries"""
        if self.cursor is None:
            print("Chưa kết nối database.")
            return False
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Error as e:
            print(f"Execute error: {e}")
            self.connection.rollback()
            return False