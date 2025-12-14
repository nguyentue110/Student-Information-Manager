# main.py - Entry point for Student Management System
"""
HƯỚNG DẪN CHẠY:
1. Đảm bảo đã cài đặt: PyQt6, mysql-connector-python, PyQt6-Charts
2. Đảm bảo database đã được tạo (chạy schema.sql và seed.sql)
3. Cập nhật password MySQL trong db_connection.py
4. Chạy: python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QPushButton, QStackedWidget, QLabel, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import pages
from main_win import StudentsPage, SubjectsPage, LecturersPage, ClassesPage
from main_win import EnrollmentsPage, Query1Page, Query2Page, Query3Page, Query4Page, DashboardPage

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main Application Window
    
    NAVIGATION:
    - Dashboard (overview)
    - Students (CRUD)
    - Subjects (CRUD)
    - Lecturers (CRUD)
    - Classes (CRUD)
    - Enrollments (CRUD)
    - Queries (4 required queries)
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setGeometry(100, 100, 1400, 800)
        
        self.setup_ui()
        
        # Show dashboard by default
        self.show_page("Dashboard")
    
    def setup_ui(self):
        """Setup main UI structure"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Right Content Area
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #ecf0f1;")
        main_layout.addWidget(self.stacked_widget)
        
        # Add pages
        self.pages = {}
        self.add_page("Dashboard", DashboardPage())
        self.add_page("Students", StudentsPage())
        self.add_page("Subjects", SubjectsPage())
        self.add_page("Lecturers", LecturersPage())
        self.add_page("Classes", ClassesPage())
        self.add_page("Enrollments", EnrollmentsPage())
        self.add_page("Query 1: INNER JOIN", Query1Page())
        self.add_page("Query 2: LEFT JOIN", Query2Page())
        self.add_page("Query 3: Multi-table", Query3Page())
        self.add_page("Query 4: Above Avg", Query4Page())
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("📚 Student\nManagement")
        header.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 20px;
            background-color: #1abc9c;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Navigation buttons
        nav_items = [
            ("📊 Dashboard", "Dashboard"),
            ("👨‍🎓 Students", "Students"),
            ("📖 Subjects", "Subjects"),
            ("👨‍🏫 Lecturers", "Lecturers"),
            ("🏫 Classes", "Classes"),
            ("📝 Enrollments", "Enrollments"),
            ("", ""),  # Separator
            ("📋 QUERIES", ""),
            ("Q1: INNER JOIN", "Query 1: INNER JOIN"),
            ("Q2: LEFT JOIN", "Query 2: LEFT JOIN"),
            ("Q3: Multi-table", "Query 3: Multi-table"),
            ("Q4: Above Avg", "Query 4: Above Avg"),
        ]
        
        for label, page_name in nav_items:
            if not label:
                # Separator
                sep = QLabel()
                sep.setFixedHeight(10)
                layout.addWidget(sep)
            elif not page_name:
                # Section header
                lbl = QLabel(label)
                lbl.setStyleSheet("color: #95a5a6; font-size: 12px; font-weight: bold; padding: 10px 15px;")
                layout.addWidget(lbl)
            else:
                btn = QPushButton(label)
                btn.clicked.connect(lambda checked, p=page_name: self.show_page(p))
                layout.addWidget(btn)
        
        layout.addStretch()
        
        # Footer
        footer = QLabel("v1.0.0 - 2024")
        footer.setStyleSheet("color: #95a5a6; padding: 10px; font-size: 10px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def add_page(self, name, widget):
        """Add page to stacked widget"""
        self.pages[name] = widget
        self.stacked_widget.addWidget(widget)
    
    def show_page(self, page_name):
        """Show specific page"""
        if page_name in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_name])
            logger.info(f"Showing page: {page_name}")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Test database connection first
    try:
        from db_connection import test_connection
        if not test_connection():
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Database Error")
            msg.setText("Cannot connect to database!")
            msg.setInformativeText("Please check:\n1. MySQL is running\n2. Database exists\n3. Password is correct in db_connection.py")
            msg.exec()
            sys.exit(1)
    except Exception as e:
        print(f"Database connection error: {e}")
        sys.exit(1)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    logger.info("Application started successfully!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()