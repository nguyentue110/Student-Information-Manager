# models.py - Complete Model Layer cho tất cả entities
"""
GIẢI THÍCH:
- Mỗi model class đại diện cho 1 bảng trong DB
- Implement đầy đủ CRUD operations
- Sử dụng db connection pool và validators
- Transaction support cho data integrity
"""

from db_connection import db
from typing import List, Dict, Optional, Tuple
from validators import Validators, ValidationError
import logging

logger = logging.getLogger(__name__)
def validate_student_data(data):
    return Validators.validate_student_data(data)

def validate_subject_data(data):
    return Validators.validate_subject_data(data)

def validate_enrollment_data(data):
    return Validators.validate_enrollment_data(data)


# ============================================================
# BASE MODEL - Abstract class với common methods
# ============================================================

class BaseModel:
    """
    Base class cho tất cả models
    Chứa common functionality
    """
    
    @staticmethod
    def _format_where_clause(filters: Dict) -> Tuple[str, List]:
        """
        Tạo WHERE clause từ dict filters
        
        Args:
            filters: Dict of field: value
        
        Returns:
            Tuple of (where_string, params_list)
        """
        if not filters:
            return "", []
        
        conditions = []
        params = []
        
        for field, value in filters.items():
            conditions.append(f"{field} = %s")
            params.append(value)
        
        where_clause = " WHERE " + " AND ".join(conditions)
        return where_clause, params


# ============================================================
# STUDENT MODEL
# ============================================================

class StudentModel(BaseModel):
    """
    Model for students table
    
    CRUD:
    - create(): Add new student
    - get_by_id(): Get student by ID
    - update(): Update student info
    - delete(): Delete student
    - list(): Get paginated list
    - search(): Search students
    """
    
    @staticmethod
    def create(data: dict) -> int:
        """
        Create new student
        
        Args:
            data: Dict với keys: full_name, email, dob, gender, etc.
        
        Returns:
            StudentID của student mới
        
        Raises:
            ValidationError: Nếu data invalid
        """
        # Validate data
        clean_data = validate_student_data(data)
        
        sql = """
            INSERT INTO students
            (FirstName, LastName, DOB, Gender, Address, Phone, Email, EnrollmentYear, Major)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            clean_data['first_name'],
            clean_data['last_name'],
            clean_data['dob'],
            clean_data['gender'],
            clean_data['address'],
            clean_data['phone'],
            clean_data['email'],
            clean_data['enrollment_year'],
            clean_data['major']
        )
        
        try:
            with db.get_cursor(dictionary=False) as cursor:
                cursor.execute(sql, params)
                student_id = cursor.lastrowid
                logger.info(f"Created student ID: {student_id}")
                return student_id
        except Exception as e:
            logger.error(f"Failed to create student: {e}")
            raise
    
    @staticmethod
    def get_by_id(student_id: int) -> Optional[Dict]:
        """Get student by ID"""
        sql = "SELECT * FROM students WHERE StudentID = %s"
        return db.execute_query(sql, (student_id,), fetch_one=True)
    
    @staticmethod
    def update(student_id: int, data: dict) -> int:
        """
        Update student
        
        Returns:
            Number of affected rows
        """
        clean_data = validate_student_data(data)
        
        sql = """
            UPDATE students 
            SET FirstName=%s, LastName=%s, DOB=%s, Gender=%s, 
                Address=%s, Phone=%s, Email=%s, EnrollmentYear=%s, Major=%s
            WHERE StudentID=%s
        """
        
        params = (
            clean_data['first_name'],
            clean_data['last_name'],
            clean_data['dob'],
            clean_data['gender'],
            clean_data['address'],
            clean_data['phone'],
            clean_data['email'],
            clean_data['enrollment_year'],
            clean_data['major'],
            student_id
        )
        
        affected = db.execute_update(sql, params)
        logger.info(f"Updated student {student_id}, affected rows: {affected}")
        return affected
    
    @staticmethod
    def delete(student_id: int) -> int:
        """Delete student (cascade delete enrollments)"""
        sql = "DELETE FROM students WHERE StudentID = %s"
        affected = db.execute_update(sql, (student_id,))
        logger.info(f"Deleted student {student_id}")
        return affected
    
    @staticmethod
    def list(limit: int = 50, offset: int = 0, order_by: str = "StudentID") -> List[Dict]:
        """
        Get paginated list of students
        
        Args:
            limit: Max records to return
            offset: Starting position
            order_by: Column to sort by
        """
        sql = f"""
            SELECT * FROM students 
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """
        return db.execute_query(sql, (limit, offset))
    
    @staticmethod
    def search(keyword: str, fields: List[str] = None) -> List[Dict]:
        """
        Search students by keyword
        
        Args:
            keyword: Search term
            fields: Fields to search in (default: FirstName, LastName, Email)
        """
        if fields is None:
            fields = ['FirstName', 'LastName', 'Email']
        
        # Build LIKE conditions
        like_conditions = [f"{field} LIKE %s" for field in fields]
        where_clause = " OR ".join(like_conditions)
        
        sql = f"""
            SELECT * FROM students 
            WHERE {where_clause}
            ORDER BY StudentID
        """
        
        # Create params with % wildcards
        search_term = f"%{keyword}%"
        params = tuple([search_term] * len(fields))
        
        return db.execute_query(sql, params)
    
    @staticmethod
    def count() -> int:
        """Get total number of students"""
        result = db.execute_query("SELECT COUNT(*) as count FROM students", fetch_one=True)
        return result['count'] if result else 0
    
    @staticmethod
    def get_with_avg_grade(min_classes: int = 1) -> List[Dict]:
        """
        Get students with their average grades
        
        Args:
            min_classes: Minimum number of classes enrolled
        """
        sql = """
            SELECT 
                s.StudentID,
                s.FirstName,
                s.LastName,
                ROUND(AVG(e.Grade), 2) AS AvgGrade,
                COUNT(*) AS TotalClasses
            FROM students s
            JOIN enrollments e ON s.StudentID = e.StudentID
            WHERE e.Grade IS NOT NULL
            GROUP BY s.StudentID
            HAVING COUNT(*) >= %s
            ORDER BY AvgGrade DESC
        """
        return db.execute_query(sql, (min_classes,))


# ============================================================
# SUBJECT MODEL
# ============================================================

class SubjectModel(BaseModel):
    """Model for subjects table"""
    
    @staticmethod
    def create(data: dict) -> str:
        """Create new subject, returns SubjectCode"""
        clean_data = validate_subject_data(data)
        
        sql = "INSERT INTO subjects (SubjectCode, SubjectName, Credits) VALUES (%s, %s, %s)"
        params = (clean_data['code'], clean_data['name'], clean_data['credits'])
        
        db.execute_update(sql, params)
        logger.info(f"Created subject: {clean_data['code']}")
        return clean_data['code']
    
    @staticmethod
    def get_by_code(code: str) -> Optional[Dict]:
        """Get subject by code"""
        sql = "SELECT * FROM subjects WHERE SubjectCode = %s"
        return db.execute_query(sql, (code,), fetch_one=True)
    
    @staticmethod
    def update(code: str, data: dict) -> int:
        """Update subject"""
        sql = "UPDATE subjects SET SubjectName=%s, Credits=%s WHERE SubjectCode=%s"
        params = (data['name'], data['credits'], code)
        return db.execute_update(sql, params)
    
    @staticmethod
    def delete(code: str) -> int:
        """Delete subject"""
        sql = "DELETE FROM subjects WHERE SubjectCode = %s"
        return db.execute_update(sql, (code,))
    
    @staticmethod
    def list() -> List[Dict]:
        """Get all subjects"""
        return db.execute_query("SELECT * FROM subjects ORDER BY SubjectCode")
    
    @staticmethod
    def count() -> int:
        """Get total subjects"""
        result = db.execute_query("SELECT COUNT(*) as count FROM subjects", fetch_one=True)
        return result['count'] if result else 0


# ============================================================
# LECTURER MODEL
# ============================================================

class LecturerModel(BaseModel):
    """Model for lecturers table"""
    
    @staticmethod
    def create(data: dict) -> int:
        """Create new lecturer, returns LecturerID"""
        first_name = Validators.validate_required(data['first_name'], 'First Name')
        last_name = Validators.validate_required(data['last_name'], 'Last Name')
        
        email = data.get('email', '').strip()
        if email:
            email = Validators.validate_email(email)
        
        office = data.get('office', '').strip()
        
        sql = """
            INSERT INTO lecturers (LecturerFirstName, LecturerLastName, LecturerEmail, Office)
            VALUES (%s, %s, %s, %s)
        """
        params = (first_name, last_name, email, office)
        
        with db.get_cursor(dictionary=False) as cursor:
            cursor.execute(sql, params)
            lecturer_id = cursor.lastrowid
            logger.info(f"Created lecturer ID: {lecturer_id}")
            return lecturer_id
    
    @staticmethod
    def get_by_id(lecturer_id: int) -> Optional[Dict]:
        """Get lecturer by ID"""
        sql = "SELECT * FROM lecturers WHERE LecturerID = %s"
        return db.execute_query(sql, (lecturer_id,), fetch_one=True)
    
    @staticmethod
    def update(lecturer_id: int, data: dict) -> int:
        """Update lecturer"""
        sql = """
            UPDATE lecturers 
            SET LecturerFirstName=%s, LecturerLastName=%s, LecturerEmail=%s, Office=%s
            WHERE LecturerID=%s
        """
        params = (
            data['first_name'], 
            data['last_name'], 
            data.get('email'), 
            data.get('office'),
            lecturer_id
        )
        return db.execute_update(sql, params)
    
    @staticmethod
    def delete(lecturer_id: int) -> int:
        """Delete lecturer"""
        sql = "DELETE FROM lecturers WHERE LecturerID = %s"
        return db.execute_update(sql, (lecturer_id,))
    
    @staticmethod
    def list() -> List[Dict]:
        """Get all lecturers"""
        return db.execute_query("SELECT * FROM lecturers ORDER BY LecturerID")
    
    @staticmethod
    def get_with_classes(lecturer_id: int) -> List[Dict]:
        """Get lecturer's classes"""
        sql = """
            SELECT c.*, s.SubjectName
            FROM classes c
            JOIN subjects s ON c.SubjectCode = s.SubjectCode
            WHERE c.LecturerID = %s
            ORDER BY c.Year DESC, c.Semester
        """
        return db.execute_query(sql, (lecturer_id,))


# ============================================================
# CLASS MODEL
# ============================================================

class ClassModel(BaseModel):
    """Model for classes table"""
    
    @staticmethod
    def create(data: dict) -> int:
        """Create new class, returns ClassID"""
        subject_code = Validators.validate_required(data['subject_code'], 'Subject Code')
        semester = Validators.validate_semester(data['semester'])
        year = Validators.validate_year(data['year'])
        
        lecturer_id = data.get('lecturer_id')
        class_name = data.get('class_name', '').strip()
        max_capacity = Validators.validate_capacity(data.get('max_capacity', 60))
        
        sql = """
            INSERT INTO classes
            (SubjectCode, LecturerID, ClassName, Semester, Year, MaxCapacity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (subject_code, lecturer_id, class_name, semester, year, max_capacity)
        
        with db.get_cursor(dictionary=False) as cursor:
            cursor.execute(sql, params)
            class_id = cursor.lastrowid
            logger.info(f"Created class ID: {class_id}")
            return class_id
    
    @staticmethod
    def get_by_id(class_id: int) -> Optional[Dict]:
        """Get class by ID with subject and lecturer info"""
        sql = """
            SELECT c.*, s.SubjectName, s.Credits,
                   l.LecturerFirstName, l.LecturerLastName
            FROM classes c
            JOIN subjects s ON c.SubjectCode = s.SubjectCode
            LEFT JOIN lecturers l ON c.LecturerID = l.LecturerID
            WHERE c.ClassID = %s
        """
        return db.execute_query(sql, (class_id,), fetch_one=True)
    
    @staticmethod
    def update(class_id: int, data: dict) -> int:
        """Update class"""
        sql = """
            UPDATE classes
            SET SubjectCode=%s, LecturerID=%s, ClassName=%s, 
                Semester=%s, Year=%s, MaxCapacity=%s
            WHERE ClassID=%s
        """
        params = (
            data['subject_code'],
            data.get('lecturer_id'),
            data.get('class_name'),
            data['semester'],
            data['year'],
            data.get('max_capacity', 60),
            class_id
        )
        return db.execute_update(sql, params)
    
    @staticmethod
    def delete(class_id: int) -> int:
        """Delete class"""
        sql = "DELETE FROM classes WHERE ClassID = %s"
        return db.execute_update(sql, (class_id,))
    
    @staticmethod
    def list(year: int = None, semester: str = None) -> List[Dict]:
        """Get classes with optional filters"""
        sql = """
            SELECT c.*, s.SubjectName,
                   l.LecturerFirstName, l.LecturerLastName,
                   COUNT(e.StudentID) as EnrolledCount
            FROM classes c
            JOIN subjects s ON c.SubjectCode = s.SubjectCode
            LEFT JOIN lecturers l ON c.LecturerID = l.LecturerID
            LEFT JOIN enrollments e ON c.ClassID = e.ClassID
        """
        
        conditions = []
        params = []
        
        if year:
            conditions.append("c.Year = %s")
            params.append(year)
        if semester:
            conditions.append("c.Semester = %s")
            params.append(semester)
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " GROUP BY c.ClassID ORDER BY c.Year DESC, c.Semester"
        
        return db.execute_query(sql, tuple(params))
    
    @staticmethod
    def get_enrollment_count(class_id: int) -> int:
        """Get number of students enrolled in class"""
        sql = "SELECT COUNT(*) as count FROM enrollments WHERE ClassID = %s"
        result = db.execute_query(sql, (class_id,), fetch_one=True)
        return result['count'] if result else 0


# ============================================================
# ENROLLMENT MODEL
# ============================================================

class EnrollmentModel(BaseModel):
    """Model for enrollments table (composite PK)"""
    
    @staticmethod
    def create(data: dict) -> bool:
        """
        Create enrollment
        
        Returns:
            True if successful
        """
        clean_data = validate_enrollment_data(data)
        
        # Check if already enrolled
        if EnrollmentModel.exists(clean_data['student_id'], clean_data['class_id']):
            raise ValidationError("Student already enrolled in this class")
        
        sql = """
            INSERT INTO enrollments (StudentID, ClassID, Grade, GradeLetter, Note)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            clean_data['student_id'],
            clean_data['class_id'],
            clean_data.get('grade'),
            clean_data.get('grade_letter'),
            clean_data.get('note')
        )
        
        db.execute_update(sql, params)
        logger.info(f"Created enrollment: Student {clean_data['student_id']} -> Class {clean_data['class_id']}")
        return True
    
    @staticmethod
    def exists(student_id: int, class_id: int) -> bool:
        """Check if enrollment exists"""
        sql = "SELECT 1 FROM enrollments WHERE StudentID=%s AND ClassID=%s"
        result = db.execute_query(sql, (student_id, class_id), fetch_one=True)
        return result is not None
    
    @staticmethod
    def update(student_id: int, class_id: int, data: dict) -> int:
        """Update enrollment (usually grade)"""
        sql = """
            UPDATE enrollments
            SET Grade=%s, GradeLetter=%s, Note=%s
            WHERE StudentID=%s AND ClassID=%s
        """
        params = (
            data.get('grade'),
            data.get('grade_letter'),
            data.get('note'),
            student_id,
            class_id
        )
        return db.execute_update(sql, params)
    
    @staticmethod
    def delete(student_id: int, class_id: int) -> int:
        """Delete enrollment"""
        sql = "DELETE FROM enrollments WHERE StudentID=%s AND ClassID=%s"
        return db.execute_update(sql, (student_id, class_id))
    
    @staticmethod
    def get_by_student(student_id: int) -> List[Dict]:
        """Get all enrollments for a student"""
        sql = """
            SELECT e.*, c.ClassName, c.Semester, c.Year,
                   s.SubjectName, s.Credits
            FROM enrollments e
            JOIN classes c ON e.ClassID = c.ClassID
            JOIN subjects s ON c.SubjectCode = s.SubjectCode
            WHERE e.StudentID = %s
            ORDER BY c.Year DESC, c.Semester
        """
        return db.execute_query(sql, (student_id,))
    
    @staticmethod
    def get_by_class(class_id: int) -> List[Dict]:
        """Get all enrollments for a class"""
        sql = """
            SELECT e.*, s.FirstName, s.LastName, s.Email
            FROM enrollments e
            JOIN students s ON e.StudentID = s.StudentID
            WHERE e.ClassID = %s
            ORDER BY s.LastName, s.FirstName
        """
        return db.execute_query(sql, (class_id,))


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    print("Testing models...")
    
    # Test student count
    count = StudentModel.count()
    print(f"Total students: {count}")
    
    # Test subject list
    subjects = SubjectModel.list()
    print(f"Total subjects: {len(subjects)}")
    
    print("Models tested successfully!")