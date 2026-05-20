Programmering exam Cybersecurity 2026 EK

Dette program bruges til at hente incidents fra et API
og gemme dem i en lokal SQLite database.

## Struktur
root<br />
├── json_schema<br />
│   ├── schema_summary.json<br />
|   └── schema_token.json<br />
├── .env<br />
├── exam.db<br />
├── db.py<br />
├── exam.log<br />
├── main.py<br />
├── requirements.txt<br />
├── token<br />
└── validate.py<br />

## Requirements 
pip install -r requirements.txt

Programmet kræver en e-mail og en server-url. De kan enten gives med command line arguments (der prioteres) eller i en .env fil. 

.env fil skal indholde:
URL = "http://164.92.167.24"<br />
EMAIL = "din skole mail"


Commanline arguments:
usage: main.py [-h] [-u URL] [-e EMAIL] [-d]

options:
  -h, --help         show this help message and exit
  -u, --url URL      Server url. Can be stored in .env
  -e, --email EMAIL  Student e-mail. Can be stored in .env
  -d, --debug        Debug. Print out responses as json-files







