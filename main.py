#region imports
import argparse
import os
import sys
import time
import json
import sqlite3
import logging
from datetime import datetime

import requests
from requests import Response
from dotenv import load_dotenv, dotenv_values 

import db.db as db
from validate import validate_response
#endregion

def get_token(url: str, email: str) -> str:
    '''  
    Check for valid local token. If none, requests a new one.

    Args:
        url (str): url!
        email (str): student-email
    
    Returns:
        str: token
    '''

    response = False

    logger.info("Attempting to open local token.")
    try:
        with open ("token", 'r') as file: 
            token_object = json.load(file)

        token = token_object["token"]
        expires_at = token_object["expires_at"]
        expires_at = datetime.fromisoformat(expires_at)

        if expires_at.timestamp() < datetime.now().timestamp():  # todo: test sammenligning af datetime
            logger.info("Local token expired.")
            token = None
        
    except Exception as err:
        logger.info("Failure to find local token. {err}")  # catch-all
        token = None

    if token is None:  
        logger.info("Requesting new token.")
        response = request_token(url, email)
        response = response.json()
        
        with open("token", 'w') as file: # todo rewrite
            file.write(json.dumps(response, indent=4))
        token = response["token"]

    # for testing and for generating json schemas. must delete
    if response:
        jsonable_to_file(response)

    logger.info("Token got")
    return token


def request_token(url: str, email: str) -> Response:
    # Happily ignoring all exception handling todo
    r = requests.post(url + "/api/auth/token", json={"email": email})
    
    return r


def get_incidents(url: str, token: str, skip=0) -> list:
    '''  
    todo: Another unnecessary docstring

    Args:
        url (str): url!
        token (str): token
        skip (int): how many incidents to skip in (in chronological order?)
    
    Returns:
        list: list of validated incidents
    '''

    incidents = []
    retry = True

    while (True):
        try:
            response = request_incidents(url, token, top=100, skip=skip)
            if response.status_code==418:
                jsonable_to_file(response.json(), "teapot.txt", mode='a')
                raise requests.exceptions.Timeout

        except requests.exceptions.Timeout as err:
            if retry: 
                print("Timeout. Retrying in 5 sec")
                time.sleep(5)
                retry = False
                continue

            print("Timeout. Retried once. Exiting", file=sys.stderr)
            raise SystemExit(1)
        except requests.HTTPError as err:
            print("http error", file=sys.stderr)
            raise SystemExit(1)
        except requests.RequestException as err:
            print("RequestException", file=sys.stderr)
            raise SystemExit(1)
        except Exception as err:
            print("oh no, my {err.__name__}", file=sys.stderr)
            raise SystemExit(1)      
        
        if response.status_code != 200:
            with open("temp_error.txt", 'w') as file:
                file.write(str(response.content))

        response = response.json() # todo: error handleing
        
        # with open(f"tmp_bulk_response_{skip}.json", 'w') as file:
        #     file.write(json.dumps(response, indent=4))
        #debug
        jsonable_to_file(response, f"tmp_bulk_response_{skip}.json", 'w')

        for i in response["value"]:
            if validate_response(i, "json_schema/schema_incident.json"):
                incidents.append(i)
            else:
                logger.error(f"Validation error, {i} ") # todo what to do 
        
        if "@odata.nextLink" in response:
            skip += 100
            print("Waiting...")
            time.sleep(2)
        else:
            break

    return incidents


def request_incidents(url: str, token: str, top=10, skip=0) -> Response:
    '''  
    Another unnecessary docstring

    Args:
        url (str): url!
        token (str): token
        top (int): how many incidents to requests
        skip (int): how many incidents to skip in (in chronological order?)
    
    Returns:
        Response: http response of incidents
    '''
    header = {"Authorization": "Bearer " + token}
    payload ={"$top": top,
              "$skip": skip}
    response = requests.get(url + "/api/incidents", headers=header, params=payload)

    logger.info(f"{response.status_code} - {response.headers}") 

    return response


def request_incident(url: str, token: str, id='INC-SQLI-001') -> Response:
    header = {"Authorization": "Bearer " + token}
    response = requests.get(url + "/api/incidents/" + id, headers=header)

    logger.info(f"{response.status_code} - {response.headers}")

    return response


def request_summary(url: str, token: str) -> Response:
    '''GET /api/incidents/summary'''
    header = {"Authorization": "Bearer " + token}
    response = requests.get(url + "/api/incidents/summary", headers=header)

    jsonable_to_file(response.json(), "summary_respones.json", mode='w')

    logger.info(f"{response.status_code} - {response.headers}")

    return response


def incidents_to_db(incidents, database="alerts.db") -> None:
    
    print("starting output to db")
    try:
        with sqlite3.connect(fr"db/{database}") as connection:
            db.init_db(connection)
        
            for incident in incidents:
                db.add_incident(connection, incident)
                for alert in incident["alerts"]:
                    db.add_alert(connection, alert, incident["incidentId"])
                    iocs = []
                    for domain in alert["entities"]["domains"]:
                        iocs.append(('domains', domain))
                    for email in alert["entities"]["emails"]:
                         iocs.append(('emails', email))
                    for fileHash in alert["entities"]["fileHashes"]:
                         iocs.append(('fileHashes', fileHash))
                    for ip in alert["entities"]["ips"]:
                         iocs.append(('ips', ip))
                    for process in alert["entities"]["processes"]:
                         iocs.append(('processes', process))    
                    for url in alert["entities"].get("urls", []):
                         iocs.append(('urls', url))  
                    for ioc in iocs:
                        db.add_ioc(connection, incident["incidentId"], ioc[0], ioc[1])          

    except Exception as err:
        logger.error(err, )
        print("db error. attempting rollback", file=sys.stderr)
        connection.rollback() # type: ignore


def jsonable_to_file(jsonable, filepath="out.json", mode='a') -> None:
    '''Simple jsonable output to file, mostly for manual testing.

    Args:
    '''
    try:
        with open(filepath, mode) as file:
            o = json.dumps(jsonable, indent=4)
            file.write(o)
    
    except Exception as err:
        print("oh no, my output to file", err)


def setup_logger(log_path="exam.log") -> logging.Logger:
    logging.basicConfig(
        filename=log_path,
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
    # arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="url. Can be stored in .env. todo")
    parser.add_argument("-e", "--email", help="Student e-mail. Can be stored in .env")
    parser.add_argument("-d", "--debug", action='store_true', help="Only request single incident, no db")
    args = parser.parse_args()
    # todo: add a reset flag to drop db, download everything from to top. maybe backup db

    #setup env todo anything else?
    load_dotenv(override=True) 


    #set module directory todo

    #set url and email
    if args.url:
        url = args.url
    else:
        url = os.getenv("URL")
        
    if args.email:
        email = args.email
    else:
        email = os.getenv("EMAIL")

    # url and email is required, todo better error message, add log
    if url is None or email is None:
        print("oh no, my {err.__name__}", file=sys.stderr)
        raise SystemExit(1)  


    # setting logger to global to avoid having to pass it around
    global logger
    logger = setup_logger()

    # todo think should  tkoen be saved in env?
    token = get_token(url, email) 


    # check how many incidents in sky
    summary = request_summary(url, token)
    summary = summary.json()
    count_in_sky = summary["total_incidents"]
    print(count_in_sky, "sky")

    # check how many incidents in db
    with sqlite3.connect(fr"db/exam.db") as connection:
        db.init_db(connection)
        count_in_db =(db.get_count_incidents(connection))
    
    # if there is new incidents, dl them
    print(count_in_db, 'db')
    if count_in_sky > count_in_db:
        incidents = get_incidents(url, token, skip=count_in_db)
        incidents_to_db(incidents, "exam.db")
    #todo some kind of message if no new

    '''
    if args.debug:
        r = request_incident(url, token)
        r = r.json()
        #print(json.dumps(r, indent=4))
    else:
        pass
        #incidents = get_incidents(url, token)
        #output_to_db(incidents, "exam.db")
        #output_to_file(incidents)
    '''

if __name__ == "__main__":
    main()