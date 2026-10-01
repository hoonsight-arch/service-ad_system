"""FastAPI 앱 팩토리.

실행: ``PYTHONPATH=service_ad_system/src python -m uvicorn service_ad_system.main:app --reload --port 8000``
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from service_ad_system.api.errors import register_error_handlers
from service_ad_system.api.jobs import JobStore
from service_ad_system.api.observability import setup_observability
from service_ad_system.api.pipeline import build_pipeline
from service_ad_system.core.config import get_settings
from service_ad_system.routers import api_router, generate_router
from service_ad_system.utils.logging import configure_logging
from service_ad_system.database import get_db
from service_ad_system.services.model_service import model_service

def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="소상공인 맞춤형 광고 문구·이미지 생성 API",
    )

    origins = settings.cors_origins
    allow_all = origins == ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=not allow_all,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 공유 상태: job 저장소와 파이프라인
    app.state.job_store = JobStore(ttl_seconds=settings.job_ttl_seconds)
    app.state.pipeline = build_pipeline(settings.copy_provider, settings.image_provider)
    app.state.background_tasks = set()

    register_error_handlers(app)
    setup_observability(app)  # /metrics, request_id, 요청 로깅
    
    # 라우터 등록
    app.include_router(api_router)
    app.include_router(generate_router)
    
    return app

app = create_app()