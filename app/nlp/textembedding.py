from typing import Any

from transformers import AutoTokenizer, AutoModel


class TextEmbedder:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def generate_embedding(self, input_value: Any):
        input_value = self.tokenizer(input_value, return_tensors="pt", truncation=True, padding=True)
        embedding = self.model(**input_value).last_hidden_state.mean(dim=1).detach().numpy()
        return embedding
