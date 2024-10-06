from google.cloud import firestore
from google.oauth2 import service_account

from shapes.sender_message import Event


class _EventTable:
    def __init__(self):
        # Read the service account credentials from a JSON file
        service_account_file_path = "./creds.json"
        credentials = service_account.Credentials.from_service_account_file(service_account_file_path)
        self.client = firestore.Client(credentials=credentials)

    def create_event(self, event: Event):
        doc_ref = self.client.collection("events").document()
        doc_ref.set(event.model_dump())
        print("Document created.")

    def get_events(self):
        print("Getting events...")
        docs = self.client.collection("events").stream()
        for doc in docs:
            print(f"{doc.id} => {doc.to_dict()}")
        return docs


EventTable = _EventTable()
