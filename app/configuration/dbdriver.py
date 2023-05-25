from abc import ABC, abstractmethod
from typing import TypeVar

import oss2
from pymongo.mongo_client import MongoClient

from app.configuration.configs import Settings, MongodbSettings, Oss2Settings

# Define Type Variable T bounded by Settings class
T = TypeVar("T", bound=Settings)


class DbConnection(ABC):
    # Abstract Base Class for generic Database Connections
    def __init__(self, settings: T):
        self.settings = settings

    @abstractmethod
    def set_connection(self):
        pass

    @abstractmethod
    def close_connection(self):
        pass


class MongodbDriver(DbConnection):

    def __init__(self, settings: MongodbSettings):
        super().__init__(settings)
        self.client = self.set_connection()

    def set_connection(self):
        # Set up a MongoDB connection
        try:
            client = MongoClient(self.settings.MONGODB_URI)
            if client.admin.command('ping'):
                print(f"MongoDB connection set successfully!")
            return client
        except Exception as e:
            print(f"Error occurred while setting up MongoDB connection: {e}")

    def close_connection(self):
        # Close the MongoDB connection
        try:
            self.client.close()
            print("MongoDB connection closed successfully!")
        except Exception as e:
            print(f"Error occurred while closing MongoDB connection: {e}")


class Oss2Driver(DbConnection):

    def __init__(self, settings: Oss2Settings):
        super().__init__(settings)
        self.bucket = self.set_connection()

    def set_connection(self):
        # Set up a OSS2 connection
        try:
            auth = oss2.Auth(self.settings.OSS_ACCESS_KEY_ID, self.settings.OSS_ACCESS_KEY_SECRET)
            bucket = oss2.Bucket(auth, self.settings.OSS_ENDPOINT, self.settings.OSS_BUCKET_NAME, connect_timeout=30)
            if bucket.get_bucket_info():
                print(f"OSS bucket connection set successfully!")
            return bucket
        except oss2.exceptions.OssError as e:
            print(f"Error occurred while connecting to OSS bucket: {e}")

    def close_connection(self):
        print("OSS connection closed successfully!")
