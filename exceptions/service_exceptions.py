# exceptions/service_exceptions.py


class AppBaseException(Exception):
    """所有业务异常的基类"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class ResourceNotFoundError(AppBaseException):
    """资源不存在"""
    def __init__(self, resource: str, id: int):
        super().__init__(message=f"{resource} (id={id}) 不存在", code=404)


class DuplicateNameError(AppBaseException):
    """名称重复"""
    def __init__(self, resource: str, name: str):
        super().__init__(message=f"{resource} 名称 '{name}' 已存在", code=409)


class InvalidOperationError(AppBaseException):
    """非法操作"""
    def __init__(self, message: str):
        super().__init__(message=message, code=400)


class InvalidDecimalError(InvalidOperationError):
    """小数精度超限"""
    def __init__(self, field_name: str, max_places: int = 2):
        super().__init__(message=f"{field_name} 最多支持 {max_places} 位小数")