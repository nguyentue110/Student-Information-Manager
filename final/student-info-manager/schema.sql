-- ============================================================
-- schema.sql (Premium Version)
-- - NOT NULL constraints
-- - UNIQUE emails
-- - ENUM gender
-- - CHECK constraints for Grade
-- - FK constraints with sensible ON DELETE behavior
-- - Composite PK on enrollments (StudentID, ClassID)
-- ============================================================

DROP DATABASE IF EXISTS student_management;
CREATE DATABASE student_management;
USE student_management;

-- ============================================================
-- STUDENTS
-- ============================================================
CREATE TABLE students (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    DOB DATE NOT NULL,
    Gender ENUM('M','F','O') NOT NULL,
    Address VARCHAR(255),
    Phone VARCHAR(20),
    Email VARCHAR(100) UNIQUE,
    EnrollmentYear INT NOT NULL,
    Major VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- LECTURERS
-- ============================================================
CREATE TABLE lecturers (
    LecturerID INT AUTO_INCREMENT PRIMARY KEY,
    LecturerFirstName VARCHAR(100) NOT NULL,
    LecturerLastName VARCHAR(100) NOT NULL,
    LecturerEmail VARCHAR(100) UNIQUE,
    Office VARCHAR(50)
);

-- ============================================================
-- SUBJECTS
-- ============================================================
CREATE TABLE subjects (
    SubjectCode VARCHAR(20) PRIMARY KEY,
    SubjectName VARCHAR(255) NOT NULL,
    Credits INT NOT NULL CHECK (Credits > 0)
);

-- ============================================================
-- CLASSES
-- ============================================================
CREATE TABLE classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    SubjectCode VARCHAR(20) NOT NULL,
    LecturerID INT,
    ClassName VARCHAR(100),
    Semester VARCHAR(10) NOT NULL,
    Year INT NOT NULL,
    MaxCapacity INT DEFAULT 60,
    CONSTRAINT fk_classes_subject
        FOREIGN KEY (SubjectCode) REFERENCES subjects(SubjectCode)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_classes_lecturer
        FOREIGN KEY (LecturerID) REFERENCES lecturers(LecturerID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ============================================================
-- ENROLLMENTS (Composite Primary Key)
-- ============================================================
CREATE TABLE enrollments (
    StudentID INT NOT NULL,
    ClassID INT NOT NULL,
    Grade DECIMAL(4,2) CHECK (Grade >= 0 AND Grade <= 10),
    GradeLetter VARCHAR(5),
    Note VARCHAR(255),
    PRIMARY KEY (StudentID, ClassID),
    CONSTRAINT fk_enrollments_student
        FOREIGN KEY (StudentID) REFERENCES students(StudentID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_enrollments_class
        FOREIGN KEY (ClassID) REFERENCES classes(ClassID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================================
-- Indexes (performance)
-- ============================================================
CREATE INDEX idx_students_enrollment_year ON students (EnrollmentYear);
CREATE INDEX idx_classes_subjectcode ON classes (SubjectCode);
CREATE INDEX idx_enrollments_class ON enrollments (ClassID);
