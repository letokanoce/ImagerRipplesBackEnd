import random
from typing import List, Any

from bson.objectid import ObjectId
from sklearn.metrics.pairwise import cosine_similarity

from app.cv.imgembedding import ImageEmbedder
from app.handler.cache_handler import RedisHandler
from app.handler.dbhandler import MongodbHandler, Oss2Handler
from app.nlp.textembedding import TextEmbedder


class RippleQuerier:
    def __init__(self, mongodb_handler: MongodbHandler, oss2_handler: Oss2Handler, redis_handler: RedisHandler):
        self.mongodb_handler = mongodb_handler
        self.oss2_handler = oss2_handler
        self.redis_handler = redis_handler

    def fuzzy_search(self, keywords: List[Any]):
        try:
            # Create MongoDB filter and projection
            query_filter = {"label": {"$all": keywords}}
            projection = {"_id": True, "name": True, "label": True, "strength": True}

            # Perform query, shuffle it
            orig_search_result = self.mongodb_handler.query(filter=query_filter, projection=projection)
            random.shuffle(orig_search_result)

            # Get the image URL for each item
            result = [{**doc, "_id": str(doc["_id"]),
                       "address": self.oss2_handler.generate_img_url(doc["name"], 120)} for doc in
                      orig_search_result][:4]

            print(f"Top n search results: {result}.")
            return result
        except Exception as e:
            print(f"Error in searching process: {e}")

    def get_similar_img(self, img_id: str, text_embedder: TextEmbedder, image_embedder: ImageEmbedder):
        try:
            # self.redis_handler.clear()
            # Get the chosen document and generate embeddings for it
            query_filter = {"_id": ObjectId(img_id)}
            chosen_doc = (self.mongodb_handler.query(filter=query_filter,
                                                     projection={"_id": True, "name": True, "label": True}))[0]
            chosen_label_embedding = text_embedder.generate_embedding(chosen_doc["label"])
            chosen_image_embedding = image_embedder.generate_embedding(
                self.oss2_handler.generate_img_url(chosen_doc["name"], 120))

            projection = {"_id": True, "name": True, "label": True, "strength": True}

            selected_docs = [doc for doc in self.mongodb_handler.query(projection=projection) if (
                    (doc["_id"] != chosen_doc["_id"]) and
                    (float(cosine_similarity(chosen_label_embedding,
                                             text_embedder.generate_embedding(doc["label"]))[0][0]) > 0.805))]
            print(f"Finding {len(selected_docs)} similar images")
            # Calculate image similarity for each document
            docs_similarity = []
            for doc in selected_docs:
                cache_key = f"{max(doc['_id'], chosen_doc['_id'])}-{min(doc['_id'], chosen_doc['_id'])}"
                cache_value = self.redis_handler.get_from_redis(cache_key)

                # If not cached, calculate and store image similarity
                if cache_value is None:
                    doc_image_embedding = image_embedder.generate_embedding(
                        self.oss2_handler.generate_img_url(doc["name"], 120))
                    print("doc image embedding is ready!")
                    image_similarity = cosine_similarity(chosen_image_embedding, doc_image_embedding)[0][0]
                    print("begin to set to cache")
                    self.redis_handler.set_to_redis(cache_key,
                                                    {"source": str(chosen_doc["_id"]),
                                                     "similarity": float(image_similarity)})
                else:
                    image_similarity = float(cache_value["similarity"])

                docs_similarity.append((doc, float(image_similarity)))

            # Generate final results with documents info
            result = sorted(
                [{
                    **doc, "_id": str(doc["_id"]),
                    "address": self.oss2_handler.generate_img_url(doc["name"], 120),
                    "similarity": {"source": str(chosen_doc["_id"]), "value": similarity_value}}
                    for doc, similarity_value in docs_similarity],
                key=lambda x: x["similarity"]["value"], reverse=True)[:8]

            print(f"Similar image results: {result}.")
            return result
        except Exception as e:
            print(f"Error in finding similar images process: {e}")
