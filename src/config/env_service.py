import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class EnvService:
    """Service for managing environment variables."""

    @staticmethod
    def get_lm_studio_base_url() -> str:
        """Get LM Studio API base URL from environment variables."""
        return os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')

    @staticmethod
    def get_lm_studio_api_key() -> str:
        """Get LM Studio API key from environment variables."""
        return os.getenv('LM_STUDIO_API_KEY', 'not-needed')

    @staticmethod
    def get_lm_studio_model() -> str:
        """Get LM Studio model name from environment variables."""
        return os.getenv('LM_STUDIO_MODEL', 'local-model')
