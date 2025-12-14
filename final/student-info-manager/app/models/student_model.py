from db.connection import get_connection

class StudentModel:

    @staticmethod
    def create(student):
        sql = """
            INSERT INTO students
            (FirstName, LastName, DOB, Gender, Address, Phone, Email, EnrollmentYear, Major)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        params = (
            student["first_name"],
            student["last_name"],
            student["dob"],
            student["gender"],
            student.get("address"),
            student.get("phone"),
            student.get("email"),
            student["enrollment_year"],
            student.get("major"),
        )

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        student_id = cur.lastrowid
        cur.close()
        conn.close()
        return student_id

    @staticmethod
    def get_by_id(student_id):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM students WHERE StudentID = %s",
            (student_id,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    @staticmethod
    def update(student_id, data):
        fields = ", ".join(f"{k} = %s" for k in data)
        params = list(data.values()) + [student_id]

        sql = f"UPDATE students SET {fields} WHERE StudentID = %s"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        affected = cur.rowcount
        cur.close()
        conn.close()
        return affected

    @staticmethod
    def delete(student_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM students WHERE StudentID = %s",
            (student_id,)
        )
        affected = cur.rowcount
        cur.close()
        conn.close()
        return affected

    @staticmethod
    def list(limit=50, offset=0):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM students ORDER BY StudentID LIMIT %s OFFSET %s",
            (limit, offset)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
