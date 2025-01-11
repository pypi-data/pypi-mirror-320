ssh root@157.230.228.116

docker exec -it mavera-api bash
python

from src.mavera.database import PersonaDB
db = PersonaDB()
key = db.create_api_key("Bill Hickman", "bill@mavera.io")
print(f"Generated key: {key}")
