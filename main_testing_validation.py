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
from dotenv import load_dotenv, dotenv_values 

import db.db as db
from validate import validate_response, validate_json
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

    #logger.info("Attempting to open local token.")
    try:
        with open ("token", 'r') as file: 
            token_object = json.load(file)

        token = token_object["token"]
        expires_at = token_object["expires_at"]
        expires_at = datetime.fromisoformat(expires_at)

        if expires_at.timestamp() < datetime.now().timestamp():  # todo: test sammenligning af datetime
            #logger.info("Local token expired.")
            token = None
        
    except Exception as err:
        #logger.info("Failure to find local token. {err}")  # catch-all
        token = None

    if token is None:  
        #logger.info("Requesting new token.")
        response = request_token(url, email)
        response = response.json()
        
        with open("token", 'w') as file: # todo rewrite
            file.write(json.dumps(response, indent=4))
        token = response["token"]

    #logger.info("Token got")
    return token


def request_token(url: str, email: str) -> Response:
    r = requests.post(url + "/api/auth/token", json={"email": email})
    
    return r


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

    return response


def request_incident(url: str, token: str, id='INC-SQLI-001') -> Response:
    header = {"Authorization": "Bearer " + token}
    response = requests.get(url + "/api/incidents/" + id, headers=header)

    return response


def request_summary(url: str, token: str) -> Response:
    '''GET /api/incidents/summary'''
    header = {"Authorization": "Bearer " + token}
    response = requests.get(url + "/api/incidents/summary", headers=header)

    return response


def jsonable_to_file(jsonable, filename="out.json", mode='a') -> None:
    '''Simple jsonable output to file, mostly for manual testing.

    Args:
    '''
    try:
        with open(BASE_PATH / filename, mode) as file:
            o = json.dumps(jsonable, indent=4)
            file.write(o)
    
    except Exception as err:
        print("oh no, my output to file", err)


def main() -> None:
    global BASE_PATH
    BASE_PATH = Path(__file__).resolve().parent

    #setup env todo anything else?
    load_dotenv(override=True) 
    url = str(os.getenv("URL"))
    email = str(os.getenv("EMAIL"))
    token = get_token(url, email) 

    '''
    token_resp = request_token(url, email)
    btoken = validate_response(token_resp, BASE_PATH / "json_schema" / "schema_token.json" )
    print(f"{btoken=}")
    '''
    
    '''
    summ_resp = request_summary(url, token)
    bsumm = validate_response(summ_resp, BASE_PATH / "json_schema" / "schema_summary.json" )
    print(f"{bsumm=}")
    '''

    
    inci_resp = request_incident(url, token)
    '''
    binci = validate_response(inci_resp, BASE_PATH / "json_schema" / "schema_incident.json" )
    print(f"{binci=}")
    '''
    
    '''
    bulk_resp = request_incidents(url,token, top=10, skip=3)
    bbulk = validate_response(bulk_resp, BASE_PATH / "json_schema" / "schema_bulk.json" )
    print(f"{bbulk=}")
    '''

    inci = inci_resp.json()
    alerts = inci["alerts"]
    alert = alerts[0]
    balert = validate_json(alert, BASE_PATH / "json_schema" / "schema_alert.json")
    print(f"{balert=}")


if __name__ == "__main__":
    main()