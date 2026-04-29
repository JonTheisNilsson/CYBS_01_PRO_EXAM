import json
import jsonschema
from jsonschema import validate

    
def validate_response(response, schema_path: str) -> bool:

    with open(schema_path, 'r') as file:
        schema = json.load(file)

    try:
        validate(instance=response, schema=schema)
        #print("JSON data is valid.")
        return True
    except jsonschema.exceptions.ValidationError as e: # type: ignore
        print(f"JSON data is invalid: {e.message}")
        return False