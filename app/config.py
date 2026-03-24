import os


class Settings:
    ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    NPPES_BASE_URL: str = "https://npiregistry.cms.hhs.gov/api/"
    APP_TITLE: str = "PrescriberPoint AI Practice Onboarding"

    CORS_ORIGINS: list[str] = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")

    # Classifier LLM — defaults to Qwen on Groq (free tier)
    CLASSIFY_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
    CLASSIFY_BASE_URL: str = os.environ.get(
        "CLASSIFY_BASE_URL", "https://api.groq.com/openai/v1"
    )
    CLASSIFY_MODEL: str = os.environ.get("CLASSIFY_MODEL", "qwen/qwen3-32b")

    LANGFUSE_PUBLIC_KEY: str = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY: str = os.environ.get("LANGFUSE_SECRET_KEY", "")
    LANGFUSE_HOST: str = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")


settings = Settings()
