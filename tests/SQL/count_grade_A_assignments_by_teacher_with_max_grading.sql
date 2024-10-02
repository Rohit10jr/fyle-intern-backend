-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
WITH TeacherAssignmentCounts AS (
    SELECT teacher_id, COUNT(*) AS total_graded
    FROM assignments WHERE state = 'GRADED' 
    GROUP BY teacher_id
),
MaxGradingTeacher AS (
    SELECT teacher_id
    FROM TeacherAssignmentCounts
    ORDER BY total_graded DESC
    LIMIT 1
)
SELECT COUNT(*) AS grade_A_count FROM assignments
WHERE teacher_id = (SELECT teacher_id FROM MaxGradingTeacher) AND grade = 'A';