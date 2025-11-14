from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PAI-MHC API"
    mongodb_uri: str = "mongodb://localhost:27017/"
    mongodb_db: str = "pai_mhc_db"
    jwt_secret: str = "change_me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


