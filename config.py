from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DATABASE_HOSTNAME : str
    DATABASE_PORT : str
    DATABASE_PASSWORD : str
    DATABASE_NAME : str
    DATABASE_USERNAME : str

    REDIS_URL : str
    SECRET_KEY : str
    ALGORIGTHM : str
    ACCESS_TOKEN_TIME : int

    class Config :
        env_file = ".env"    

settings = Settings()
