from app.models.student_model import StudentModel
from app.models.class_model import ClassModel
from app.services.enrollment_service import EnrollmentService
import uuid

email = f"demo_{uuid.uuid4()}@example.com"

sid = StudentModel.create({
    "first_name": "Demo",
    "last_name": "Student",
    "dob": "2002-01-01",
    "gender": "M",
    "address": "Hanoi",
    "phone": "0900000000",
    "email": email,
    "enrollment_year": 2024,
    "major": "Computer Science"
})

print("Created student ID:", sid)

cls = ClassModel.get_by_id(1)
print("Class:", cls)

EnrollmentService.enroll(
    sid,
    1,
    grade=8.5,
    grade_letter="B",
    note="Good"
)

print("Enrollment success")