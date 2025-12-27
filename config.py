from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DATABASE_URL:str
    REDIS_URL : str
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_TIME : int

    class Config :
        env_file = ".env"    

settings = Settings()
