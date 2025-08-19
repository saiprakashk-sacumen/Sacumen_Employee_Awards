from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/awards"
    HUGGINGFACE_TOKEN: str = ""  # optional, only if you login to HuggingFace


    # Jira credentials
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    JIRA_DOMAIN: str = "harshal782002.atlassian.net"  # default value
    PROJECT_KEY: str = "SCRUM"  # default value

settings = Settings()