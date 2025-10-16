import boto3
import json
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from botocore.exceptions import ClientError
from urllib.parse import quote_plus


class BaseConfig(BaseSettings):
    # Application settings
    ENV_STATE: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class GlobalConfig(BaseConfig):
    # AWS Settings
    AWS_REGION: Optional[str] = None
    USE_AWS_SECRETS: bool = True
    AWS_SECRET_NAME: Optional[str] = None

    # Database connection components (for building URL)
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = None

    # Database settings
    DATABASE_URL: Optional[str] = None
    DB_ECHO: bool = False

    def get_database_url(self) -> str:
        # Option 1: Complete DATABASE_URL
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # Option 2: Individual components
        if self.DB_USER and self.DB_PASSWORD:
            password = quote_plus(self.DB_PASSWORD)

            return (
                f"postgresql://{self.DB_USER}:{password}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

        # Option 3: AWS Secrets Manager
        if self.USE_AWS_SECRETS and self.AWS_SECRET_NAME:
            credentials = self._get_secret_from_aws()
            return self._build_database_url(credentials)

        raise ValueError(
            "Database configuration not properly set. Provide DATABASE_URL, AWS credentials, or individual DB components."
        )

    def _get_secret_from_aws(self) -> dict:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name="secretsmanager",
            region_name=self.AWS_REGION,
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=self.AWS_SECRET_NAME
            )
        except ClientError as e:
            raise Exception(f"Failed to retrieve database credentials: {str(e)}")

        # Parse the secret string
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
            return json.loads(secret)
        else:
            raise ValueError("Secret is not in string format")

    def _build_database_url(self, credentials: dict) -> str:
        username = credentials.get("username")
        password = quote_plus(credentials.get("password"))
        host = credentials.get("host", self.DB_HOST)
        port = credentials.get("port", self.DB_PORT)
        dbname = credentials.get("dbname", self.DB_NAME)

        if not username or not password:
            raise ValueError("Username and password must be provided in AWS secret")

        return f"postgresql://{username}:{password}@{host}:{port}/{dbname}"


class DevConfig(GlobalConfig):
    # Database settings
    DB_ECHO: bool = True

    model_config = SettingsConfigDict(env_prefix="DEV_", env_file=".env")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_", env_file=".env")


class TestConfig(GlobalConfig):
    # AWS Settings
    USE_AWS_SECRETS: bool = False

    # Database settings
    DB_ECHO: bool = True

    model_config = SettingsConfigDict(env_prefix="TEST_", env_file=".env")


@lru_cache()
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)
