"""
This file contains commonly used pydantic models.
"""

from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel
from uniteampckg.constants.error_constant import ErrorCode

# This is a Generic type that can be used to define a type that is a
# subclass of BaseModel
DataT = TypeVar("DataT", bound=BaseModel)


class FunctionResp(BaseModel, Generic[DataT]):
    """
    TODO
    """

    status: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    response_type: Optional[str] = None
    data: Optional[DataT] = (
        # This DataT type can be defined as ex. FunctionResp[UserModel] or
        # FunctionResp[str]
        None
    )
    status_code: Optional[int] = None

    class Config:
        """
        TODO
        """

        arbitrary_types_allowed = True


class PaginationModel(BaseModel):
    """
    TODO
    """

    take: Optional[int] = None
    skip: Optional[int] = None
    totalElements: Optional[int] = None


class BaseResponse(BaseModel):
    """
    Base response model
    """

    status: bool
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    data: Optional[Any] = None
    pagination: Optional[PaginationModel] = None


class CustomException(Exception):
    def __init__(
        self,
        error_code: Optional[str] = ErrorCode.INTERNAL_SERVER_ERROR,
        error_message: Optional[str] = "",
        status_code: Optional[int] = 500,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.status_code = status_code
        super().__init__(self.error_message)
