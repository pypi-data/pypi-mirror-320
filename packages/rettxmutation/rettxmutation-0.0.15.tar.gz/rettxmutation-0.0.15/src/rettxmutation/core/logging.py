# logging.py
import logging
from logging import StreamHandler, FileHandler


def setup_logging(log_level: int = logging.INFO):
    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            StreamHandler(),
            FileHandler('app.log', encoding='utf-8')
        ]
    )
    logger = logging.getLogger()

    # Set the log level for Azure SDKs to WARNING
    azure_logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
    azure_logger.setLevel(logging.WARNING)

    return logger
