from pymongo import MongoClient
from pymongo.errors import PyMongoError

class AtlasMongo():
    def __init__(self, uri: str, db_name: str, collection_name: str):
        """
        Initializes the MongoDB repository class..

        :param uri: MongoDB connection URI (default 'mongodb://localhost:27017/')
        :param db_name: Database name
        :param collection_name: Name of the collection within the database
        """
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        except PyMongoError as e:
            print(f"Error connecting to database: {e}")
            raise

    def create(self, document: dict):
        """
        Inserts a new document into the collection.
        """
        try:
            result = self.collection.insert_one(document)
            return result.inserted_id
        except PyMongoError as e:
            print(f"Error inserting document: {e}")
            return None

    def find(self, query: dict):
        """
        Find documents that match the query.
        """
        try:
            return list(self.collection.find(query))
        except PyMongoError as e:
            print(f"Error when performing the query: {e}")
            return []

    def update(self, query: dict, update_data: dict):
        """
        Update documents that match the query.
        """
        try:
            result = self.collection.update_many(query, {'$set': update_data})
            return result.modified_count
        except PyMongoError as e:
            print(f"Error updating documents: {e}")
            return 0

    def delete(self, query: dict):
        """
        Delete documents that match the query.
        """
        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as e:
            print(f"Error deleting documents: {e}")
            return 0

    def close(self):
        """
        Close the connection to the database.
        """
        self.client.close()