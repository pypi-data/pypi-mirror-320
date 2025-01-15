from datetime import datetime
from typing import Generic, TypeVar, Optional, List

from mag_tools.exception.app_exception import AppException
from mag_tools.model.service_status import ServiceStatus

T = TypeVar('T')

class Results(Generic[T]):
    def __init__(self, status: Optional[ServiceStatus] = ServiceStatus.OK, code: Optional[ServiceStatus] = ServiceStatus.OK,
                 message: Optional[str] = None, data: Optional[List[T]] = None):
        self.status = status.value if status else ServiceStatus.OK.value
        self.code = code.value if code else ServiceStatus.OK.value
        self.message = message if message else status.reason
        self.timestamp = datetime.now()
        self.data = data if data else []
        self.total_count = len(self.data)

    @staticmethod
    def exception(ex: Exception) -> 'Results':
        message = str(ex) if ex.args else str(ex.__cause__)
        return Results(status=ServiceStatus.INTERNAL_SERVER_ERROR, code=ServiceStatus.INTERNAL_SERVER_ERROR, message=message)

    @staticmethod
    def success(data: Optional[List[T]] = None) -> 'Results':
        return Results(message="OK", data=data)

    @staticmethod
    def fail(message: str) -> 'Results':
        return Results(code=ServiceStatus.INTERNAL_SERVER_ERROR, message=message)

    @staticmethod
    def unauthorized(message: str) -> 'Results':
        return Results(status=ServiceStatus.UNAUTHORIZED, code=ServiceStatus.UNAUTHORIZED, message=message)

    @staticmethod
    def forbidden(message: str) -> 'Results':
        return Results(status=ServiceStatus.FORBIDDEN, code=ServiceStatus.FORBIDDEN, message=message)

    def is_success(self) -> bool:
        return self.status == ServiceStatus.OK.value and self.code == ServiceStatus.OK.value

    def check(self) -> None:
        if not self.is_success():
            raise AppException(self.message)

    def size(self) -> int:
        return len(self.data)

    def get(self, idx: int) -> Optional[T]:
        self.check()
        return self.data[idx] if idx < self.size() else None

    def data(self) -> List[T]:
        return self.data