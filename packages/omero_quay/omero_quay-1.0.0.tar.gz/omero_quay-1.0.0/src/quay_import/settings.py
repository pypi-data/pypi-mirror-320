from __future__ import annotations

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[DJANGO] %(levelname)s %(asctime)s %(module)s "
            "%(name)s.%(funcName)s:%(lineno)s: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
