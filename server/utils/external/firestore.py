from typing import Optional

from google.cloud import firestore
from google.oauth2 import service_account

from shapes.events import Event
from utils import logger


class _EventTable:
    def __init__(self):
        # Read the service account credentials from a JSON file
        service_account_file_path = "./cred.json"
        credentials = service_account.Credentials.from_service_account_file(service_account_file_path)
        self.client = firestore.Client(credentials=credentials)

    def create_event(self, event: Event):
        doc_ref = self.client.collection("events").document(event.id)
        doc_ref.set(event.model_dump())
        return doc_ref.id

    def get_events(self) -> list[Event]:
        docs = (self.client.collection("events")
                .order_by("timestamp", direction="DESCENDING")
                .stream())
        return [Event(**doc.to_dict()) for doc in docs]

    def get_event_by_id(self, event_id) -> Optional[Event]:
        doc_ref = self.client.collection("events").document(event_id)
        doc = doc_ref.get()

        if not doc.exists:
            logger.warn(f"No document found for ID: {event_id}")
            return None

        return Event(**doc.to_dict())


EventTable = _EventTable()

if __name__ == '__main__':
    events = EventTable.get_events()
    for event in events:
        print(event.timestamp)
