import os
from typing import Any, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "HT SB API"
    API_V1_STR: str = "/api/v1"
    
    # 環境設定
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    OPENAPI_URL: Optional[str] = os.getenv("OPENAPI_URL", "")
    ALLOWED_ORIGINS: Optional[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")

    # JWT認証
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))  # 1日

    # OAuth設定
    GITHUB_CLIENT_ID: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")
    GITHUB_REDIRECT_URI: Optional[str] = os.getenv("GITHUB_REDIRECT_URI")

    FRONTEND_REDIRECT_URL: Optional[str] = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:3000/ht-sb")
    
    # データベース設定
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ht_sb")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    # Redis設定
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    # S3/MinIO設定
    S3_ENDPOINT_URL: Optional[str] = os.getenv("S3_ENDPOINT_URL")  # MinIO用、AWS S3の場合はNone
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    STORAGE_BUCKET_NAME: str = os.getenv("STORAGE_BUCKET_NAME", "ht-sb-bucket")
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # TASUKI
    TASUKI_API_URL: str = os.getenv("TASUKI_API_URL", "https://api.tasuki.io/api/v1")
    TASUKI_API_KEY: str = os.getenv("TASUKI_API_KEY")
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        
        # 環境に基づいてDBのURIを設定
        if self.ENVIRONMENT == "production":
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            # 開発環境ではSQLiteも使用可能
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
            # または: self.SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db"
            
    class Config:
        case_sensitive = True

settings = Settings()