SELECT incidentId, type, value, COUNT(*) AS cnt
FROM iocs
GROUP BY incidentId, type, value
HAVING COUNT(*) > 1;