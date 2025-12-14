# studentdialog_logic.py - Updated with Edit Mode Support
from PyQt6 import QtWidgets
from StudentDialogUI import Ui_Dialog
import mysql.connector
from mysql.connector import Error
import re

class StudentDialog(QtWidgets.QDialog):
    def __init__(self, edit_mode=False, student_id=None):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        # Set mode
        self.edit_mode = edit_mode
        self.student_id = student_id

        # Update dialog title and button text based on mode
        if self.edit_mode:
            self.setWindowTitle("Edit Student")
            self.ui.Confirm.setText("Update Student")
        else:
            self.setWindowTitle("Add New Student")
            self.ui.Confirm.setText("Add Student")

        # Connect buttons
        self.ui.Confirm.clicked.connect(self.save_student)
        self.ui.pushButton_2.clicked.connect(self.close)

        # Connect to MySQL
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='lequyen5002',
                database='student_management' 
            )
            self.cursor = self.conn.cursor()
            print("Connected to MySQL")
        except Error as e:
            print("Error connecting to MySQL:", e)
            QtWidgets.QMessageBox.critical(self, "Database Error", 
                f"Cannot connect to database:\n{str(e)}")

    def save_student(self):
        """Save or update student based on mode"""
        if self.edit_mode:
            self.update_student()
        else:
            self.add_student()

    def add_student(self):
        """Add new student to database"""
        try:
            # Get form data
            student_id = self.ui.lineEdit.text().strip()
            full_name = self.ui.lineEdit_4.text().strip()
            address = self.ui.lineEdit_3.text().strip()
            phone = self.ui.lineEdit_5.text().strip()
            email = self.ui.lineEdit_6.text().strip()
            dob_qdate = self.ui.dateEdit.date()
            gender_text = self.ui.comboBox.currentText()
            major = self.ui.comboBox_2.currentText().strip()
            enrollment_year = 2024  # You can make this dynamic

            # ------------------- Validation -------------------
            # 1. Required fields
            if not full_name or not email:
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Full Name and Email are required.")
                return

            # 2. DOB validation
            if not dob_qdate.isValid():
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Invalid birthdate.")
                return
            dob = dob_qdate.toString("yyyy-MM-dd")

            # 3. Email validation (regex)
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Invalid email format. Use: example@domain.com")
                return

            # 4. Phone validation (if provided)
            if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Phone number must contain only digits, +, -, or spaces.")
                return

            # 5. Split full name
            name_parts = full_name.strip().split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = ' '.join(name_parts[1:])
            else:
                first_name = full_name
                last_name = ''

            # 6. Gender mapping
            gender_map = {
                'Male': 'M',
                'Female': 'F',
                'Nam': 'M',
                'Nữ': 'F'
            }
            gender = gender_map.get(gender_text, gender_text[0] if gender_text else 'M')

            # 7. Major validation
            if not major or major == "New Item":
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Please select or enter a valid major.")
                return

            # Calculate enrollment year from DOB (assume 18 years old at enrollment)
            enrollment_year = dob_qdate.year() + 18

            # ------------------- Insert -------------------
            sql = """
                INSERT INTO students (FirstName, LastName, DOB, Gender, Address, Phone, Email, EnrollmentYear, Major)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (first_name, last_name, dob, gender, address, phone, email, enrollment_year, major)
            
            self.cursor.execute(sql, values)
            self.conn.commit()
            
            QtWidgets.QMessageBox.information(self, "Success", 
                f"Student '{full_name}' added successfully!")
            
            # Clear form
            self.clear_form()
            self.accept()  # Close dialog with success

        except mysql.connector.IntegrityError as e:
            self.conn.rollback()
            if "Duplicate entry" in str(e):
                QtWidgets.QMessageBox.warning(self, "Error", 
                    "Email already exists in the database!")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", 
                    f"Database integrity error:\n{str(e)}")
        except Exception as e:
            self.conn.rollback()
            QtWidgets.QMessageBox.critical(self, "Error", 
                f"An error occurred:\n{str(e)}")

    def update_student(self):
        """Update existing student in database"""
        try:
            # Get form data
            full_name = self.ui.lineEdit_4.text().strip()
            address = self.ui.lineEdit_3.text().strip()
            phone = self.ui.lineEdit_5.text().strip()
            email = self.ui.lineEdit_6.text().strip()
            dob_qdate = self.ui.dateEdit.date()
            gender_text = self.ui.comboBox.currentText()
            major = self.ui.comboBox_2.currentText().strip()

            # ------------------- Validation -------------------
            if not full_name or not email:
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Full Name and Email are required.")
                return

            if not dob_qdate.isValid():
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Invalid birthdate.")
                return
            dob = dob_qdate.toString("yyyy-MM-dd")

            # Email validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Invalid email format.")
                return

            # Phone validation
            if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Phone number must contain only digits.")
                return

            # Split full name
            name_parts = full_name.strip().split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = ' '.join(name_parts[1:])
            else:
                first_name = full_name
                last_name = ''

            # Gender mapping
            gender_map = {
                'Male': 'M',
                'Female': 'F',
                'Nam': 'M',
                'Nữ': 'F',
                'M': 'M',
                'F': 'F'
            }
            gender = gender_map.get(gender_text, gender_text[0] if gender_text else 'M')

            # Major validation
            if not major or major == "New Item":
                QtWidgets.QMessageBox.warning(self, "Validation Error", 
                    "Please select or enter a valid major.")
                return

            # Calculate enrollment year
            enrollment_year = dob_qdate.year() + 18

            # ------------------- Update -------------------
            sql = """
                UPDATE students 
                SET FirstName=%s, LastName=%s, DOB=%s, Gender=%s, 
                    Address=%s, Phone=%s, Email=%s, EnrollmentYear=%s, Major=%s
                WHERE StudentID=%s
            """
            values = (first_name, last_name, dob, gender, address, phone, 
                     email, enrollment_year, major, self.student_id)
            
            self.cursor.execute(sql, values)
            self.conn.commit()
            
            QtWidgets.QMessageBox.information(self, "Success", 
                f"Student '{full_name}' updated successfully!")
            
            self.accept()  # Close dialog with success

        except mysql.connector.IntegrityError as e:
            self.conn.rollback()
            if "Duplicate entry" in str(e):
                QtWidgets.QMessageBox.warning(self, "Error", 
                    "Email already exists for another student!")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", 
                    f"Database integrity error:\n{str(e)}")
        except Exception as e:
            self.conn.rollback()
            QtWidgets.QMessageBox.critical(self, "Error", 
                f"An error occurred:\n{str(e)}")

    def clear_form(self):
        """Clear all form fields"""
        self.ui.lineEdit.clear()
        self.ui.lineEdit_4.clear()
        self.ui.lineEdit_3.clear()
        self.ui.lineEdit_5.clear()
        self.ui.lineEdit_6.clear()
        self.ui.comboBox.setCurrentIndex(0)
        self.ui.comboBox_2.setCurrentIndex(0)

    def closeEvent(self, event):
        """Close database connection when dialog closes"""
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("Dialog database connection closed")
        event.accept()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = StudentDialog()
    dialog.show()
    sys.exit(app.exec())