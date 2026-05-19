CREATE TABLE IF NOT EXISTS incidents (
incidentID      TEXT PRIMARY KEY,
incidentName    TEXT,
severity        TEXT,
status          TEXT,
createdTime     TEXT
)


CREATE TABLE IF NOT EXISTS alerts (
alertId             TEXT PRIMARY KEY,
incidentID          TEXT,
machineID           TEXT,
detectionSource     TEXT,
firstActivity       TEXT
)


CREATE TABLE IF NOT EXISTS iocs (
incidentId  TEXT,
type        TEXT,
value       TEXT,
PRIMARY KEY (incidentId, type, value)
);