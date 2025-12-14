from app.db.connection import get_connection

class SubjectModel:
    @staticmethod
    def create(subject):
        sql = "INSERT INTO subjects (SubjectCode, SubjectName, Credits) VALUES (%s,%s,%s)"
        params = (subject['code'], subject['name'], subject['credits'])
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_code(code):
        sql = "SELECT * FROM subjects WHERE SubjectCode = %s"
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, (code,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def list_all():
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM subjects ORDER BY SubjectCode")
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()
