#!/usr/bin/env python
""" Programmering exam Cybersecurity 2026 EK

 Dette program bruges til at hente incidents fra et API
og gemme dem i en SQLite database som vi har lært om i skolen.

Programmet håndterer authentication med en token som vi starter med at requeste,
den bruger derefter den token til at requeste incidents fra API'et, i et json format,
g vi gemmer derefter incidents, alerts, IOC i databasen som vi har lavet
 
Der bruges forskellige Python biblioteker til blandt andet:
- HTTP requests
- databasehåndtering
- JSON behandling
- logging

vi har gjort så programmet bruger en lokal .env fil
til at hente URL og email automatisk.

Modified: 2026-05-18
Authors:
Jon Theis Nilsson
Rasmus Nymark Lund
Christian Bjørnsholm Madseb
Daniel Dara Ali Zarhoush

"""

#region imports
import argparse
import os
import sys
import time
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

import requests
from requests import Response
from dotenv import load_dotenv

import db.db as db
from validate import validate_response, validate_json
#endregion

def get_token(url: str, email: str) -> str:
    """Return token, either valid local, or requests a new one.

    Args:
        url (str): Server url
        email (str): student-email
    
    Returns:
        str: token
    """

    response = False

    logger.info("Attempting to open local token.")
    try:
        with open ("token", 'r') as file: 
            token_object = json.load(file)

        if not validate_json(token_object, BASE_PATH / "json_schema" / "schema_token.json"):
            raise Exception
        
        token = token_object["token"]

        if email != token_object["email"]:
            logger.info("Local token belongs to different user.")
            token = None

        expires_at = token_object["expires_at"]
        expires_at = datetime.fromisoformat(expires_at)

        if expires_at.timestamp() < datetime.now().timestamp(): 
            logger.info("Local token expired.")
            token = None

    except Exception as err:
        logger.info(f"Failure to find local token. {err}")  # catch-all
        token = None

    if token is None:  
        try:
            logger.info("Requesting new token.")
            response = request_token(url, email)

            if not validate_response(response, BASE_PATH / "json_schema" / "schema_token.json"):
                print("Response from server could not be validated")
                raise Exception

            response = response.json()
            token = response["token"]

        except Exception as err:
            logger.error(err)
            print("Failure to request new token", file=sys.stderr)
            raise SystemExit(1)
            
        try:
            with open("token", 'w') as file:
                file.write(json.dumps(response, indent=4))

        except Exception as err: 
            logger.warning(f"'Failure to save token. Continueing with temporary token.")
            

    logger.info("Token got")
    return token


def request_token(url: str, email: str) -> Response:
    """Return http-response for POST /api/auth/token."""
    response = requests.post(url + "/api/auth/token", json={"email": email})

    logger.info(f"{response.status_code} - {response.headers}") 
    
    return response


def get_incidents(url: str, token: str, skip=0) -> list:
    """Get all incidents from api, from skip and forward.

    Args:
        url (str): Server url
        token (str): token
        skip (int): how many incidents to skip
    
    Returns:
        list: list of validated incidents
    """

    incidents = []
    retry = True

    while (True):
        try:
            logger.info(f"Requesting 100 incidents, {skip = }")
            response = request_incidents(url, token, top=100, skip=skip)
            if response.status_code == 418:
                jsonable_to_file(response.json(), "teapot.txt", mode='a')
                raise requests.exceptions.Timeout
            #TODO validate response
   
            if response.status_code != 200:
                with open("temp_error.txt", 'w') as file:
                    file.write(str(response.content)) # TODO: kan det skiftes ud med eksisterende funktion?
                raise Exception

            response = response.json() # TODO: error handleing
            
            #TODO
            #if debug:
            #   jsonable_to_file(response, f"tmp_bulk_response_{skip}.json", 'w')

            for i in response["value"]:
                if validate_json(i, BASE_PATH / "json_schema" / "schema_incident.json"):
                    incidents.append(i)
                else:
                    logger.error(f"Validation error, {i} ") # TODO what to do 
            
            if "@odata.nextLink" in response:
                skip += 100
                wait_seconds(2)
            else:
                break

        except requests.exceptions.Timeout as err:
            if retry: 
                print("Timeout. Retrying in 5 sec")
                wait_seconds(5)
                retry = False
                continue
            else:
                print("Timeout. Retried once. Exiting.")
                raise

        except Exception as err:
            print("Error while retriving data. Flushing already recieved data. There can more to retrive on server.")
            logger.error(err)
            break  

    return incidents


def request_incidents(url: str, token: str, top=10, skip=0) -> Response:
    """Returns http-response for GET /api/incidents/.

    Args:
        url (str): Server url
        token (str): token
        top (int): how many incidents to requests
        skip (int): how many incidents to skip in (in chronological order?)
    
    Returns:
        Response: http response of incidents
    """
    header = {"Authorization": "Bearer " + token}
    payload ={"$top": top,
              "$skip": skip}
    response = requests.get(url + "/api/incidents", headers=header, params=payload)

    logger.info(f"{response.status_code} - {response.headers}") 

    return response


def request_incident(url: str, token: str, id='INC-SQLI-001') -> Response:
    """Returns http-response for GET /api/incidents/{id}."""
    header = {"Authorization": "Bearer " + token}
    response = requests.get(url + "/api/incidents/" + id, headers=header)

    logger.info(f"{response.status_code} - {response.headers}")

    return response


def request_summary(url: str, token: str) -> Response:
    """Returns https-response for GET /api/incidents/summary."""
    header = {"Authorization": "Bearer " + token}
    response = requests.get(url + "/api/incidents/summary", headers=header)

    logger.info(f"{response.status_code} - {response.headers}")

    return response


def incidents_to_db(incidents, db_path: Path) -> None:
    """Saves all incidents to database.

    Args:
        incidents (list) - list of incidents
        db_path (Path) - Path to database
    """
    
    print("starting output to db")
    try:
        with sqlite3.connect(db_path) as connection:
            for incident in incidents:
                db.add_incident(connection, incident)

                for alert in incident.get("alerts", []):
                    db.add_alert(connection, alert, incident["incidentId"])
                   
                    entities = alert['entities']
                    
                    for type_, values in entities.items():
                        for value in values:
                            db.add_ioc(connection, incident["incidentId"], type_, value)         

    except Exception as err:
        logger.error(err)
        print("db error. attempting rollback", file=sys.stderr)
        connection.rollback()


def jsonable_to_file(jsonable, filename="out.json", mode='a') -> None:
    """Outputs jsonable to file. Mostly for manual testing and debugging."""
    try:
        with open(BASE_PATH / filename, mode) as file:
            output = json.dumps(jsonable, indent=4)
            file.write(output)
    
    except Exception as err:
        logger.error(err)
        print("Error outputing to file")


def load_email_and_url(args) -> tuple[str, str]:
    """Returns email and url from command line args or .env, prioritizing args."""
    if args.url:
        url = args.url
    else:
        url = os.getenv("URL")
        
    if args.email:
        email = args.email
    else:
        email = os.getenv("EMAIL")

    if url is None or email is None:
        print("E-mail and url is required. Please see --help", file=sys.stderr)
        raise SystemExit(1)  
    
    return url, email


def wait_seconds(seconds: int=1, animation: str|list[str]="|/-\\") -> None:
    """Waits x seconds while displaying a little animation."""
    try:
        id = 0
        end = time.time() + seconds

        print('\033[?25l', end="") # make cursor invisible,  see "ANSI Escape Sequences"

        while end > time.time():
            print(animation[id % len(animation)], end="\r")
            id += 1
            time.sleep(0.1)

    finally:      
        print('\033[?25h', end="") # make cursor visible"


def setup_logger(log_file_name="exam.log") -> logging.Logger:
    """Returns new logger."""
    logging.basicConfig(
        filename=BASE_PATH / log_file_name,
        encoding="utf-8",
        filemode="a",
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    return logger


def main() -> None:
    # Command line arguments parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Server url. Can be stored in .env")
    parser.add_argument("-e", "--email", help="Student e-mail. Can be stored in .env")
    parser.add_argument("-d", "--debug", action='store_true', help="Debug. Print out responses as json-files")
    args = parser.parse_args()

    #set module directories
    global BASE_PATH
    BASE_PATH = Path(__file__).resolve().parent
    DB_PATH = BASE_PATH / "db" / "exam.db" # TODO: could be less hardcoded. 

    # setting logger to global to avoid having to pass it around
    global logger
    logger = setup_logger()

    global DEBUG
    if args.debug:
        logger.info("Debug enabled")
        DEBUG = True

    #Loading local environmennts varibles
    load_dotenv() 

    url, email = load_email_and_url(args)
    token = get_token(url, email) 

    # check hvor mange incidents der er på serveren.
    summary = request_summary(url, token)
    summary = summary.json()
    count_in_sky = summary["total_incidents"]
    print(f"Incidents on server: {count_in_sky}")

    # check hvor mange incidents der er i db, og initialiser db.
    #with sqlite3.connect(fr"db/exam.db") as connection:
    with sqlite3.connect(DB_PATH) as connection:
        db.init_db(connection)
        count_in_db =(db.get_count_incidents(connection))
    
    # Hvis der er nye incidents, request dem.
    print(f"Incidents in database: {count_in_db}")
    if count_in_sky > count_in_db:
        print("Requesting remaining incidents")
        incidents = get_incidents(url, token, skip=count_in_db)
        
        incidents_to_db(incidents, DB_PATH)
    else:
        print("No new incidents.")

    print("Done")


if __name__ == "__main__":
    main()