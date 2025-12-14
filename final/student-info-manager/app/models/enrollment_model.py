from app.db.connection import get_connection

class EnrollmentModel:
    @staticmethod
    def create(student_id, class_id, grade=None, grade_letter=None, note=None):
        sql = "INSERT INTO enrollments (StudentID, ClassID, Grade, GradeLetter, Note) VALUES (%s,%s,%s,%s,%s)"
        params = (student_id, class_id, grade, grade_letter, note)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def exists(student_id, class_id):
        sql = "SELECT 1 FROM enrollments WHERE StudentID=%s AND ClassID=%s"
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, (student_id, class_id))
            return cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()
