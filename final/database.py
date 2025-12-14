import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QApplication
import sys
from design import Ui_MainWindow

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, host='localhost', user='root', password='', database=''):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor()
            print("Connected to database")
        except Error as e:
            print("Database connection error:", e)

    def fetch_all(self, query):
        if not self.cursor:
            return []
        self.cursor.execute(query)
        return self.cursor.fetchall()

class StudentTableWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


        # 2. Kết nối database
        self.db = DatabaseManager()
        self.db.connect(
            host='localhost',
            user='root',
            password='lequyen5002',
            database='student_management'
        )

        # 3. Load dữ liệu
        self.load_students_table()

    def load_students_table(self):
        # Query dữ liệu từ MySQL
        query = "SELECT StudentID, FirstName, LastName, DOB, Gender, Email, Major FROM students"
        rows = self.db.fetch_all(query)

        if not rows:
            return

        # 4. Cài đặt số hàng và cột
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(len(rows[0]))

        # 5. Đặt tên cột
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'First Name', 'Last Name', 'DOB', 'Gender', 'Email', 'Major'])

        # 6. Đưa dữ liệu vào table
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    

import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QApplication
import sys
from design import Ui_MainWindow

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, host='localhost', user='root', password='', database=''):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor()
            print("Connected to database")
        except Error as e:
            print("Database connection error:", e)

    def fetch_all(self, query):
        if not self.cursor:
            return []
        self.cursor.execute(query)
        return self.cursor.fetchall()

class StudentTableWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


        # 2. Kết nối database
        self.db = DatabaseManager()
        self.db.connect(
            host='localhost',
            user='root',
            password='lequyen5002',
            database='student_management'
        )

        # 3. Load dữ liệu
        self.load_students_table()

    def load_students_table(self):
        # Query dữ liệu từ MySQL
        query = "SELECT StudentID, FirstName, LastName, DOB, Gender, Email, Major FROM students"
        rows = self.db.fetch_all(query)

        if not rows:
            return

        # 4. Cài đặt số hàng và cột
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(len(rows[0]))

        # 5. Đặt tên cột
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'First Name', 'Last Name', 'DOB', 'Gender', 'Email', 'Major'])

        # 6. Đưa dữ liệu vào table
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = StudentTableWindow()
    window.show()
    sys.exit(app.exec())