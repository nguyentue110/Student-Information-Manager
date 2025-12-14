from app.db.connection import get_connection

class LecturerModel:
    @staticmethod
    def create(data):
        sql = "INSERT INTO lecturers (LecturerFirstName, LecturerLastName, LecturerEmail, Office) VALUES (%s,%s,%s,%s)"
        params = (data['first_name'], data['last_name'], data.get('email'), data.get('office'))
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_id(lid):
        sql = "SELECT * FROM lecturers WHERE LecturerID = %s"
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, (lid,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()
