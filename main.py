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

    print("Attempting to open local token.")
    try:
        with open ("token", 'r') as file: 
            token_object = json.load(file)

        token = token_object["token"]
        expires_at = token_object["expires_at"]
        expires_at = datetime.fromisoformat(expires_at)

        if expires_at.timestamp() < datetime.now().timestamp():  # todo: test sammenligning af datetime
            print("Local token expired.")
            token = None
        
    except Exception as err:
        print("Failure to find local token.", err)  # catch-all
        token = None

    if token is None:  
        print("Requesting new token.") #todo: logger
        response = request_token(url, email)
        response = response.json()
        
        with open("token", 'w') as file:
            file.write(json.dumps(response, indent=4))
        token = response["token"]

    # for testing and for generating json schemas. must delete
    if response:
        with open("tmp_token_response.json", 'w') as file:
            file.write(json.dumps(response, indent=4))

    print("Token got")
    return token


def request_token(url: str, email: str) -> Response:
    # Happily ignoring all exception handling
    r = requests.post(url + "/api/auth/token", json={"email": email})
    
    return r


def get_all_incidents(url: str, token: str, skip=0) -> list:
    '''  
    Another unnecessary docstring

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
        except requests.exceptions.Timeout as err:
            if retry: 
                print("Timeout. Retrying in 5 sec")
                time.sleep(5)
                retry = False
                continue

            print("Timeout. Retried once", file=sys.stderr)
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
        

        response = response.json()
        
        with open(f"tmp_bulk_response_{skip}.json", 'w') as file:
            file.write(json.dumps(response, indent=4))

        for i in response["value"]:
            if validate_response(i, "json_schema/schema_incident.json"):
                incidents.append(i)
            else:
                print("Validation error", i)
        

        if "@odata.nextLink" in response:
            skip += 100
            print("Waiting...")
            time.sleep(1.5)
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

    print(response.status_code, '-', response.headers) # todo logger

    '''
    try:
        j = response.json()
        with open(f"out{top}-{skip}.json", 'w') as file:
            file.write(json.dumps(j, indent=4))

    except Exception as err:
        print(type(err).__name__)
        print(err.__class__.__name__)
        print(err.__class__.__qualname__)
    '''
    return response


def request_incident(url: str, token: str, id='INC-SQLI-001') -> Response:
    header = {"Authorization": "Bearer " + token}
    response = requests.get(url + "/api/incidents/" + id, headers=header)

    print(response.status_code, '-', response.headers) # todo logger

    ''' done
    j = response.json()
    with open(f"out_incident.json", 'w') as file:
        file.write(json.dumps(j, indent=4))

        done
    alert = j['alerts'][0]
    with open(f"out_alert.json", 'w') as file:
        file.write(json.dumps(alert, indent=4))
    '''
        
    return response

def output_to_db(incidents, database="alerts.db") -> None:
    try:
        with sqlite3.connect(fr"db/{database}") as connection:
            db.init_db(connection)
        
            for incident in incidents:
                for alert in incident["alerts"]:
                    db.add_alert(connection, alert, incident["incidentId"])

    except Exception as err:
        print("db error. attempting rollback", file=sys.stderr)
        connection.rollback() # type: ignore


def output_to_file(incidents, filepath="incidents.json") -> None:
    try:
        with open(filepath, 'a') as file:
            o = json.dumps(incidents, indent=4)
            file.write(o)
    
    except Exception as err:
        print("oh no, my output to file", err)


def setup_logger(log_path = "exam.log") -> logging.Logger:
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
    # arg parser, if not load from env
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="url todo")
    parser.add_argument("-e", "--email", help="email todo")
    args = parser.parse_args()

    #setup env
    load_dotenv(override=True) 

    if args.url:
        url = args.url
    else:
        url= os.getenv("url")#r"http://164.92.167.24" # todo: move to env
        
    if args.email:
        email = args.email
    else:
        email = os.getenv("email")#"joni0003@stud.ek.dk" # todo: move to env

    if url is None or email is None:
        print("oh no, my {err.__name__}", file=sys.stderr)
        raise SystemExit(1)  

    global logger
    logger = setup_logger()

    token = get_token(url, email) 

    #request_incident(url, token)
    
    incidents = get_all_incidents(url, token)

    output_to_db(incidents, "simple.db")
    #output_to_file(incidents)


if __name__ == "__main__":
    main()