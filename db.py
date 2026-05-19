import datetime


def init_db(connection) -> None:
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
        incidentID      TEXT PRIMARY KEY,
        incidentName    TEXT,
        severity        TEXT,
        status          TEXT,
        createdTime     TEXT
        );''')
    connection.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
        alertId             TEXT PRIMARY KEY,
        incidentID          TEXT,
        machineID           TEXT,
        detectionSource     TEXT,
        firstActivity       TEXT
        );''')
    connection.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iocs (
        incidentId  TEXT,
        type        TEXT,
        value       TEXT,
        PRIMARY KEY (incidentId, type, value)
        );''')
    connection.commit()




def get_count_incidents(connection) -> int:
    cursor = connection.cursor()
    cursor.execute(
    '''select count( ) from incidents''')
    count = cursor.fetchone()
    return count[0]