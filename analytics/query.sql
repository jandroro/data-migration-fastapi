-- Number of employees hired for each job and department in 2021
-- Divided by quarter, ordered alphabetically by department and job

SELECT 
    d.department
    , j.job
    , SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 1 THEN 1 ELSE 0 END) AS Q1
    , SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 2 THEN 1 ELSE 0 END) AS Q2
    , SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 3 THEN 1 ELSE 0 END) AS Q3
    , SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 4 THEN 1 ELSE 0 END) AS Q4
FROM  employees e
    INNER JOIN departments d ON e.department_id = d.id
    INNER JOIN jobs j ON e.job_id = j.id
WHERE EXTRACT(YEAR FROM e.datetime) = 2021
GROUP BY 
    d.department 
    , j.job
ORDER BY 
    d.department ASC
    , j.job asc
;


-- List of ids, name and number of employees hired of each department that hired more employees
-- than the mean of employees hired in 2021 for all the departments, ordered by the number of
-- employees hired (descending).

SELECT 
    id,
    department as name,
    hired
FROM (
    SELECT 
        d.id,
        d.department,
        COUNT(e.id) as hired,
        AVG(COUNT(e.id)) OVER () as mean_hired
    FROM departments d
    LEFT JOIN employees e ON d.id = e.department_id
    WHERE EXTRACT(YEAR FROM e.datetime) = 2021
       OR e.id IS NULL
    GROUP BY d.id, d.department
) as dept_stats
WHERE hired > mean_hired
ORDER BY hired desc
;