import datetime


def init_db(connection) -> None:
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        alertID     TEXT,
        incidentID  TEXT,
        category    TEXT,
        machineID   TEXT,
        firstSeen   TEXT,
        timestamp   TEXT
        );"""
    )
    connection.commit()


def add_alert(connection, alert, incident_id:str) -> None:
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO alerts (alertID, incidentID, category, machineID, firstSeen, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (alert["alertId"], 
         incident_id, 
         alert["category"], 
         alert["machineId"], 
         None, 
         datetime.datetime.now())
    )
    connection.commit()


def get_count_incidents() -> int:
    raise NotImplemented


def get_count_alerts() -> int:
    raise NotImplemented