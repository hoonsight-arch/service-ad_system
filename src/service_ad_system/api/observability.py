from __future__ import annotations

import time
import uuid
from typing import Callable
from fastapi import FastAPI, Request, Response
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.base import BaseHTTPMiddleware

# [수정 포인트] 중복 선언을 막기 위해 자체 Counter/Gauge 선언을 제거하고
# metrics.py에 정의된 메트릭 객체를 가져와서 사용하거나 공유합니다.
from service_ad_system.metrics import JOBS_TOTAL, JOBS_IN_PROGRESS, JOB_DURATION


# =====================================================================
# 1. 관측성 미들웨어 정의 (상관관계 추적 및 로그 노이즈 최적화)
# =====================================================================

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    클라이언트 요청별 X-Request-ID 추적, loguru 컨텍스트 바인딩,
    그리고 /metrics나 /health 같은 반복 호출 엔드포인트의 로그 노이즈를 최적화하는 미들웨어입니다.
    """
    # 로그 노이즈를 줄이기 위해 DEBUG 레벨로 처리할 경로 목록
    NOISE_PATHS = {"/metrics", "/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 1. X-Request-ID 처리 (없으면 12자리 고유 ID 또는 uuid 생성)
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = uuid.uuid4().hex[:12]

        path = request.url.path
        is_noise_path = path in self.NOISE_PATHS

        # 2. loguru contextualize를 활용해 request_id 바인딩
        with logger.contextualize(request_id=request_id):
            start_time = time.perf_counter()

            # 노이즈 경로인 경우 DEBUG 레벨, 일반 API인 경우 INFO 레벨로 로깅
            if is_noise_path:
                logger.debug(f"Incoming probe request: {request.method} {path}")
            else:
                logger.info(f"Incoming request: {request.method} {path}")

            try:
                response = await call_next(request)
                process_time = time.perf_counter() - start_time

                if is_noise_path:
                    logger.debug(
                        f"Completed probe request: {request.method} {path} | "
                        f"Status: {response.status_code} | Duration: {process_time:.4f}s"
                    )
                else:
                    logger.info(
                        f"Completed request: {request.method} {path} | "
                        f"Status: {response.status_code} | Duration: {process_time:.4f}s"
                    )

                # 3. 응답 헤더에 X-Request-ID 주입
                response.headers["X-Request-ID"] = request_id
                return response

            except Exception as exc:
                process_time = time.perf_counter() - start_time
                logger.exception(
                    f"Failed request: {request.method} {path} | "
                    f"Duration: {process_time:.4f}s | Error: {exc}"
                )
                raise


# =====================================================================
# 2. 관측성 설정 통합 함수
# =====================================================================

def setup_observability(app: FastAPI) -> None:
    """FastAPI 앱에 X-Request-ID 미들웨어와 Prometheus Instrumentator를 연동합니다."""
    
    # 1. 미들웨어 등록 (가장 먼저 실행되도록 추가)
    app.add_middleware(ObservabilityMiddleware)

    # 2. Prometheus 메트릭 자동 수집 및 '/metrics' 엔드포인트 노출
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics", "/health", "/docs", "/redoc", "/openapi.json"],
    ).instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=True,
        tags=["Observability"],
    )

    logger.info("Observability setup (Loguru + X-Request-ID + Prometheus) initialized successfully.")