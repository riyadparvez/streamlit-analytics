import json

from google.cloud import firestore
from google.oauth2 import service_account

config_path = "/Users/riyad/Downloads/firestore.json"

with open(config_path) as f:
    firestore_config = json.load(f)

creds = service_account.Credentials.from_service_account_info(firestore_config)
db = firestore.Client(credentials=creds)


def get_document(collection_ref):
    for doc in collection_ref.stream():
        print(f"{doc.id} => {doc.to_dict()}")


def insert_new_doc(collection_name: str, key: str, document: dict):
    collection_ref = db.collection(collection_name)
    # Add a new doc in collection 'cities' with ID 'LA'
    collection_ref.document(key).set(document)


if __name__ == "__main__":
    collection_name = "analytics-test"
    collection_ref = db.collection(collection_name)
    get_document(collection_ref)
