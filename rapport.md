bruger 
Path(__file__).resolve().parent
til at finde path programmet er i, i stedet for cwd, da det ikke nødvendigvis er det samme.



til at validere http-response'ne bruger vi jsonschema og det tilsvarende python modul.
Det fungere ved at man laver en anden json fil der beskriver strukturen på den json-fil man vil validere. se mappen json_schema.

Vi er ikke sikre på om det er en god løsning eller ej. Det er både en fordel og en ulempe at json er så fleksibelt. Hvis strukturen fra api'en ændre bare en lille smule kan det lukke ned i validering. Måske er det det vi vil have. Det kommer lidt an på projektet.