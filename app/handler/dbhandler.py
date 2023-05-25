from app.configuration.dbdriver import MongodbDriver, Oss2Driver


class MongodbHandler:
    # Initialize MongoDB handler
    def __init__(self, db_driver: MongodbDriver, database_name: str, collection_name: str):
        self.client = db_driver.client
        self.collection = self.client[database_name][collection_name]
        print(f"MongodbHandler initialized with database: {database_name}, collection: {collection_name}")

    def query(self, *args, **kwargs):
        # Start a session and execute the query
        with self.client.start_session() as session:
            try:
                query_result = self.collection.find(*args, **kwargs, session=session)
                result = list(query_result)
                print(f"Query executed successfully, found {len(result)} records")
                return result
            except Exception as e:
                print(f"Error occurred while querying: {e}")

    def insert(self, *args, **kwargs):
        # Start a session and execute the insertion
        with self.client.start_session() as session:
            try:
                result = self.collection.insert_many(*args, **kwargs, session=session)
                print(f"{len(result.inserted_ids)} documents inserted successfully")
                return result.inserted_ids
            except Exception as e:
                print(f"Error occurred while inserting documents: {e}")


class Oss2Handler:
    # Initialize Oss2 handler
    def __init__(self, db_driver: Oss2Driver):
        self.bucket = db_driver.bucket
        print("Oss2Handler initialized")

    def generate_img_url(self, key: str, expires_time: int):
        # Generate the signed URL for a given name
        try:
            url = self.bucket.sign_url('GET', key, expires_time)
            print(f"Signed URL generated successfully: {url}")
            return url
        except Exception as e:
            print(f"Error occurred while generating the signed url: {e}")
