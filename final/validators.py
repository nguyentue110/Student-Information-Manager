import re
from datetime import datetime, date
from db_connection import db # <--- ĐÃ THÊM: Cần thiết để kiểm tra UNIQUE/Composite PK


class ValidationError(Exception):
    """Ngoại lệ tùy chỉnh được raise khi validation thất bại."""
    pass


class Validators:
    
    # --------------------------------------------------------------------------------
    # CÁC PHƯƠNG THỨC VALIDATION CHUNG VÀ CSDL
    # --------------------------------------------------------------------------------
    @staticmethod
    def is_empty(value, field_name):
        """Kiểm tra nếu giá trị rỗng (dành cho các trường NOT NULL)."""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            raise ValidationError(f"{field_name} là trường bắt buộc và không được để trống.")

    @staticmethod
    def check_unique(table, column, value, current_id=None, id_column=None):
        """Kiểm tra xem giá trị có bị trùng lặp trong CSDL hay không (UNIQUE constraint)."""
        if not value:
            return 
            
        id_col = id_column if id_column else f"{table}ID"
        
        query = f"SELECT 1 FROM {table} WHERE {column} = %s"
        params = [value]
        
        # Loại trừ bản ghi hiện tại khi UPDATE
        if current_id is not None:
            query += f" AND {id_col} != %s"
            params.append(current_id)
            
        exists = db.execute_query(query, params, fetch_one=True)
        
        if exists:
            raise ValidationError(f"{column} '{value}' đã tồn tại trong hệ thống. Vui lòng nhập giá trị khác.")

    # --------------------------------------------------------------------------------
    # VALIDATION CỤ THỂ CHO TỪNG TRƯỜNG
    # --------------------------------------------------------------------------------
    @staticmethod
    def validate_full_name(full_name: str) -> tuple:
        """Kiểm tra tên và tách thành FirstName, LastName."""
        Validators.is_empty(full_name, "Full Name")
        if " " not in full_name.strip():
            raise ValidationError("Full name must contain first and last name")

        parts = full_name.strip().split()
        first_name = parts[0]
        last_name = " ".join(parts[1:])
        return first_name, last_name

    @staticmethod
    def validate_email(email: str, table: str, current_id: int = None) -> str:
        """Kiểm tra định dạng Email và UNIQUE."""
        Validators.is_empty(email, "Email") # Email là UNIQUE và NOT NULL (chúng ta giả định NOT NULL ở đây)
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")
            
        # Kiểm tra UNIQUE trong CSDL
        id_col = "StudentID" if table == 'students' else "LecturerID"
        Validators.check_unique(table, 'Email', email, current_id, id_col)
        return email

    @staticmethod
    def validate_dob(dob: str) -> str:
        """Kiểm tra định dạng ngày sinh YYYY-MM-DD và giới hạn tuổi."""
        Validators.is_empty(dob, "Birthdate")
        try:
            dt = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("DOB must be YYYY-MM-DD")

        age = date.today().year - dt.year
        if age < 15 or age > 80:
            raise ValidationError("Age must be between 15 and 80 years old.")
        return dob

    @staticmethod
    def validate_gender(gender: str) -> str:
        """Kiểm tra Gender và chuyển về định dạng ENUM ('M','F','O')."""
        Validators.is_empty(gender, "Gender")
        
        # Chuyển đổi từ chuỗi đầy đủ sang ENUM
        gender_map = {"Male": "M", "Female": "F", "Other": "O", "M": "M", "F": "F", "O": "O"}
        
        if gender not in gender_map and gender not in gender_map.values():
             raise ValidationError("Gender must be Male, Female, or Other.")
             
        return gender_map.get(gender, gender) # Trả về M/F/O

    @staticmethod
    def validate_year(val: int) -> int:
        """Kiểm tra năm trong phạm vi hợp lệ."""
        Validators.is_empty(val, "Year")
        try:
            year = int(val)
        except ValueError:
            raise ValidationError("Year must be a number.")
            
        if year < 1990 or year > datetime.now().year + 5: # Cho phép 5 năm trong tương lai
            raise ValidationError("Invalid year range.")
        return year

    @staticmethod
    def validate_subject_code(code: str, is_new: bool = False) -> str:
        """Kiểm tra định dạng Subject Code (PRIMARY KEY) và UNIQUE."""
        Validators.is_empty(code, "Subject Code")
        code = code.strip().upper()
        
        # Định dạng: LETTERS + NUMBERS (e.g., CS101)
        if not re.match(r'^[A-Z]+\d+$', code):
            raise ValidationError("Subject code must be LETTERS+NUMBERS (e.g., CS101)")
            
        # Nếu là thêm mới, kiểm tra UNIQUE
        if is_new:
            Validators.check_unique('subjects', 'SubjectCode', code, id_column='SubjectCode')
            
        return code

    @staticmethod
    def validate_grade(grade: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
        """Kiểm tra Grade (0-10) và làm tròn."""
        if grade is None or str(grade).strip() == "":
            return None # Grade có thể là NULL trong CSDL
            
        try:
            grade = float(grade)
        except ValueError:
            raise ValidationError("Grade must be a number.")

        if grade < min_val or grade > max_val:
            raise ValidationError(f"Grade must be between {min_val} and {max_val}")

        return round(grade, 2)
    
    # --------------------------------------------------------------------------------
    # VALIDATION CẤP ĐỘ DATASET
    # --------------------------------------------------------------------------------

    @staticmethod # <--- ĐÃ THÊM: STATICMETHOD
    def validate_student_data(data: dict, student_id: int = None) -> dict:
        v = Validators

        # Về mặt GUI, bạn nên tách FirstName và LastName ngay trong Form
        # nhưng nếu Form yêu cầu Full Name, sử dụng hàm tách
        # Tuy nhiên, CSDL của bạn có FirstName và LastName riêng biệt
        # Tôi sẽ giả định data['FirstName'] và data['LastName'] đã được cung cấp
        
        # Trường hợp 1: Form cung cấp Full Name (như trong mã gốc của bạn)
        # first_name, last_name = v.validate_full_name(data["full_name"]) 
        
        # Trường hợp 2: Form cung cấp First Name và Last Name riêng
        v.is_empty(data.get("FirstName"), "First Name")
        v.is_empty(data.get("LastName"), "Last Name")
        
        email = v.validate_email(data["Email"], 'students', student_id)
        dob = v.validate_dob(data["DOB"])
        gender = v.validate_gender(data["Gender"])
        enrollment_year = v.validate_year(data["EnrollmentYear"])

        return {
            "FirstName": data["FirstName"],
            "LastName": data["LastName"],
            "Email": email,
            "DOB": dob,
            "Gender": gender,
            "EnrollmentYear": enrollment_year,
            "Address": data.get("Address"),
            "Phone": data.get("Phone"),
            "Major": data.get("Major")
        }

    @staticmethod # <--- ĐÃ THÊM: STATICMETHOD
    def validate_subject_data(data: dict, is_new: bool = False) -> dict:
        v = Validators

        subject_code = v.validate_subject_code(data["SubjectCode"], is_new=is_new) # Kiểm tra UNIQUE khi thêm mới

        # Subject name must not be empty
        name = data.get("SubjectName", "").strip()
        v.is_empty(name, "Subject Name")

        # Credits must be integer from 1–10 (theo schema.sql)
        credits = data.get("Credits")
        v.is_empty(credits, "Credits")

        try:
            credits = int(credits)
        except ValueError:
            raise ValidationError("Credits must be an integer")

        # CHECK (Credits > 0)
        if credits <= 0 or credits > 10: 
            raise ValidationError("Credits must be a positive integer (1-10)")

        return {
            "SubjectCode": subject_code,
            "SubjectName": name,
            "Credits": credits
        }

    @staticmethod # <--- ĐÃ THÊM: STATICMETHOD
    def validate_enrollment_data(data: dict, is_new: bool = False) -> dict:
        v = Validators

        student_id = data.get("StudentID")
        class_id = data.get("ClassID")

        # StudentID và ClassID là khóa chính kép, không được rỗng
        v.is_empty(student_id, "Student ID")
        v.is_empty(class_id, "Class ID")
        
        # Grade optional (CHECK 0-10)
        grade = v.validate_grade(data.get("Grade"))

        # Kiểm tra Composite PK UNIQUE (Chỉ cần khi thêm mới)
        if is_new:
            check_query = "SELECT 1 FROM enrollments WHERE StudentID=%s AND ClassID=%s"
            exists = db.execute_query(check_query, (student_id, class_id), fetch_one=True)
            if exists:
                raise ValidationError("Sinh viên đã đăng ký vào lớp học này!")

        # Grade Letter có thể là NULL
        grade_letter = data.get("GradeLetter")
        note = data.get("Note")
        
        return {
            "StudentID": student_id,
            "ClassID": class_id,
            "Grade": grade,
            "GradeLetter": grade_letter,
            "Note": note
        }