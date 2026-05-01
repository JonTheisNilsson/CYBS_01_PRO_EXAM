add venv to gitignore



source bin/activate

pip install -r requirements.txt

pip install python-dotenv


tood:

create validation schema for
token response - not done
bulk response
incident - needs testing
alert - needs testing

update with built-in types for email, ips, hosts?....

create new sql schema

logging


jsonschema
alert changed, last_seen is removed and can no longer be required in schema
https://json-schema.org/understanding-json-schema/reference/comments



docstrings are outdated
Sphinx autodoc_typehints


spørg alex
kan vi antage at incidentId og alertId er unikke?
hvordan skal ioc table forstås?
er rækkefølgen på incidents bestemt?
kan tidligere incidents blive opdateret?
må vi selv vælge docstring koncention?
bør vi holde os til minimum db eller fylde den op?