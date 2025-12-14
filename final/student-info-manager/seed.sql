-- ============================================================
-- SEED.SQL (Final – Stored-procedure generation, no CTE)
-- REQUIREMENT: Run schema.sql BEFORE running this file
-- ============================================================

-- ============================================================
-- SUBJECTS (6 subjects)
-- ============================================================
INSERT INTO subjects (SubjectCode, SubjectName, Credits) VALUES
('MATH101', 'Calculus I', 3),
('CS101', 'Introduction to Programming', 3),
('PHY101', 'Physics I', 4),
('ENG201', 'Academic English', 2),
('STA202', 'Applied Statistics', 3),
('CS201', 'Data Structures', 4);

-- ============================================================
-- LECTURERS (4 lecturers)
-- ============================================================
INSERT INTO lecturers (LecturerFirstName, LecturerLastName, LecturerEmail, Office) VALUES
('John', 'Smith', 'john.smith@example.com', 'B201'),
('Anna', 'Nguyen', 'anna.nguyen@example.com', 'C305'),
('David', 'Tran', 'david.tran@example.com', 'A110'),
('Mika', 'Suzuki', 'mika.suzuki@example.com', 'B103');

-- ============================================================
-- 10 manual STUDENTS (sample)
-- ============================================================
INSERT INTO students  
(FirstName, LastName, DOB, Gender, Address, Phone, Email, EnrollmentYear, Major) VALUES
('Minh', 'Tran', '2004-05-12', 'M', 'Hanoi', '0123456789', 's1@example.com', 2022, 'Computer Science'),
('Linh', 'Pham', '2004-09-21', 'F', 'Ho Chi Minh City', '0987654321', 's2@example.com', 2022, 'Physics'),
('Khoa', 'Le', '2003-03-10', 'M', 'Da Nang', '0912345678', 's3@example.com', 2021, 'Mathematics'),
('An', 'Vu', '2004-11-02', 'F', 'Haiphong', '0901122334', 's4@example.com', 2022, 'Computer Science'),
('Huy', 'Dang', '2003-08-19', 'M', 'Hanoi', '0933112455', 's5@example.com', 2021, 'Statistics'),
('Nhi', 'Lam', '2005-01-15', 'F', 'Hue', '0988877665', 's6@example.com', 2023, 'Computer Science'),
('Bao', 'Ho', '2004-07-03', 'M', 'Hanoi', '0911112222', 's7@example.com', 2022, 'Mathematics'),
('Quynh', 'Nguyen', '2004-12-25', 'F', 'HCMC', '0914455667', 's8@example.com', 2022, 'English'),
('Long', 'Pham', '2003-02-08', 'M', 'HCMC', '0939998888', 's9@example.com', 2021, 'Physics'),
('Trang', 'Do', '2005-04-14', 'F', 'Hanoi', '0975772446', 's10@example.com', 2023, 'Computer Science');

-- ============================================================
-- AUTO-GENERATE 190 STUDENTS USING A STORED PROCEDURE
-- This avoids CTE/user-variable warnings and is compatible widely
-- ============================================================

DELIMITER $$

CREATE PROCEDURE seed_many_students()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE genDob DATE;
    DECLARE genGender CHAR(1);
    DECLARE genPhone VARCHAR(20);
    DECLARE genEmail VARCHAR(100);
    DECLARE genMajor VARCHAR(50);

    WHILE i <= 190 DO
        -- DOB pattern
        SET genDob = DATE_ADD('2003-01-01', INTERVAL (i % 600) DAY);

        -- Gender pattern
        IF i % 3 = 0 THEN
            SET genGender = 'M';
        ELSEIF i % 3 = 1 THEN
            SET genGender = 'F';
        ELSE
            SET genGender = 'O';
        END IF;

        -- Phone and email pattern
        SET genPhone = CONCAT('090', LPAD(i, 7, '0'));
        SET genEmail = CONCAT('student', i, '@example.com');

        -- Major pattern
        IF i % 4 = 0 THEN
            SET genMajor = 'Computer Science';
        ELSEIF i % 4 = 1 THEN
            SET genMajor = 'Mathematics';
        ELSEIF i % 4 = 2 THEN
            SET genMajor = 'Physics';
        ELSE
            SET genMajor = 'Statistics';
        END IF;

        INSERT INTO students (
            FirstName, LastName, DOB, Gender, Address, Phone, Email, EnrollmentYear, Major
        ) VALUES (
            CONCAT('Student', i),
            CONCAT('Test', i),
            genDob,
            genGender,
            'Vietnam',
            genPhone,
            genEmail,
            2020 + (i % 5),
            genMajor
        );

        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

-- Call the procedure to insert 190 students
CALL seed_many_students();

-- Optionally drop the procedure (cleanup)
DROP PROCEDURE IF EXISTS seed_many_students;

-- ============================================================
-- CLASSES (minimum 4 classes)
-- ============================================================
INSERT INTO classes (SubjectCode, LecturerID, ClassName, Semester, Year, MaxCapacity) VALUES
('MATH101', 1, 'Calculus I - Group 1', 'S1', 2024, 60),
('CS101', 2, 'Intro Programming - Group 1', 'S1', 2024, 60),
('PHY101', 3, 'Physics I - Group 1', 'S1', 2024, 60),
('STA202', 4, 'Applied Statistics - Group 1', 'S1', 2024, 60);

-- ============================================================
-- ENROLLMENTS (45 rows) — safe insertion using a subquery
-- ============================================================
INSERT INTO enrollments (StudentID, ClassID, Grade, GradeLetter, Note)
SELECT t.StudentID, t.ClassID, t.g, 
    CASE
        WHEN t.g >= 9 THEN 'A'
        WHEN t.g >= 8 THEN 'B'
        WHEN t.g >= 7 THEN 'C'
        WHEN t.g >= 6 THEN 'D'
        ELSE 'F'
    END AS GradeLetter,
    ''
FROM (
    SELECT s.StudentID, c.ClassID, ROUND(RAND() * 10, 2) AS g
    FROM students s
    JOIN classes c
    WHERE s.StudentID <= 50
    ORDER BY RAND()
    LIMIT 45
) AS t;

-- ============================================================
-- Done
-- ============================================================
