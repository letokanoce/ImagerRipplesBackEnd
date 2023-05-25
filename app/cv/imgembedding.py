import requests
from PIL import Image
from transformers import ViTImageProcessor, ViTModel


class ImageEmbedder:
    def __init__(self, model_name: str):
        self.processor = ViTImageProcessor.from_pretrained(model_name)
        self.model = ViTModel.from_pretrained(model_name)

    def generate_embedding(self, image_url: str):
        image = Image.open(requests.get(image_url, stream=True).raw).convert("RGB").resize((384, 384))
        image_features = self.processor(images=image, return_tensors="pt")
        embedding = self.model(image_features.pixel_values).last_hidden_state.mean(dim=1).detach().numpy()
        return embedding
