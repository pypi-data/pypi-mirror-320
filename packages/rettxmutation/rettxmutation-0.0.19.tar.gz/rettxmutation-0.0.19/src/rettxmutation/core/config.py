# config.py
import os
import logging
from threading import Lock


# Setup logging
logger = logging.getLogger(__name__)


class Config:
    _instance = None
    _lock = Lock()

    RETTX_DOCUMENT_ANALYSIS_ENDPOINT: str = ""
    RETTX_DOCUMENT_ANALYSIS_KEY: str = ""
    RETTX_COGNITIVE_SERVICES_ENDPOINT: str = ""
    RETTX_COGNITIVE_SERVICES_KEY: str = ""
    RETTX_OPENAI_KEY: str = ""
    RETTX_OPENAI_MODEL_VERSION: str = ""
    RETTX_OPENAI_ENDPOINT: str = ""
    RETTX_OPENAI_MODEL_NAME: str = ""

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.info("Creating new Config instance...")
                    cls._instance = super(Config, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info("Initializing Config...")
        self.load_secrets()

    def load_secrets(self):
        logger.info("Loading secrets for environment")
        self._load_secrets_from_env()

    def _load_secrets_from_env(self):
        # Azure Document Analysis Configuration
        self.RETTX_DOCUMENT_ANALYSIS_ENDPOINT = os.getenv("RETTX_DOCUMENT_ANALYSIS_ENDPOINT", "")
        self.RETTX_DOCUMENT_ANALYSIS_KEY = os.getenv("RETTX_DOCUMENT_ANALYSIS_KEY", "")
        # Cognitive Services Configuration
        self.RETTX_COGNITIVE_SERVICES_ENDPOINT = os.getenv("RETTX_COGNITIVE_SERVICES_ENDPOINT", "")
        self.RETTX_COGNITIVE_SERVICES_KEY = os.getenv("RETTX_COGNITIVE_SERVICES_KEY", "")
        # OpenAI Configuration
        self.RETTX_OPENAI_KEY = os.getenv("RETTX_OPENAI_KEY", "")
        self.RETTX_OPENAI_MODEL_VERSION = os.getenv("RETTX_OPENAI_MODEL_VERSION", "")
        self.RETTX_OPENAI_ENDPOINT = os.getenv("RETTX_OPENAI_ENDPOINT", "")
        self.RETTX_OPENAI_MODEL_NAME = os.getenv("RETTX_OPENAI_MODEL_NAME", "")
