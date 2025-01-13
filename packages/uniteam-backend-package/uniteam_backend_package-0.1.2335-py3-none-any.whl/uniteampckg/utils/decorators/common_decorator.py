import json
from pydantic import ValidationError
from uniteampckg.constants.error_constant import ErrorCode
from uniteampckg.models.base_models import CustomException, FunctionResp, BaseResponse
from functools import wraps

import inspect
from uniteampckg.utils.logging.logger import Logger

logger = Logger("common_decorator")
logger.configure_logging()


def handle_route_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except ValidationError as error:
            logger.error(f"Validation Error", exception=error)
            return (
                BaseResponse(
                    status=False,
                    error_code=ErrorCode.INVALID_REQUEST,
                ).model_dump(),
                400,
            )

        except Exception as error:
            logger.error(f"Internal Server Error", exception=error)
            return (
                BaseResponse(
                    status=False,
                    error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                ).model_dump(),
                500,
            )

    return decorated_function


def handle_function_exception(f):
    """
    Used to handle exceptions in functions, and return a FunctionResp object
    Return CustomException object if the error is a CustomException
    Return ValidationError object if the error is a ValidationError
    Return Internal Server Error if the error is any other exception

    Every error is logged with stack trace
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except ValidationError as error:
            frame = inspect.currentframe().f_back.f_back
            logger.error(f"ValidationError Error", exception=error)
            return FunctionResp(
                status=False,
                error_code=ErrorCode.INVALID_REQUEST,
            )

        except CustomException as error:
            frame = inspect.currentframe().f_back.f_back
            logger.error(f"CustomException Error", exception=error, frame=frame)
            return FunctionResp(
                status=False,
                error_code=error.error_code,
                error_message=error.error_message,
            )

        except Exception as error:
            frame = inspect.currentframe().f_back.f_back
            logger.error(f"Internal Server Error", exception=error)
            return FunctionResp(
                status=False,
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            )

    return decorated_function
