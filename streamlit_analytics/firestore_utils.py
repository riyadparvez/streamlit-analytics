import json
from datetime import datetime, timedelta, timezone
from typing import Any

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

    def insert_doc(self, key: str, document: dict[str, Any]):
        document = document.copy()
        document["mytime"] = firestore.SERVER_TIMESTAMP
        self.collection_ref.document(key).set(document)

    def f(self, window: int):
        """
        Returns only last `window` hours of data
        """
        now = datetime.now(timezone.utc)
        filtered_timestamp = now - timedelta(hours=window)
        docs = (
            db.collection(collection_name)
            .where("mytime", ">=", filtered_timestamp)
            .stream()
        )
        for doc in docs:
            print(f"{doc.id} => {doc.to_dict()}")
            print(doc.create_time)
            print(doc.update_time)
            print("\n")


if __name__ == "__main__":
    collection_name = "analytics-test"
    adapter = FirestoreAdapter(collection_name)
    adapter.f(24)
