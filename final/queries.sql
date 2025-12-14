USE student_management;

SELECT 
    s.StudentID,
    s.FirstName,
    s.LastName,
    c.ClassID,
    sub.SubjectName,
    e.Grade
FROM enrollments e
INNER JOIN students s 
    ON e.StudentID = s.StudentID
INNER JOIN classes c 
    ON e.ClassID = c.ClassID
INNER JOIN subjects sub 
    ON c.SubjectCode = sub.SubjectCode;

SELECT 
    s.StudentID,
    s.FirstName,
    s.LastName,
    c.ClassID,
    e.Grade
FROM students s
LEFT JOIN enrollments e 
    ON s.StudentID = e.StudentID
LEFT JOIN classes c 
    ON e.ClassID = c.ClassID;

SELECT 
    s.StudentID,
    s.FirstName,
    s.LastName,
    ROUND(AVG(e.Grade), 2) AS AvgGrade,
    COUNT(*) AS TotalClasses
FROM students s
JOIN enrollments e 
    ON s.StudentID = e.StudentID
WHERE e.Grade IS NOT NULL
GROUP BY s.StudentID
HAVING COUNT(*) >= 3
ORDER BY AvgGrade DESC
LIMIT 10;

SELECT AVG(Grade) 
INTO @global_avg
FROM enrollments
WHERE Grade IS NOT NULL;

SELECT 
    s.StudentID,
    s.FirstName,
    s.LastName,
    ROUND(AVG(e.Grade), 2) AS StudentAvg
FROM students s
JOIN enrollments e 
    ON s.StudentID = e.StudentID
WHERE e.Grade IS NOT NULL
GROUP BY s.StudentID
HAVING StudentAvg > @global_avg;
