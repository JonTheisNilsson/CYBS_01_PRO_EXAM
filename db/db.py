import datetime



def drop_db(connection) -> None:
    cursor = connection.cursor()
    cursor.execute('''DROP TABLE incidents''')
    cursor.execute('''DROP TABLE alerts''')
    cursor.execute('''DROP TABLE iocs''')
    pass


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
        
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents_index (
    ID              INTEGER PRIMARY KEY AUTOINCREMENT,
    incidentId      TEXT,
    incidentName    TEXT
    );''')
    connection.commit()
    #


def add_alert(connection, alert, incident_id:str) -> None:
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO alerts (alertID, incidentID, machineID, detectionSource, firstActivity) VALUES (?, ?, ?, ?, ?)",
        (alert["alertId"], 
         incident_id,  
         alert["machineId"], 
         alert["detectionSource"], 
         alert["firstActivity"])
    )
    connection.commit()


def add_incident(connection, incident) -> None:
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO incidents (incidentID, incidentName, severity, status, createdTime) VALUES (?, ?, ?, ?, ?)",
        (incident["incidentId"], 
         incident["incidentName"],
         incident["severity"],
         incident["status"],
         datetime.datetime.now())
    )
    connection.commit()


def add_ioc(connection, incident_id, ioc_type, ioc_value) -> None:
    cursor = connection.cursor()
    cursor.execute("INSERT OR IGNORE INTO iocs(incidentID, type, value) VALUES (?,?,?)",
                   (incident_id,
                    ioc_type,
                    ioc_value))
    connection.commit()


def add_index(connection, incident) -> None:
    cursor = connection.cursor()
    cursor.execute("INSERT INTO incidents_index(incidentId, incidentName) VALUES (?,?)",
                   (incident['incidentId'],
                    incident['incidentName']))
    connection.commit()



def get_count_incidents(connection) -> int:
    cursor = connection.cursor()
    cursor.execute(
    '''select count( ) from incidents''')
    count = cursor.fetchone()
    return count[0]


def get_count_alerts() -> int:
    raise NotImplemented