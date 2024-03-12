import datetime as dt
import json
import logging
from typing import override, Optional
import io
import csv
from os import path
from logging import config, Logger
import atexit

"""
Logger setup for project.
To access project logger use @get_logger().
There is a single logger instance for the entire project.
"""

LOG_RECORD_BUILTIN_ATTRS = {
    'args',
    'asctime',
    'created',
    'exc_info',
    'exc_text',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'module',
    'msecs',
    'message',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'stack_info',
    'thread',
    'threadName',
    'taskName',
}

# -------------------------------------------------- INITIALIZATION -------------------------------------------------

# Configuration for logging.
_configuration = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'to_screen': {
            '()': 'logging_config.logger_tools.ToScreenFormatter',
            'fmt_keys': {
                'timestamp': 'timestamp',
                'level': 'levelname',
                'thread_name': 'threadName',
                'module': 'module',
                'function': 'funcName',
                'line': 'lineno',
                'message': 'message',
                'exc_info': 'exc_info'
            }
        },
        'csv': {
            '()': 'logging_config.logger_tools.CsvFormatter',
            'fmt_keys': {
                'timestamp': 'timestamp',
                'level': 'levelname',
                'logger': 'name',
                'thread_name': 'threadName',
                'module': 'module',
                'function': 'funcName',
                'line': 'lineno',
                'message': 'message'
            }
        }
    },
    'filters': {
        'no_errors': {
            '()': 'logging_config.logger_tools.NonErrorFilter'
        }
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'filters': ['no_errors'],
            'formatter': 'to_screen',
            'stream': 'ext://sys.stdout'
        },
        'stderr': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'to_screen',
            'stream': 'ext://sys.stderr'
        },
        'file_csv': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'csv',
            'filename': 'logs/web_server.csv',
            'when': 'midnight',
            'backupCount': 7
        },
        'queue_handler': {
            'class': 'logging.handlers.QueueHandler',
            'handlers': [
                'stdout',
                'stderr',
                'file_csv',
            ],
            'respect_handler_level': True
        }
    },
    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': [
                'queue_handler'
            ]
        }
    }
}

# Path to configuration files.
LOGGING_PATH = 'logs'

# Logging singleton.
_LOGGER: Optional[logging.Logger] = None


# Configure root logger.
def _setup_logging(name: str) -> logging.Logger:

    logging.config.dictConfig(_configuration)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)

    return logging.getLogger(name)


def get_logger() -> logging.Logger:
    global _LOGGER
    if _LOGGER is None:
        _LOGGER = _setup_logging('web_server_logger')
    return _LOGGER


# -------------------------------------------------- FORMATTERS -------------------------------------------------
class CsvFormatter(logging.Formatter):
    def __init__(
            self,
            *,
            fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}
        self.output = io.StringIO()
        self.writer = csv.writer(self.output, quoting=csv.QUOTE_ALL)

    @override
    def format(self, record: logging.LogRecord) -> str:
        return self._prepare_message(record)

    def _prepare_message(self, record: logging.LogRecord) -> str:
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }

        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        # We want the message in this order:
        message_list_keys = ['timestamp', 'level',
                             'thread_name', 'module',
                             'function', 'line', 'message']
        
        if record.exc_info is not None: message_list_keys.append('exc_info')

        message_list_for_csv = []

        for key in message_list_keys:
            if key in message:
                # If "function" == "<module>" the line executed was not within
                # function scope.
                message_list_for_csv.append(message[key])

        self.writer.writerow(message_list_for_csv)  # Write row to self.output
        data = self.output.getvalue()  # Grab data.

        self.output.truncate(0)  # Reset the stream.
        self.output.seek(0)  # Bring pointer to the start of the object's stream.

        return data.replace('\n', ' ').strip()


class ToScreenFormatter(logging.Formatter):
    def __init__(
            self,
            *,
            fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        return self._prepare_message(record)

    def _prepare_message(self, record: logging.LogRecord) -> str:
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        # We want the message in this order:
        message_list_keys = ['timestamp', 'level',
                             'thread_name', 'module',
                             'function', 'line', 'message',
                             'exc_info']

        message_string = f"[{message['timestamp']}] " + \
                         f"{message['level']} " + \
                         f"[{message['thread_name']}] " + \
                         f"[{message['module']}.{message['function']}:{message['line']}] " + \
                         f"{message['message']}"
        
        if record.exc_info is not None:
            messagge_string += ' ' + str(message['exc_info'])

        return message_string.replace('\n', ' ')


class MyJSONFormatter(logging.Formatter):
    def __init__(
            self,
            *,
            fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


# -------------------------------------------------- FILTERS -------------------------------------------------
class NonErrorFilter(logging.Filter):
    # Is the specified record to be logged?
    # False for no, true for yes.
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno < logging.ERROR