import json
from pathlib import Path

import jsonschema
from jsonschema import validate


    
def validate_response(response, schema_path: Path) -> bool:

    return validate_json(response.json(), schema_path)

    with open(schema_path, 'r') as file:
        schema = json.load(file)

    try:
        validate(instance=response.json(), schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e: # type: ignore
        print(f"JSON data is invalid: {e.message}")
        return False
    


def validate_json(jsonable, schema_path: Path) -> bool:
    with open(schema_path, 'r') as file:
        schema = json.load(file)

    try:
        validate(instance=jsonable, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e: # type: ignore
        print(f"JSON data is invalid: {e.message}")
        return False