from app.models.enrollment_model import EnrollmentModel
from app.models.student_model import StudentModel
from app.models.class_model import ClassModel

class EnrollmentService:
    @staticmethod
    def enroll(student_id, class_id, grade=None, grade_letter=None, note=None):
        # validate student
        student = StudentModel.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        # validate class
        _class = ClassModel.get_by_id(class_id)
        if not _class:
            raise ValueError("Class not found")

        # check duplicate
        if EnrollmentModel.exists(student_id, class_id):
            raise ValueError("Student already enrolled in this class")

        # optional: validate grade range if provided
        if grade is not None:
            if not (0 <= float(grade) <= 10):
                raise ValueError("Grade must be between 0 and 10")

        EnrollmentModel.create(student_id, class_id, grade, grade_letter, note)
        return True
