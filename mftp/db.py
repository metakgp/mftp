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

    # Update operations
    def __update_one(self, filter_dict: Dict, update_dict: Dict, upsert: bool = False) -> Dict:
        """Update single document matching filter."""
        collection = self.__get_collection()
        result = collection.update_one(filter_dict, update_dict, upsert=upsert)
        return {
            'matched_count': result.matched_count,
            'modified_count': result.modified_count,
            'upserted_id': str(result.upserted_id) if result.upserted_id else None
        }

