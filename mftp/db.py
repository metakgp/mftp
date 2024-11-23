import logging
from pymongo import DESCENDING
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Any, Dict, List, Optional
from pymongo.errors import ConnectionFailure


class NoticeDB:
    def __init__(self, config: Optional[Dict[str, Any]] = None, collection_name: str = 'notices') -> None:
        """Initialize MongoDB connector with configuration."""
        self.config = {
            'uri': (config or {}).get('uri', 'mongodb://localhost:27017'),
            'db_name': (config or {}).get('db_name', 'mftp'),
            'max_pool_size': (config or {}).get('max_pool_size', 10),
            'timeout_ms': (config or {}).get('timeout_ms', 5000)
        }
        
        self.db: Optional[Database] = None
        self.client: Optional[MongoClient] = None
        self.logger = logging.getLogger(__name__)

        self.DESCENDING = DESCENDING
        self.collection_name = collection_name

    def connect(self) -> Database | None:
        """Connect to MongoDB and return database instance."""
        try:
            if self.client is None:
                self.client = MongoClient(
                    self.config['uri'],
                    maxPoolSize=self.config['max_pool_size'],
                    serverSelectionTimeoutMS=self.config['timeout_ms']
                )
                # Test the connection
                self.client.admin.command('ping')
                self.db = self.client[self.config['db_name']]
                self.logger.info(f"Successfully connected to MongoDB: {self.config['db_name']}")
            
            return self.db
        except ConnectionFailure as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def add_successful_ntfy_subscriber(self, notice_uid: str, ntfy_topic: str) -> None:
        """
        Add a subscriber to the 'ntfy_last_successful_subscriber_state' document. 
        If the document does not exist, create it.
        """
        uid = f"ntfy_lssl-{notice_uid}"
        collection = self.__get_collection()

        # Check if the document exists
        existing_doc = collection.find_one({"uid": uid})

        if existing_doc is None:
            # Create the document if it doesn't exist
            new_doc = {"uid": uid, "subscribers": [ntfy_topic]}
            collection.insert_one(new_doc)
            return

        # Update the document to add the subscriber if it's not already in the list
        if ntfy_topic not in existing_doc.get("subscribers", []):
            collection.update_one(
                {"uid": uid},
                {"$push": {"subscribers": ntfy_topic}}
            )

    def get_successful_ntfy_subscribers(self, notice_uid: str) -> List[str]:
        """Retrieve the list of subscribers from the 'ntfy_last_successful_subscriber_list' document."""
        uid = f"ntfy_lssl-{notice_uid}"
        collection = self.__get_collection()

        # Retrieve the document
        existing_doc = collection.find_one({"uid": uid})

        # Return the subscribers list or an empty list if the document does not exist
        if existing_doc:
            return existing_doc.get("subscribers", [])
        return []
    
    def delete_successful_ntfy_subscribers(self, notice_uid: str) -> None:
        """Delete the ntfy subscriber list document corresponding to a notice."""
        uid = f"ntfy_lssl-{notice_uid}"
        collection = self.__get_collection()

        # Update the document to set the subscribers list to an empty list
        collection.delete_one({"uid": uid})

    def find_new_notices(self, uid_list: List[str]) -> List[str]:
        """Find and return the list of UIDs that have not been sent."""
        # Query for UIDs that exist in the database
        query = {"UID": {"$in": uid_list}}
        sent_notices = self.__find_many(query, {"UID": 1})

        # Extract UIDs that are already sent
        sent_uids = set()
        if sent_notices:
            sent_uids = {notice["UID"] for notice in sent_notices}

        # Return UIDs that are not sent
        return [uid for uid in uid_list if uid not in sent_uids]
    
    def save_notice(self, document: Dict) -> str:
        return self.__insert_one(document)

    def __get_collection(self) -> Collection:
        """Get MongoDB collection, establishing connection if necessary."""
        if self.db is None:
            self.connect()
        return self.db[self.collection_name]

    # Create operations
    def __insert_one(self, document: Dict) -> str:
        """Insert single document and return inserted ID."""
        collection = self.__get_collection()
        result = collection.insert_one(document)
        return str(result.inserted_id)

    # Read operations
    def __find_many(self, query: Optional[Dict] = None, projection: Optional[Dict] = None) -> Optional[List]:
        """Find and return single document matching query."""
        collection = self.__get_collection()
        return list(collection.find(query or {}, projection))

