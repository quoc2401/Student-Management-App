USE INFORMATION_SCHEMA;
SELECT *
FROM table_constraints
WHERE TABLE_SCHEMA = "mystumana" 
      AND TABLE_NAME = "student" 

SELECT * FROM table_constraints WHERE TABLE_SCHEMA = "quoc2401$mystumana" AND TABLE_NAME = "student";
