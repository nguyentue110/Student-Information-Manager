# query_models.py - Models cho các yêu cầu query đặc biệt
"""
GIẢI THÍCH:
Implement 4 queries theo yêu cầu:
1. INNER JOIN: Student name and grade per subject
2. LEFT JOIN: All students with/without grades
3. Multi-table JOIN: Student-Subject-Grade-Lecturer (3+ tables)
4. Above global average: Students với avg grade > global average

Pattern: Static methods trả về list of dicts
"""

from db_connection import db
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class QueryModels:
    """
    Class chứa các query phức tạp theo yêu cầu
    
    YÊU CẦU:
    - Mỗi query phải có export CSV functionality
    - Show results in GUI table
    - Sorting và search support
    """
    
    # ============================================================
    # QUERY 1: INNER JOIN - Student name and grade per subject
    # ============================================================
    
    @staticmethod
    def query_student_grades_by_subject(subject_code: Optional[str] = None) -> List[Dict]:
        """
        INNER JOIN query: Student name, subject, and grade
        
        GIẢI THÍCH:
        - INNER JOIN chỉ lấy students có enrollments
        - Join qua: enrollments -> students, classes, subjects
        - Optional filter by subject code
        
        Args:
            subject_code: Optional subject code để filter
        
        Returns:
            List of dicts với columns:
            - StudentID, FirstName, LastName
            - SubjectCode, SubjectName
            - ClassID, ClassName, Semester, Year
            - Grade, GradeLetter
        
        USE CASE: Xem điểm của students theo môn học
        """
        sql = """
            SELECT 
                s.StudentID,
                s.FirstName,
                s.LastName,
                sub.SubjectCode,
                sub.SubjectName,
                c.ClassID,
                c.ClassName,
                c.Semester,
                c.Year,
                e.Grade,
                e.GradeLetter
            FROM enrollments e
            INNER JOIN students s ON e.StudentID = s.StudentID
            INNER JOIN classes c ON e.ClassID = c.ClassID
            INNER JOIN subjects sub ON c.SubjectCode = sub.SubjectCode
        """
        
        params = ()
        if subject_code:
            sql += " WHERE sub.SubjectCode = %s"
            params = (subject_code,)
        
        sql += " ORDER BY sub.SubjectName, s.LastName, s.FirstName"
        
        results = db.execute_query(sql, params)
        logger.info(f"Query 1 (INNER JOIN) returned {len(results)} rows")
        return results
    
    @staticmethod
    def get_grade_distribution():
        """
        Trả về số lượng sinh viên theo khoảng điểm:
        - 0–5
        - 5–7
        - 7–8.5
        - 8.5–10
        """

        sql = """
            SELECT 
                CASE
                    WHEN Grade < 5 THEN '0 - 5'
                    WHEN Grade < 7 THEN '5 - 7'
                    WHEN Grade < 8.5 THEN '7 - 8.5'
                    ELSE '8.5 - 10'
                END AS GradeRange,
                COUNT(*) AS Count
            FROM enrollments
            WHERE Grade IS NOT NULL
            GROUP BY GradeRange
            ORDER BY GradeRange
        """

        return db.execute_query(sql)
    # ============================================================
    # QUERY 2: LEFT JOIN - All students with/without grades
    # ============================================================
    
    @staticmethod
    def query_all_students_with_grades() -> List[Dict]:
        """
        LEFT JOIN query: List all students including those without grades
        
        GIẢI THÍCH:
        - LEFT JOIN đảm bảo tất cả students đều hiển thị
        - Students chưa enroll sẽ có NULL cho class/grade fields
        - Useful để identify students chưa đăng ký môn nào
        
        Returns:
            List of dicts với columns:
            - StudentID, FirstName, LastName
            - ClassID, ClassName (NULL nếu chưa enroll)
            - Grade (NULL nếu chưa có điểm)
            - TotalEnrollments (số môn đã đăng ký)
        
        USE CASE: 
        - Identify students chưa đăng ký môn
        - Overview toàn bộ students
        """
        sql = """
            SELECT 
                s.StudentID,
                s.FirstName,
                s.LastName,
                s.Email,
                s.Major,
                c.ClassID,
                c.ClassName,
                c.Semester,
                c.Year,
                e.Grade,
                e.GradeLetter,
                COUNT(e.ClassID) OVER (PARTITION BY s.StudentID) as TotalEnrollments
            FROM students s
            LEFT JOIN enrollments e ON s.StudentID = e.StudentID
            LEFT JOIN classes c ON e.ClassID = c.ClassID
            ORDER BY s.StudentID, c.Year DESC, c.Semester
        """
        
        results = db.execute_query(sql)
        logger.info(f"Query 2 (LEFT JOIN) returned {len(results)} rows")
        return results
    
    # ============================================================
    # QUERY 3: Multi-table JOIN - Student-Subject-Grade-Lecturer
    # ============================================================
    
    @staticmethod
    def query_complete_enrollment_info(
        student_id: Optional[int] = None,
        subject_code: Optional[str] = None,
        lecturer_id: Optional[int] = None,
        semester: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Dict]:
        """
        Multi-table JOIN: Complete enrollment information
        
        GIẢI THÍCH:
        - Join 5 tables: students, enrollments, classes, subjects, lecturers
        - Provides complete picture của enrollment
        - Multiple optional filters
        
        Args:
            student_id: Filter by student
            subject_code: Filter by subject
            lecturer_id: Filter by lecturer
            semester: Filter by semester
            year: Filter by year
        
        Returns:
            List of dicts với columns:
            - Student info: StudentID, FirstName, LastName, Email
            - Subject info: SubjectCode, SubjectName, Credits
            - Class info: ClassID, ClassName, Semester, Year
            - Lecturer info: LecturerID, LecturerName
            - Grade info: Grade, GradeLetter
        
        USE CASE:
        - Comprehensive enrollment reports
        - Filter by multiple criteria
        - Academic records
        """
        sql = """
            SELECT 
                -- Student info
                s.StudentID,
                s.FirstName as StudentFirstName,
                s.LastName as StudentLastName,
                s.Email as StudentEmail,
                s.Major,
                
                -- Subject info
                sub.SubjectCode,
                sub.SubjectName,
                sub.Credits,
                
                -- Class info
                c.ClassID,
                c.ClassName,
                c.Semester,
                c.Year,
                
                -- Lecturer info
                l.LecturerID,
                l.LecturerFirstName,
                l.LecturerLastName,
                CONCAT(l.LecturerFirstName, ' ', l.LecturerLastName) as LecturerName,
                l.Office,
                
                -- Grade info
                e.Grade,
                e.GradeLetter,
                e.Note
                
            FROM enrollments e
            INNER JOIN students s ON e.StudentID = s.StudentID
            INNER JOIN classes c ON e.ClassID = c.ClassID
            INNER JOIN subjects sub ON c.SubjectCode = sub.SubjectCode
            LEFT JOIN lecturers l ON c.LecturerID = l.LecturerID
            WHERE 1=1
        """
        
        conditions = []
        params = []
        
        if student_id:
            conditions.append("s.StudentID = %s")
            params.append(student_id)
        
        if subject_code:
            conditions.append("sub.SubjectCode = %s")
            params.append(subject_code)
        
        if lecturer_id:
            conditions.append("l.LecturerID = %s")
            params.append(lecturer_id)
        
        if semester:
            conditions.append("c.Semester = %s")
            params.append(semester)
        
        if year:
            conditions.append("c.Year = %s")
            params.append(year)
        
        if conditions:
            sql += " AND " + " AND ".join(conditions)
        
        sql += " ORDER BY c.Year DESC, c.Semester, sub.SubjectName, s.LastName"
        
        results = db.execute_query(sql, tuple(params))
        logger.info(f"Query 3 (Multi-table JOIN) returned {len(results)} rows")
        return results
    
    # ============================================================
    # QUERY 4: Above Global Average
    # ============================================================
    
    @staticmethod
    def query_students_above_average(min_classes: int = 3) -> List[Dict]:
        """
        Complex query: Students với average grade > global average
        
        GIẢI THÍCH:
        - Calculate global average từ tất cả grades
        - Calculate individual student averages
        - Compare và filter students above global avg
        - Require minimum số classes để fair comparison
        
        ALGORITHM:
        1. Subquery: Calculate global average
        2. Main query: Calculate per-student average
        3. HAVING clause: Filter students > global avg
        
        Args:
            min_classes: Minimum số classes để qualify (default: 3)
        
        Returns:
            List of dicts với columns:
            - StudentID, FirstName, LastName
            - StudentAvg (average grade)
            - GlobalAvg (overall average)
            - TotalClasses (số môn đã có điểm)
            - DifferenceFromAvg (chênh lệch so với global avg)
        
        USE CASE:
        - Identify top performers
        - Compare individual vs overall performance
        - Academic ranking
        """
        sql = """
            WITH GlobalAvg AS (
                SELECT ROUND(AVG(Grade), 2) as AvgGrade
                FROM enrollments
                WHERE Grade IS NOT NULL
            )
            SELECT 
                s.StudentID,
                s.FirstName,
                s.LastName,
                s.Email,
                s.Major,
                ROUND(AVG(e.Grade), 2) AS StudentAvg,
                (SELECT AvgGrade FROM GlobalAvg) AS GlobalAvg,
                COUNT(*) AS TotalClasses,
                ROUND(AVG(e.Grade) - (SELECT AvgGrade FROM GlobalAvg), 2) AS DifferenceFromAvg
            FROM students s
            JOIN enrollments e ON s.StudentID = e.StudentID
            WHERE e.Grade IS NOT NULL
            GROUP BY s.StudentID
            HAVING 
                COUNT(*) >= %s
                AND AVG(e.Grade) > (SELECT AvgGrade FROM GlobalAvg)
            ORDER BY StudentAvg DESC, TotalClasses DESC
        """
        
        results = db.execute_query(sql, (min_classes,))
        logger.info(f"Query 4 (Above Average) returned {len(results)} rows")
        return results
    
    # ============================================================
    # BONUS QUERIES - Additional useful queries
    # ============================================================
    
# Trong file query_models.py

    @staticmethod
    def query_top_students(limit: int = 10, min_classes: int = 1) -> List[Dict]:
        """
        Get top N students by average grade
        
        GIẢI THÍCH:
        - Tính điểm trung bình (AvgGrade) của mỗi sinh viên.
        - Chỉ xét những sinh viên có điểm ít nhất min_classes môn học (mặc định là 1).
        
        Args:
            limit: Số lượng sinh viên top N muốn hiển thị (mặc định 10).
            min_classes: Số môn tối thiểu sinh viên phải có điểm (mặc định 1).

        Returns:
            List of dicts: StudentID, FirstName, LastName, AvgGrade, TotalClasses, MinGrade, MaxGrade
        
        USE CASE: Dashboard KPI, leaderboard
        """
        sql = """
            SELECT 
                s.StudentID,
                s.FirstName,
                s.LastName,
                ROUND(AVG(e.Grade), 2) AS AvgGrade,
                COUNT(*) AS TotalClasses,
                MIN(e.Grade) AS MinGrade,
                MAX(e.Grade) AS MaxGrade
            FROM students s
            JOIN enrollments e ON s.StudentID = e.StudentID
            WHERE e.Grade IS NOT NULL
            GROUP BY s.StudentID
            HAVING COUNT(*) >= %s
            ORDER BY AvgGrade DESC
            LIMIT %s
        """
        
        # db.execute_query sẽ thực thi SQL và thay thế %s bằng các tham số
        return db.execute_query(sql, (min_classes, limit))
    
    @staticmethod
    def query_grade_distribution() -> List[Dict]:
        """
        Get grade distribution for dashboard charts
        
        Returns:
            List with grade ranges and counts
        """
        sql = """
            SELECT 
                CASE 
                    WHEN Grade >= 9 THEN 'A (9-10)'
                    WHEN Grade >= 8 THEN 'B (8-9)'
                    WHEN Grade >= 7 THEN 'C (7-8)'
                    WHEN Grade >= 6 THEN 'D (6-7)'
                    WHEN Grade >= 5 THEN 'E (5-6)'
                    ELSE 'F (0-5)'
                END AS GradeRange,
                COUNT(*) AS Count,
                ROUND(AVG(Grade), 2) AS AvgInRange
            FROM enrollments
            WHERE Grade IS NOT NULL
            GROUP BY GradeRange
            ORDER BY 
                CASE GradeRange
                    WHEN 'A (9-10)' THEN 1
                    WHEN 'B (8-9)' THEN 2
                    WHEN 'C (7-8)' THEN 3
                    WHEN 'D (6-7)' THEN 4
                    WHEN 'E (5-6)' THEN 5
                    ELSE 6
                END
        """
        
        return db.execute_query(sql)
    
    @staticmethod
    def query_subject_performance() -> List[Dict]:
        """
        Get average grade per subject
        
        USE CASE: Identify difficult/easy subjects
        """
        sql = """
            SELECT 
                sub.SubjectCode,
                sub.SubjectName,
                sub.Credits,
                COUNT(DISTINCT e.StudentID) AS TotalStudents,
                ROUND(AVG(e.Grade), 2) AS AvgGrade,
                MIN(e.Grade) AS MinGrade,
                MAX(e.Grade) AS MaxGrade,
                COUNT(CASE WHEN e.Grade >= 5 THEN 1 END) AS PassCount,
                COUNT(CASE WHEN e.Grade < 5 THEN 1 END) AS FailCount
            FROM subjects sub
            JOIN classes c ON sub.SubjectCode = c.SubjectCode
            JOIN enrollments e ON c.ClassID = e.ClassID
            WHERE e.Grade IS NOT NULL
            GROUP BY sub.SubjectCode
            ORDER BY AvgGrade DESC
        """
        
        return db.execute_query(sql)
    
    @staticmethod
    def query_lecturer_performance() -> List[Dict]:
        """
        Get lecturer teaching stats
        
        USE CASE: Evaluate lecturer effectiveness
        """
        sql = """
            SELECT 
                l.LecturerID,
                CONCAT(l.LecturerFirstName, ' ', l.LecturerLastName) AS LecturerName,
                l.Office,
                COUNT(DISTINCT c.ClassID) AS TotalClasses,
                COUNT(DISTINCT e.StudentID) AS TotalStudents,
                ROUND(AVG(e.Grade), 2) AS AvgGrade,
                COUNT(CASE WHEN e.Grade >= 8 THEN 1 END) AS ExcellentCount
            FROM lecturers l
            JOIN classes c ON l.LecturerID = c.LecturerID
            JOIN enrollments e ON c.ClassID = e.ClassID
            WHERE e.Grade IS NOT NULL
            GROUP BY l.LecturerID
            ORDER BY AvgGrade DESC
        """
        
        return db.execute_query(sql)
    
    # ============================================================
    # DASHBOARD KPI QUERIES
    # ============================================================
    
    @staticmethod
    def get_dashboard_kpis() -> Dict:
        """
        Get all KPIs for dashboard in one efficient call
        
        Returns:
            Dict với keys:
            - total_students
            - total_subjects
            - total_classes
            - total_enrollments
            - avg_grade
            - pass_rate
        """
        sql = """
            SELECT 
                (SELECT COUNT(*) FROM students) AS total_students,
                (SELECT COUNT(*) FROM subjects) AS total_subjects,
                (SELECT COUNT(*) FROM classes) AS total_classes,
                (SELECT COUNT(*) FROM enrollments) AS total_enrollments,
                (SELECT ROUND(AVG(Grade), 2) FROM enrollments WHERE Grade IS NOT NULL) AS avg_grade,
                (SELECT ROUND(
                    100.0 * COUNT(CASE WHEN Grade >= 5 THEN 1 END) / COUNT(*), 
                    2
                ) FROM enrollments WHERE Grade IS NOT NULL) AS pass_rate
        """
        
        result = db.execute_query(sql, fetch_one=True)
        logger.info("Dashboard KPIs fetched")
        return result if result else {}


# ============================================================
# EXPORT UTILITIES
# ============================================================

def export_query_to_csv(data: List[Dict], filename: str) -> bool:
    """
    Export query results to CSV file
    
    Args:
        data: List of dicts from query
        filename: Output filename
    
    Returns:
        True if successful
    """
    import csv
    
    if not data:
        logger.warning("No data to export")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Exported {len(data)} rows to {filename}")
        return True
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return False


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    print("Testing query models...")
    
    # Test Query 1: INNER JOIN
    print("\n1. Testing INNER JOIN query...")
    results = QueryModels.query_student_grades_by_subject()
    print(f"   Found {len(results)} records")
    if results:
        print(f"   Sample: {results[0]}")
    
    # Test Query 2: LEFT JOIN
    print("\n2. Testing LEFT JOIN query...")
    results = QueryModels.query_all_students_with_grades()
    print(f"   Found {len(results)} records")
    
    # Test Query 3: Multi-table JOIN
    print("\n3. Testing Multi-table JOIN query...")
    results = QueryModels.query_complete_enrollment_info()
    print(f"   Found {len(results)} records")
    
    # Test Query 4: Above Average
    print("\n4. Testing Above Average query...")
    results = QueryModels.query_students_above_average()
    print(f"   Found {len(results)} students above average")
    
    # Test Dashboard KPIs
    print("\n5. Testing Dashboard KPIs...")
    kpis = QueryModels.get_dashboard_kpis()
    print(f"   KPIs: {kpis}")
    
    print("\n✓ All query tests completed!")