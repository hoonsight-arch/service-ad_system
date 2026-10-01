from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError as PydanticValidationError


# =====================================================================
# 1. 커스텀 도메인 에러 클래스 정의
# =====================================================================

class APIError(Exception):
    """애플리케이션 전반에서 사용하는 기본 API 에러 클래스"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_SERVER_ERROR",
        details: any = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        super().__init__(self.message)


class ValidationError(APIError):
    """요청 데이터 검증 실패 시 발생하는 에러"""
    def __init__(self, message: str = "Validation error", details: any = None):
        super().__init__(
            message=message,
            status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            details=details,
        )


class ModelUnavailableError(APIError):
    """AI 모델을 로드할 수 없거나 사용할 수 없는 상태일 때 발생하는 에러"""
    def __init__(self, message: str = "AI model is currently unavailable", details: any = None):
        super().__init__(
            message=message,
            status_code=status_code.HTTP_503_SERVICE_UNAVAILABLE,
            code="MODEL_UNAVAILABLE",
            details=details,
        )


class ResourceNotFoundError(APIError):
    """요청한 리소스를 찾을 수 없을 때 발생하는 에러"""
    def __init__(self, message: str = "Requested resource not found", details: any = None):
        super().__init__(
            message=message,
            status_code=status_code.HTTP_404_NOT_FOUND,
            code="RESOURCE_NOT_FOUND",
            details=details,
        )


# =====================================================================
# 2. 예외 핸들러 등록 함수
# =====================================================================

def register_error_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 표준화된 에러 핸들러 및 엔벨로프 응답 파이프라인을 등록합니다."""

    @app.exception_handler(APIError)
    async def custom_api_exception_handler(request: Request, exc: APIError):
        """커스텀 도메인 예외 처리 (APIError 및 하위 클래스)"""
        logger.warning(
            f"API Error occurred | Path: {request.url.path} | "
            f"Code: {exc.code} | Status: {exc.status_code} | Message: {exc.message}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError):
        """FastAPI 기본 Request Body / Query 파라미터 유효성 검증 예외 처리"""
        logger.warning(
            f"Validation Error occurred | Path: {request.url.path} | Errors: {exc.errors()}"
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameters or body.",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: PydanticValidationError):
        """Pydantic 내부 모델 검증 예외 처리"""
        logger.warning(
            f"Pydantic Validation Error occurred | Path: {request.url.path} | Errors: {exc.errors()}"
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "MODEL_VALIDATION_ERROR",
                    "message": "Data validation failed.",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """예상하지 못한 서버 내부 에러 처리 (500 Internal Server Error)"""
        logger.exception(
            f"Uncaught Global Error occurred | Path: {request.url.path} | Error: {exc}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected internal server error occurred.",
                    "details": str(exc) if not app.debug else {"trace": repr(exc)},
                }
            },
        )