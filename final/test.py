import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLineEdit, 
    QLabel, QPushButton, QComboBox, QSpinBox, 
    QStackedWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIntValidator

# !!! PHẢI IMPORT FILE TÀI NGUYÊN ĐÃ ĐƯỢC BIÊN DỊCH !!!
# Vui lòng tạo file icon_rc.py từ hi.qrc bằng pyside6-rcc
try:
    import icon_rc  
except ImportError:
    print("WARNING: icon_rc.py not found. Icons may not display correctly.")

# Import lớp giao diện từ file .ui đã biên dịch
try:
    from design_ui import Ui_MainWindow 
except ImportError:
    # Nếu không tìm thấy, tạo một lớp giả để code chạy được
    class Ui_MainWindow(object):
        def setupUi(self, MainWindow):
            MainWindow.setWindowTitle("SMS - Missing UI File")
            
            # Khởi tạo các widget cần thiết để tránh lỗi AttributeError
            self.stackedWidget = QStackedWidget(MainWindow)
            self.Students = QWidget() # Trang Students cũ (Index 0)
            self.stackedWidget.addWidget(self.Students)
            
            # Mô phỏng các nút bấm (dùng tên đã được sửa đổi trong các câu trả lời trước)
            self.pushButton_Students = QPushButton("Students (CRUD)", MainWindow)
            self.pushButton_Lecturers = QPushButton("Lecturers (CRUD)", MainWindow)
            self.pushButton_Classes = QPushButton("Classes (CRUD)", MainWindow)
            self.pushButton_Subjects = QPushButton("Subjects (CRUD)", MainWindow)
            self.pushButton_Enrollments = QPushButton("Enrollments (CRUD)", MainWindow)
            self.pushButton_Queries = QPushButton("Reports & Queries", MainWindow)
            self.pushButton_Dashboard = QPushButton("Dashboard", MainWindow)

            # Các nút được định nghĩa trong file .ui gốc
            self.pushButton = self.pushButton_Students
            self.pushButton_2 = self.pushButton_Lecturers # Teachers -> Lecturers
            self.pushButton_3 = self.pushButton_Classes
            self.pushButton_4 = self.pushButton_Subjects
            
# ============================================================
# LỚP ĐẠI DIỆN CHO MÀN HÌNH STUDENTS CRUD
# ============================================================
class StudentsCRUDPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # 1. KHU VỰC FORM NHẬP/CHỈNH SỬA
        self.setup_form_section()
        self.layout.addWidget(self.form_widget)
        
        # 2. KHU VỰC BẢNG DỮ LIỆU
        self.setup_table_section()
        self.layout.addWidget(self.table_widget)
        
        # Thử nạp dữ liệu giả định để minh họa
        self.load_sample_data()

    def setup_form_section(self):
        """Thiết lập khu vực Form và Nút CRUD."""
        self.form_widget = QWidget()
        grid = QGridLayout(self.form_widget)

        # Định nghĩa các trường dữ liệu theo schema.sql 
        
        # Hàng 1
        grid.addWidget(QLabel("First Name:"), 0, 0)
        self.input_firstName = QLineEdit()
        grid.addWidget(self.input_firstName, 0, 1)

        grid.addWidget(QLabel("Last Name:"), 0, 2)
        self.input_lastName = QLineEdit()
        grid.addWidget(self.input_lastName, 0, 3)

        # Hàng 2 (Validation: Date format)
        grid.addWidget(QLabel("Birthdate:"), 1, 0)
        self.input_dob = QDateEdit(calendarPopup=True)
        self.input_dob.setDate(QDate(2005, 1, 1))
        self.input_dob.setDisplayFormat("yyyy-MM-dd")
        grid.addWidget(self.input_dob, 1, 1)

        grid.addWidget(QLabel("Gender:"), 1, 2)
        self.input_gender = QComboBox()
        self.input_gender.addItems(["M", "F", "O"]) # ENUM('M','F','O') 
        grid.addWidget(self.input_gender, 1, 3)

        # Hàng 3
        grid.addWidget(QLabel("Email:"), 2, 0)
        self.input_email = QLineEdit()
        grid.addWidget(self.input_email, 2, 1)

        grid.addWidget(QLabel("Major:"), 2, 2)
        self.input_major = QLineEdit()
        grid.addWidget(self.input_major, 2, 3)

        # KHU VỰC NÚT CRUD
        self.btn_create = QPushButton("Create New")
        self.btn_edit = QPushButton("Edit Selected")
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_save = QPushButton("Save Changes")
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_create)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_save)
        grid.addLayout(btn_layout, 3, 0, 1, 4) # Đặt 4 nút vào hàng cuối, chiếm 4 cột

        # KẾT NỐI SỰ KIỆN (Placeholder for actual database logic)
        self.btn_create.clicked.connect(self.validate_and_create)
        # self.btn_edit.clicked.connect(self.populate_form_for_edit)
        # self.btn_delete.clicked.connect(self.delete_student)
        # self.btn_save.clicked.connect(self.validate_and_save)

    def setup_table_section(self):
        """Thiết lập QTableWidget để xem dữ liệu (paged table)."""
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5) # Ví dụ: ID, Tên, Ngày sinh, Email, Major
        self.table_widget.setHorizontalHeaderLabels(["ID", "Full Name", "DOB", "Email", "Major"])
        
        # Thiết lập bảng để tự điều chỉnh kích thước cột
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # KẾT NỐI SỰ KIỆN: Khi chọn một hàng, thông tin sẽ hiển thị trên Form
        # self.table_widget.cellClicked.connect(self.populate_form_for_edit)

    def load_sample_data(self):
        """Tải dữ liệu giả định vào bảng."""
        sample_data = [
            (1, "Minh Tran", "2004-05-12", "s1@example.com", "Computer Science"),
            (2, "Linh Pham", "2004-09-21", "s2@example.com", "Physics"),
            (3, "Khoa Le", "2003-03-10", "s3@example.com", "Mathematics"),
        ]
        
        self.table_widget.setRowCount(len(sample_data))
        for row_index, row_data in enumerate(sample_data):
            for col_index, item in enumerate(row_data):
                self.table_widget.setItem(row_index, col_index, QTableWidgetItem(str(item)))

    def validate_and_create(self):
        """Ví dụ về Validation và logic Create."""
        
        # Yêu cầu Validation 1: Required fields must not be empty
        if not self.input_firstName.text() or not self.input_lastName.text() or not self.input_email.text():
            QMessageBox.warning(self, "Validation Error", "First Name, Last Name, and Email are required fields.")
            return

        # Yêu cầu Validation 2: Date format (Đã được xử lý bởi QDateEdit)
        dob_str = self.input_dob.date().toString("yyyy-MM-dd")
        
        # Yêu cầu Validation 4: Prevent duplicate logical keys (Email - unique )
        # (Trong ứng dụng thực tế, sẽ cần kiểm tra cơ sở dữ liệu ở đây)
        if "s1@example.com" in self.input_email.text(): # Ví dụ kiểm tra trùng lặp
             QMessageBox.critical(self, "Validation Error", "Email already exists (duplicate logical key).")
             return

        QMessageBox.information(self, "Success", f"Student {self.input_firstName.text()} created successfully (DOB: {dob_str}).\nDatabase connection needed to finalize.")
        
# ============================================================
# LỚP MAIN WINDOW (Kế thừa từ UI)
# ============================================================
class MySideBar (QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Student Management System")
        
        # Tên các trang trong QStackedWidget (được sinh ra từ file .ui)
        # page_Students_CRUD sẽ thay thế widget cũ self.Students
        self.students_page = StudentsCRUDPage(self.centralwidget) 
        self.stackedWidget.removeWidget(self.Students)
        self.stackedWidget.insertWidget(0, self.students_page)
        
        # Thiết lập các trang còn lại (dùng QWidget trống cho mục đích minh họa)
        self.lecturers_page = QWidget()
        self.classes_page = QWidget()
        self.subjects_page = QWidget()
        self.enrollments_page = QWidget()
        self.queries_page = QWidget()
        self.dashboard_page = QWidget()
        
        # Đảm bảo QStackedWidget đã được mở rộng trong phiên bản UI cuối cùng 
        # để chứa tất cả 7 trang (5 CRUD + Queries + Dashboard)
        # Nếu UI của bạn chỉ có 2 trang, bạn cần thêm các trang này:
        if self.stackedWidget.count() < 7:
            # Nếu UI gốc chỉ có 2 trang, ta sẽ thêm 5 trang còn lại
            self.stackedWidget.addWidget(self.lecturers_page)    # Index 1
            self.stackedWidget.addWidget(self.classes_page)      # Index 2
            self.stackedWidget.addWidget(self.subjects_page)     # Index 3
            self.stackedWidget.addWidget(self.enrollments_page)  # Index 4
            self.stackedWidget.addWidget(self.queries_page)      # Index 5
            self.stackedWidget.addWidget(self.dashboard_page)    # Index 6

        self.connect_signals()

    def connect_signals(self):
        """Kết nối các nút bấm sidebar với QStackedWidget."""
        
        # Giả định các nút bấm đã được đặt tên đúng cách trong UI
        self.pushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0)) # Students
        self.pushButton_2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1)) # Lecturers (Teachers)
        self.pushButton_3.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2)) # Classes
        self.pushButton_4.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3)) # Subjects
        
        # Nếu đã thêm các nút mới vào UI (Enrollments, Queries, Dashboard)
        if hasattr(self, 'pushButton_5'): 
            self.pushButton_5.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(4)) # Enrollments
        if hasattr(self, 'pushButton_6'):
            self.pushButton_6.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(5)) # Queries
        if hasattr(self, 'pushButton_7'):
            self.pushButton_7.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(6)) # Dashboard

# Khối chạy ứng dụng
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MySideBar()
    window.show()
    sys.exit(app.exec())