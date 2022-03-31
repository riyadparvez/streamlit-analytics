import json
from google.cloud import firestore
from google.oauth2 import service_account

config_path = "/Users/riyad/Downloads/firestore.json"

with open(config_path) as f:
    config = json.load(f)

creds = service_account.Credentials.from_service_account_info(config)
# db = firestore.Client.from_service_account_json("/Users/riyad/Downloads/firestore.json")
db = firestore.Client(credentials=creds)

collection_ref = db.collection("usage-analytics")
