import json
from datetime import datetime, timedelta, timezone

from google.cloud import firestore
from google.oauth2 import service_account

config_path = "/Users/riyad/Downloads/firestore.json"

with open(config_path) as f:
    firestore_config = json.load(f)

creds = service_account.Credentials.from_service_account_info(firestore_config)
db = firestore.Client(credentials=creds)


class FirestoreAdapter:
    def __init__(self, collection_name: str) -> None:
        self.collection_name = collection_name
        self.collection_ref = db.collection(collection_name)


    def get_all_documents(collection_ref):
        for doc in collection_ref.stream():
            print(f"{doc.id} => {doc.to_dict()}")


    def insert_doc(self, key: str, document: dict):
        self.collection_ref.document(key).set(document)


    def f(window: int):
        """
        Returns only last `window` hours of data
        """
        now = datetime.now(timezone.utc)
        filtered_timestamp = now - timedelta(hours=window)
        # docs = db.collection(collection_name).where('riyad_test.start_timestamp', '>=', filtered_timestamp).stream()
        # docs = db.collection(collection_name).where('riyad_test.session_id', '>=', "cf67c35a-ee24-4d2b-bd10-ff865c11c0dd").stream()
        # docs = db.collection(collection_name).where('slider_slider', '>=', 67).stream()
        docs = db.collection(collection_name).where('slider_slider', '>=', 67).stream()
        for doc in docs:
            print(f"{doc.id} => {doc.to_dict()}")
            print(doc.create_time)
            print(doc.update_time)
            print("\n")


if __name__ == "__main__":
    collection_name = "analytics-test"
    collection_ref = db.collection(collection_name)
    f(24)

