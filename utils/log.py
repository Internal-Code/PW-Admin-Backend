from litestar.logging import LoggingConfig
from config.setting import ENV_FILE, ENVIRONMENT
from utils import get_project_root

LOG_DIR = get_project_root() / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"server-{ENVIRONMENT}.log"

logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": str(LOG_FILE),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "queue_listener": {
            "class": "logging.handlers.QueueHandler",
            "level": "DEBUG",
            "queue": {"()": "queue.Queue", "maxsize": -1},
            "listener": "litestar.logging.standard.LoggingQueueListener",
            "handlers": ["console", "file"],
        },
    },
    log_exceptions="always",
)

logger = logging_config.configure()()
logger.info("Environment: %s  (loaded %s, logging to %s)", ENVIRONMENT, ENV_FILE, LOG_FILE)
