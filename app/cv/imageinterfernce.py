from io import BytesIO

import numpy as np
import requests
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

from app.cv.imgembedding import ImageEmbedder


class ImageInterferer:
    def __init__(self, weights: list, image_embedder: ImageEmbedder, buffer_bytes: BytesIO):
        self.weights = np.array(weights)
        self.image_embedder = image_embedder
        self.image_bytes = buffer_bytes

    def generate_interference(self, img_url_1: str, img_url_2: str):
        try:
            image_1 = self._load_image(img_url_1)
            image_2 = self._load_image(img_url_2)

            image_embedding_1 = self.image_embedder.generate_embedding(img_url_1)
            image_embedding_2 = self.image_embedder.generate_embedding(img_url_2)

            image_similarity = cosine_similarity(image_embedding_1, image_embedding_2)[0][0]
            print(f"Compared similarity when interfering is {image_similarity}.")

            if image_similarity > 0.95:
                return True
            elif image_similarity < 0.928:
                return self._get_interfered_image(image_1, image_2)
            else:
                return False

        except (requests.exceptions.RequestException, IOError) as e:
            print(f"Error occurred while processing the images: {str(e)}")
            return None

    @staticmethod
    def _load_image(img_url: str):
        response = requests.get(img_url, stream=True)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB").resize((384, 384))
        return image

    def _get_interfered_image(self, image_1: Image, image_2: Image):
        img_array_1 = np.array(image_1).flatten()
        img_array_2 = np.array(image_2).flatten()

        new_image_array = np.dot(self.weights, [img_array_1, img_array_2])
        reshaped_img_array = new_image_array.reshape(np.array(image_1).shape)

        new_image = Image.fromarray(reshaped_img_array.astype('uint8')).convert('RGB')
        new_image.save(self.image_bytes, format='JPEG')
        self.image_bytes.seek(0)
        new_image_data = self.image_bytes.read()

        return new_image_data
