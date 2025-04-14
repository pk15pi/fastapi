# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Quiz App"
    DATABASE_URL: str = "sqlite:///./quiz.db"
    
    # for mariadb
    # Update this with your actual credentials and database info
    # pip install pymysql
    # DATABASE_URL = "pymysql + mysql://username:password@localhost:3306/quiz"

    # for oracle
    # pip install cx_Oracle  or
    # pip install oracledb
    # DATABASE_URL = "oracle+cx_oracle://username:password@localhost:1521/?service_name=orclpdb1"

    # for ms sql
    # pip install pyodbc
    # With pyodbc and DSN-less connection
    # DATABASE_URL = "mssql+pyodbc://username:password@localhost:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server"

    # for postgresql
    # install psycopg2-binary
    # DATABASE_URL = "postgresql://username:password@localhost:5432/dbname"

    # engine = create_engine(DATABASE_URL)

    # for mongodb
    # pip install pymongo
    # client = MongoClient("mongodb://username:password@localhost:27017/")
    # db = client["your_dbname"]
    # collection = db["your_collection"]

    DEBUG: bool = True


    # for JWT
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_SECRET: str = "your_secret"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
