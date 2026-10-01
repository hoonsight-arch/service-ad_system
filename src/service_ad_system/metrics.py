from __future__ import annotations

from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram, REGISTRY
from prometheus_fastapi_instrumentator import Instrumentator


# =====================================================================
# 1. 생성 Job 관련 Prometheus 커스텀 지표(Metrics) 정의 (중복 등록 방지 적용)
# =====================================================================

# 1) JOBS_TOTAL: 처리된 총 생성 Job 수 (상태 및 작업 유형별 집계)
try:
    JOBS_TOTAL = Counter(
        "service_ad_jobs_total",
        "Total number of generation jobs processed by the system",
        ["status", "job_type"],  # 예: status="success|failed", job_type="text|image|banner 등"
    )
except ValueError:
    # 이미 레지스트리에 등록된 경우 기존 메트릭을 재사용
    JOBS_TOTAL = REGISTRY._names_to_collectors.get("service_ad_jobs_total")


# 2) JOBS_IN_PROGRESS: 현재 진행 중인 생성 Job 수 (동시성 및 부하 모니터링용)
try:
    JOBS_IN_PROGRESS = Gauge(
        "service_ad_jobs_in_progress",
        "Number of generation jobs currently in progress",
        ["job_type"],
    )
except ValueError:
    JOBS_IN_PROGRESS = REGISTRY._names_to_collectors.get("service_ad_jobs_in_progress")


# 3) JOB_DURATION: 생성 Job 처리 소요 시간 (히스토그램, 버킷 세분화)
try:
    JOB_DURATION = Histogram(
        "service_ad_job_duration_seconds",
        "Duration of generation jobs in seconds",
        ["job_type"],
        buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
    )
except ValueError:
    JOB_DURATION = REGISTRY._names_to_collectors.get("service_ad_job_duration_seconds")


# =====================================================================
# 2. 관측성(Prometheus) 설정 통합 함수
# =====================================================================

def setup_observability(app: FastAPI) -> None:
    """FastAPI 애플리케이션에 Prometheus 메트릭 수집 도구를 연동하고,
    '/metrics' 엔드포인트를 통해 시스템 성능 및 요청 지표를 노출한다.
    """
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untandled=True,
        excluded_handlers=["/metrics", "/docs", "/redoc", "/openapi.json"],
    ).instrument(app).expose(
        app, 
        endpoint="/metrics", 
        include_in_schema=True, 
        tags=["Observability"],
    )