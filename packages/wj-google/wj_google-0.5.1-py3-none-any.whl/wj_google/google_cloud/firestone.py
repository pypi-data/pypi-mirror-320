import ast
import os
import json
import firebase_admin

from firebase_admin import credentials, firestore
from firebase_admin import auth
from typing import Any, Dict, List, Optional

class Firestore:

    def __init__(self, service_account_json: Optional[str] = None):
        if not service_account_json:
            service_account_json = self._get_credentials_from_env()
        self._initialize_firebase(service_account_json)
        
        # Initialize Firestore client
        self.db = firestore.client()
    
    def _get_credentials_from_env(self) -> str:
        """
        Reads the Google application credentials from the JSON file specified by the
        GCP_CREDENTIALS environment variable and returns the path to the JSON file.
        """
        credentials_value = os.getenv('GCP_CREDENTIALS')
        if not credentials_value:
            raise EnvironmentError("GCP_CREDENTIALS environment variable not set")

        try:
            credential_dict = ast.literal_eval(credentials_value)
            temp_credentials_path = 'temp_credentials.json'
            with open(temp_credentials_path, 'w') as temp_file:
                json.dump(credential_dict, temp_file)
            return temp_credentials_path
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found at path: {temp_credentials_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from the credentials file at path: {credential_dict}")


    def _initialize_firebase(self, service_account_json: str):
        """Initialize Firebase Admin with the provided service account JSON."""
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_json)
            firebase_admin.initialize_app(cred)

    # Firestore operations
    def get_document(self, collection: str, document_id: str) -> Dict[str, Any]:
        """Fetch a document from Firestore."""
        doc_ref = self.db.collection(collection).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None

    def add_document(self, collection: str, data: Dict[str, Any], document_id: Optional[str] = None) -> str:
        """Add or update a document in Firestore."""
        doc_ref = self.db.collection(collection).document(document_id)
        doc_ref.set(data)
        return doc_ref.id

    def get_all_documents(self, collection: str) -> List[Dict[str, Any]]:
        """Fetch all documents from a Firestore collection."""
        collection_ref = self.db.collection(collection)
        docs = collection_ref.stream()
        return [doc.to_dict() for doc in docs]

    def delete_document(self, collection: str, document_id: str) -> None:
        """Delete a document from Firestore."""
        doc_ref = self.db.collection(collection).document(document_id)
        doc_ref.delete()

    # Firebase Authentication operations
    def create_user(self, email: str, password: str) -> auth.UserRecord:
        """Create a new user in Firebase Authentication."""
        user = auth.create_user(
            email=email,
            password=password
        )
        return user

    def get_user(self, uid: str) -> auth.UserRecord:
        """Get a user by UID."""
        user = auth.get_user(uid)
        return user

    def delete_user(self, uid: str) -> None:
        """Delete a user by UID."""
        auth.delete_user(uid)
