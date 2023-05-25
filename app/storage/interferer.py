import random

import numpy as np
from bson.objectid import ObjectId

from app.cv.imageinterfernce import ImageInterferer
from app.handler.dbhandler import MongodbHandler, Oss2Handler


class RippleInterferer:
    def __init__(self, mongodb_handler: MongodbHandler, oss2_handler: Oss2Handler):
        self.mongodb_handler = mongodb_handler
        self.oss2_handler = oss2_handler

    def wave_collapse(self, img_id_1: str, img_id_2: str, image_interferer: ImageInterferer):
        try:
            # Create MongoDB filter and projection
            projection = {"_id": True, "name": True, "label": True, "strength": True}

            chosen_doc_1 = self.mongodb_handler.query(filter={"_id": ObjectId(img_id_1)}, projection=projection)[0]
            chosen_doc_2 = self.mongodb_handler.query(filter={"_id": ObjectId(img_id_2)}, projection=projection)[0]

            img_url_1 = self.oss2_handler.generate_img_url(chosen_doc_1['name'], 120)
            img_url_2 = self.oss2_handler.generate_img_url(chosen_doc_2['name'], 120)

            interference_result = image_interferer.generate_interference(img_url_1, img_url_2)

            if interference_result is True:
                return True
            elif interference_result is False:
                return False
            else:
                # Create interfered document
                return self._create_interfered_doc(chosen_doc_1, chosen_doc_2, interference_result, image_interferer)
        except Exception as e:
            print(f"Error occurred while processing: {e}")

    def _create_interfered_doc(self, doc_1, doc_2, interference_result, image_interferer: ImageInterferer):
        document_count = self.mongodb_handler.collection.count_documents({})
        new_doc_name = f"image{(document_count + 1):03}.jpg"
        combined_doc_label = doc_1["label"] + doc_2["label"]
        random.shuffle(combined_doc_label)
        truncated_length = random.randint(1, len(combined_doc_label))
        truncated_list = combined_doc_label[:truncated_length]

        self.oss2_handler.bucket.put_object(new_doc_name, interference_result)
        new_img_url = self.oss2_handler.generate_img_url(new_doc_name, 120)

        combined_doc_strength = np.array([doc_1["strength"], doc_2["strength"]])
        new_doc_strength = round(float(np.dot(image_interferer.weights, combined_doc_strength)), 4)

        new_doc = [{"name": new_doc_name, "label": truncated_list, "strength": new_doc_strength}]
        new_doc_id = self.mongodb_handler.insert(new_doc)[0]
        new_doc = self.mongodb_handler.query(filter={"_id": new_doc_id},
                                             projection={"_id": True, "name": True, "label": True})
        result = [{**doc, "_id": str(doc["_id"]), "address": new_img_url} for doc in new_doc]
        return result
