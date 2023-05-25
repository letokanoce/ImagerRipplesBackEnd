from io import BytesIO

from app.configuration.cache_driver import *
from app.configuration.dbdriver import *
from app.cv.imageinterfernce import ImageInterferer
from app.cv.imgembedding import ImageEmbedder
from app.nlp.textembedding import TextEmbedder

oss2_settings = Oss2Settings()
mongodb_settings = MongodbSettings()
redis_settings = RedisSettings()
buffer_bytes = BytesIO()

oss2_bucket = Oss2Driver(oss2_settings)
mongodb_client = MongodbDriver(mongodb_settings)
redis_client = RedisDriver(redis_settings)
text_embedder = TextEmbedder("bert-base-uncased")
image_embedder = ImageEmbedder("facebook/dino-vitb16")
image_interferer = ImageInterferer([0.68, 0.42], image_embedder, buffer_bytes)
