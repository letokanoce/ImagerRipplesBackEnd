from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv(verbose=True)


class Settings(BaseSettings):
    pass


class CommonSettings(Settings):
    APP_NAME: str = Field(..., env="APP_NAME")
    DEBUG_MODE: bool = Field(True, env="DEBUG_MODE")
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(6002, env="PORT")


class MongodbSettings(Settings):
    MONGODB_URI: str = Field(..., env="MONGODB_URI")


class Oss2Settings(Settings):
    OSS_ACCESS_KEY_ID: str = Field(..., env="OSS_ACCESS_KEY_ID")
    OSS_ACCESS_KEY_SECRET: str = Field(..., env="OSS_ACCESS_KEY_SECRET")
    OSS_ENDPOINT: str = Field(..., env="OSS_ENDPOINT")
    OSS_BUCKET_NAME: str = Field(..., env="OSS_BUCKET_NAME")


class RedisSettings(Settings):
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")
    REDIS_PASSWORD: str = Field(..., env="REDIS_PASSWORD")
