import sqlite3

from db import db


entities = {
                "domains": [
                    "update-oresund.com"
                ],
                "emails": [
                    "eng.larsen@oresund-industrial.dk"
                ],
                "fileHashes": [
                    "5d41402abc4b2a76b9719d911017c592"
                ],
                "ips": [
                    "192.168.30.10",
                    "172.16.100.10"
                ],
                "processes": [
                    "python3.exe sqlmap.py -u http://172.16.100.10/portal/login --data \"username=admin&password=test\" --technique=B --level=5 --batch",
                    "python3.exe sqlmap.py -u http://172.16.100.10/portal/login --data \"username=admin' OR '1'='1'-- -&password=x\" --dump --tables"
                ],
                "urls": [
                    "http://172.16.100.10/portal/login?username=admin' OR '1'='1'-- -&password=x",
                    "http://172.16.100.10/portal/login?username=admin'--&password="
                ]
            },


def incidents_to_db(incidents, database="alerts.db") -> None:
    
    with sqlite3.connect(fr"db/{database}") as connection:
        db.init_db(connection)
    
        for incident in incidents:
            db.add_incident(connection, incident)
            for alert in incident.get("alerts", []):
                db.add_alert(connection, alert, incident["incidentId"])
                
                entities = alert['entities']

                for key, value in entities.items():
                    for item in value:
                        db.add_ioc(connection, incident["incidentId"], key, item)   

                for key in ['domains', 'emails', 'fileHashes', 'ips', 'processes', 'url']:
                    for value in entities.get(key, []):
                        pass


for ent in entities:
    for type, values in ent.items():
        for value in values:
            print(type, value)


def add_ioc():
    pass