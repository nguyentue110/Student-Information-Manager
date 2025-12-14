from app.db.connection import get_connection


class ClassModel:

    @staticmethod
    def create(data):
        sql = """
            INSERT INTO classes
            (SubjectCode, LecturerID, ClassName, Semester, Year, MaxCapacity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        params = (
            data["subject_code"],
            data.get("lecturer_id"),
            data.get("class_name"),
            data["semester"],
            data["year"],
            data.get("max_capacity", 60)
        )

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        class_id = cur.lastrowid
        cur.close()
        conn.close()

        return class_id

    @staticmethod
    def get_by_id(class_id):
        sql = "SELECT * FROM classes WHERE ClassID = %s"

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (class_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        return row

    @staticmethod
    def list_all():
        sql = "SELECT * FROM classes ORDER BY Year DESC, Semester"

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return rows

    @staticmethod
    def delete(class_id):
        sql = "DELETE FROM classes WHERE ClassID = %s"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (class_id,))
        affected = cur.rowcount
        cur.close()
        conn.close()

        return affected
