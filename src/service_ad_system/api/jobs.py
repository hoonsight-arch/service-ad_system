from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
from loguru import logger

# 앞서 정의한 Prometheus 관측성 커스텀 메트릭 임포트
try:
    from src.service_ad_system.api.observability import (
        JOBS_TOTAL,
        JOBS_IN_PROGRESS,
        JOB_DURATION,
    )
except ImportError:
    # 단독 테스트 시 메트릭 객체가 없을 경우를 대비한 Mock 정의
    from prometheus_client import Counter, Gauge, Histogram
    JOBS_TOTAL = Counter("service_ad_jobs_total", "Total jobs", ["status", "job_type"])
    JOBS_IN_PROGRESS = Gauge("service_ad_jobs_in_progress", "Jobs in progress", ["job_type"])
    JOB_DURATION = Histogram("service_ad_job_duration_seconds", "Job duration", ["job_type"])


@dataclass
class JobInfo:
    """비동기 작업의 상태 및 메타데이터를 관리하는 데이터클래스"""
    job_id: str
    job_type: str
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class JobStore:
    """
    비동기 작업 상태를 안전하게 관리하는 인메모리 스토어.
    asyncio.Lock을 통한 동시성 제어 및 TTL 기반 만료 데이터 정리(_prune) 기능 제공.
    """
    def __init__(self, ttl_seconds: int = 3600):
        self._jobs: Dict[str, JobInfo] = {}
        self.ttl = ttl_seconds
        self._lock = asyncio.Lock()

    async def _prune(self) -> None:
        """TTL이 지난 오래된 작업 데이터를 메모리에서 정리합니다."""
        now = time.time()
        expired_ids = [
            jid for jid, job in self._jobs.items()
            if (now - job.updated_at) > self.ttl
        ]
        for jid in expired_ids:
            self._jobs.pop(jid, None)
        if expired_ids:
            logger.debug(f"Pruned {len(expired_ids)} expired jobs from JobStore.")

    # =====================================================================
    # 1. 하위 호환성 인터페이스 (기존 단순 딕셔너리 형태 지원)
    # =====================================================================

    def set_job(self, job_id: str, data: Dict[str, Any]) -> None:
        """기존 코드 호환을 위한 동기식 set_job 메서드"""
        self._jobs[job_id] = JobInfo(
            job_id=job_id,
            job_type=data.get("job_type", "default"),
            status=data.get("status", "completed"),
            result=data,
            created_at=time.time(),
            updated_at=time.time(),
        )

    def get_job(self, job_id: str) -> Any:
        """기존 코드 호환을 위한 동기식 get_job 메서드 (data 또는 JobInfo 반환)"""
        job = self._jobs.get(job_id)
        if not job:
            return None
        # 기존 클라이언트가 data 딕셔너리를 기대할 경우를 대비
        if job.result and isinstance(job.result, dict):
            return job.result
        return {
            "job_id": job.job_id,
            "job_type": job.job_type,
            "status": job.status,
            "result": job.result,
            "error": job.error,
        }

    # =====================================================================
    # 2. 고도화된 비동기 상태 관리 인터페이스 (asyncio.Lock 적용)
    # =====================================================================

    async def create_job(self, job_id: str, job_type: str) -> JobInfo:
        async with self._lock:
            await self._prune()
            job = JobInfo(job_id=job_id, job_type=job_type, status="pending")
            self._jobs[job_id] = job
            return job

    async def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        result: Optional[Any] = None,
        error: Optional[str] = None,
    ) -> Optional[JobInfo]:
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            if status:
                job.status = status
            if result is not None:
                job.result = result
            if error is not None:
                job.error = error
            job.updated_at = time.time()
            return job

    async def get_job_info(self, job_id: str) -> Optional[JobInfo]:
        async with self._lock:
            await self._prune()
            return self._jobs.get(job_id)

    # =====================================================================
    # 3. 백그라운드 작업 실행기 (Prometheus 메트릭 연동)
    # =====================================================================

    async def run_job(
        self,
        job_id: str,
        job_type: str,
        target_func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        백그라운드에서 비동기 또는 동기 함수를 실행하고,
        PROMETHEUS 메트릭(진행 중 수, 성공/실패 횟수, 소요 시간)을 자동으로 추적합니다.
        """
        # 1. Job 등록 및 진행 중 게이지 증가
        await self.create_job(job_id, job_type)
        await self.update_job(job_id, status="running")
        
        JOBS_IN_PROGRESS.labels(job_type=job_type).inc()
        start_time = time.perf_counter()

        try:
            logger.info(f"Starting background job | ID: {job_id} | Type: {job_type}")
            
            # 함수가 코루틴(비동기)인지 일반 함수인지 판별하여 실행
            if asyncio.iscoroutinefunction(target_func):
                result = await target_func(*args, **kwargs)
            else:
                # 블로킹 함수일 경우 이벤트 루프 스레드풀에서 실행
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, lambda: target_func(*args, **kwargs))

            # 2. 성공 처리
            duration = time.perf_counter() - start_time
            await self.update_job(job_id, status="completed", result=result)
            
            JOBS_TOTAL.labels(status="success", job_type=job_type).inc()
            JOB_DURATION.labels(job_type=job_type).observe(duration)
            
            logger.info(f"Completed background job | ID: {job_id} | Duration: {duration:.4f}s")

        except Exception as exc:
            # 3. 실패 처리
            duration = time.perf_counter() - start_time
            error_msg = str(exc)
            await self.update_job(job_id, status="failed", error=error_msg)
            
            JOBS_TOTAL.labels(status="failed", job_type=job_type).inc()
            JOB_DURATION.labels(job_type=job_type).observe(duration)
            
            logger.exception(f"Failed background job | ID: {job_id} | Error: {error_msg}")

        finally:
            # 4. 진행 중 게이지 감소
            JOBS_IN_PROGRESS.labels(job_type=job_type).dec()


# 전역 인스턴스 생성 (필요에 따라 모듈별 임포트 가능)
job_store = JobStore()