for at køre:

installer de moduler vi bruger:

pip install -r requirements.txt


lav en fil til environment varible
.env

indhold:
URL = "http://164.92.167.24"
EMAIL = "din skole mail"




add venv to gitignore


python -m venv .venv
source .venv/bin/activate
source .venv/bin/activate.fish



pip install python-dotenv


todo:
ioc types skal tages fra api

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


skip problemer. fik dubs selvom jeg ikke burde. ved ikke hvor rækkefælgen blev ændret


change to bulk insert - executemany?

init db bør rykkes ud og udføres før

docstrings are outdated
Sphinx autodoc_typehints

INC1257 dublicated? 263 264?

tilføj validation i request-funktionerne

spørg alex / svar
kan vi antage at incidentId og alertId er unikke? ja
hvordan skal ioc table forstås? forstået korrekt
er rækkefølgen på incidents fastlåst? ja...
kan tidligere incidents blive opdateret? nej...
må vi selv vælge docstring konvention?
bør vi holde os til minimum db eller fylde den op? det er fint med minimum

Hvad kunne det f.eks. være (Handle API credentials securely)? token kunne holdes i .env, men det er fint at holde den i sin egen fil. Så slipper vi for at opdatere .env i runtime.

hvad er et namespace?