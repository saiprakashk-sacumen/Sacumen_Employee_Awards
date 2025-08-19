from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    HUGGINGFACE_TOKEN: str = ""

    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    JIRA_DOMAIN: str = "harshal782002.atlassian.net"
    PROJECT_KEY: str = "SCRUM"

    SLACK_BOT_TOKEN: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
