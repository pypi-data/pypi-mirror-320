import logging
import os
from pythonjsonlogger import jsonlogger
import inspect
from types import FrameType
import logging.config
import logging.handlers
from queue import Queue
from threading import Thread


class Logger:
    logger: logging.Logger = None
    logger_name = "app"
    log_queue: Queue = Queue()
    queue_listener: logging.handlers.QueueListener = None
    environment = os.getenv("ENVIRONMENT", "local")

    def __init__(self, name: str = "app", log_level=logging.INFO):
        self.log_level = log_level
        self.logger_name = name
        self.configure_logging()
        self.start_logging_thread()

    def configure_logging(self):
        try:
            log_level = logging.DEBUG if self.environment == "local" else self.log_level

            simple_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

            handlers = {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": ("logfmt" if self.environment == "local" else "json"),
                    "level": log_level,
                }
            }

            formatters = {
                "logfmt": {"format": simple_format},
                "json": {"()": jsonlogger.JsonFormatter, "format": "%(message)s"},
            }

            logging_config = {
                "version": 1,
                "disable_existing_loggers": False,
                "handlers": handlers,
                "formatters": formatters,
                "root": {
                    "handlers": ["console"],
                    "level": log_level,
                },
            }
            logging.config.dictConfig(logging_config)

            self.logger = logging.getLogger(self.logger_name)

            # Silencing
            self.silence_logs()

        except Exception as e:
            logging.error(f"Error configuring logging: {e}")

    def silence_logs(self):
        urllib3_logger = logging.getLogger("urllib3.connectionpool")
        urllib3_logger.setLevel(logging.WARNING)

        werkzeug = logging.getLogger("werkzeug")
        werkzeug.setLevel(logging.WARNING)

        botocore_logger = logging.getLogger("botocore")
        botocore_logger.setLevel(logging.WARNING)

    def start_logging_thread(self):
        def process_log_queue():
            while True:
                record = self.log_queue.get()
                if record is None:
                    break
                self.log_actual(**record)

        self.logging_thread = Thread(target=process_log_queue)
        self.logging_thread.daemon = True
        self.logging_thread.start()

    def log_actual(
        self,
        message,
        frame: FrameType,
        level=logging.INFO,
        company_id=None,
        employee_id=None,
        request_id=None,
        path=None,
        exception: Exception | None = None,
        **kwargs,
    ):
        try:
            logger = self.logger

            filename = frame.f_globals["__file__"]
            lineno = frame.f_lineno
            func_name = frame.f_code.co_name

            filename = os.path.basename(filename)

            log_record = {
                "request_id": request_id,
                "file": filename,
                "line": lineno,
                "function": func_name,
                "route": path,
                "company_id": company_id,
                "employee_id": employee_id,
                "exception": exception,
            }

            # Add Kwargs to log record
            log_record.update(kwargs)

            log_record = {k: v for k, v in log_record.items() if v is not None}

            if exception is not None:
                if self.environment == "local":
                    message = f"{message} -\n {str(exception)}"
                logger.exception(message, extra=log_record, exc_info=exception)
            else:
                if self.environment == "local":
                    # records = ",".join([f"{k}: {v}" for k, v in log_record.items()])
                    message = f"{message}"
                logger.log(level, msg=message, extra=log_record)

        except Exception as e:
            pass

    def log(
        self,
        message,
        frame: FrameType = None,
        level=logging.INFO,
        company_id=None,
        employee_id=None,
        request_id=None,
        path=None,
        exception: Exception | None = None,
        **kwargs,
    ):
        try:
            frame = inspect.currentframe().f_back if frame is None else frame

            from flask import session, has_request_context

            if has_request_context() and "request_id" in session:
                request_id = session["request_id"]
            else:
                request_id = None

            log_record = {
                "message": message,
                "frame": frame,
                "level": level,
                "company_id": company_id,
                "employee_id": employee_id,
                "request_id": request_id,
                "path": path,
                "exception": exception,
                **kwargs,
            }

            self.log_queue.put(log_record)
        except Exception as e:
            pass

    def error(
        self,
        message,
        company_id=None,
        employee_id=None,
        request_id=None,
        path=None,
        exception: Exception | None = None,
        frame: FrameType = None,
        **kwargs,
    ):
        if not frame:
            frame = inspect.currentframe().f_back
        else:
            frame = frame.f_back
        message = f"🚨 Error: {message}"
        self.log(
            message,
            frame,
            level=logging.ERROR,
            company_id=company_id,
            employee_id=employee_id,
            request_id=request_id,
            path=path,
            exception=exception,
            **kwargs,
        )

    def warning(
        self,
        message,
        company_id=None,
        employee_id=None,
        request_id=None,
        path=None,
        exception: Exception | None = None,
        **kwargs,
    ):
        frame = inspect.currentframe().f_back
        message = f"⚠️ Warning: {message}"
        self.log(
            message,
            frame,
            level=logging.WARNING,
            company_id=company_id,
            employee_id=employee_id,
            request_id=request_id,
            path=path,
            exception=exception,
            **kwargs,
        )

    def info(
        self,
        message,
        company_id=None,
        employee_id=None,
        request_id=None,
        path=None,
        exception: Exception | None = None,
        **kwargs,
    ):
        frame = inspect.currentframe().f_back
        message = f"ℹ️ Info: {message}"
        self.log(
            message,
            frame,
            level=logging.INFO,
            company_id=company_id,
            employee_id=employee_id,
            request_id=request_id,
            path=path,
            exception=exception,
            **kwargs,
        )

    def debug(
        self,
        message,
        company_id=None,
        employee_id=None,
        request_id=None,
        path=None,
        exception: Exception | None = None,
        **kwargs,
    ):
        frame = inspect.currentframe().f_back
        self.log(
            message,
            frame,
            level=logging.DEBUG,
            company_id=company_id,
            employee_id=employee_id,
            request_id=request_id,
            path=path,
            exception=exception,
            **kwargs,
        )

    def critical(
        self,
        message,
        company_id=None,
        employee_id=None,
        request_id=None,
        path=None,
        exception: Exception | None = None,
        **kwargs,
    ):
        frame = inspect.currentframe().f_back
        message = f"🔥 Critical: {message}"
        self.log(
            message,
            frame,
            level=logging.CRITICAL,
            company_id=company_id,
            employee_id=employee_id,
            request_id=request_id,
            path=path,
            exception=exception,
            **kwargs,
        )
