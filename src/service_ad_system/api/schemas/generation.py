"""생성 API 관련 Pydantic 스키마 및 열거형 정의."""

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class InputMode(str, Enum):
    """입력 데이터 모드 유형."""
    TEXT_ONLY = "text_only"
    IMAGE_ONLY = "image_only"
    TEXT_AND_IMAGE = "text_and_image"


class OutputType(str, Enum):
    """생성할 출력 자산 유형."""
    COPY = "copy"
    BANNER = "banner"
    DETAIL_PAGE = "detail_page"
    MENU = "menu"


class JobState(str, Enum):
    """비동기 생성 작업(Job) 상태."""
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class GenerationOptions(BaseModel):
    """광고 생성 시 추가 옵션 및 톤앤매너 설정."""
    store_name: Optional[str] = Field("우리 가게", description="소상공인 매장 이름")
    tone: Optional[str] = Field("친근하고 정성스러운", description="광고 문구 및 이미지 톤앤매너")
    target_audience: Optional[str] = Field("전체", description="타겟 고객층 (예: 2030 직장인, 인근 주민)")
    additional_request: Optional[str] = Field(None, description="추가 요청 사항")


class GenerationRequest(BaseModel):
    """광고 콘텐츠 생성 요청 본문 스키마."""
    text: Optional[str] = Field(None, description="상품 설명 또는 광고 문구용 원본 텍스트")
    outputs: List[OutputType] = Field(
        default=[OutputType.COPY, OutputType.BANNER],
        description="생성하고자 하는 출력물 목록"
    )
    options: GenerationOptions = Field(default_factory=GenerationOptions, description="생성 상세 옵션")


class CopyResult(BaseModel):
    """생성된 광고 문구 결과 데이터."""
    product_summary: str = Field(..., description="상품 요약 설명")
    headline_candidates: List[str] = Field(..., description="헤드라인 문구 후보군")
    body_candidates: List[str] = Field(..., description="본문 광고 문구 후보군")
    cta_candidates: List[str] = Field(..., description="행동 유도(CTA) 버튼 문구 후보군")
    keywords: List[str] = Field(..., description="추천 해시태그 및 키워드 목록")


class SafeArea(str, Enum):
    """텍스트 가독성을 위한 안전 영역(Safe Area) 좌표 규격."""
    pass  # 실제 좌표 데이터는 동적으로 처리되므로 모델에서 딕셔너리 혹은 객체로 사용


class SafeArea(BaseModel):
    x: int = Field(..., description="시작 X 좌표")
    y: int = Field(..., description="시작 Y 좌표")
    width: int = Field(..., description="너비")
    height: int = Field(..., description="높이")


class GeneratedAsset(BaseModel):
    """생성된 시각 자산(이미지, 배너 등) 정보."""
    type: OutputType = Field(..., description="자산 유형")
    url: str = Field(..., description="서빙될 자산 접근 URL 경로")
    width: int = Field(..., description="이미지 너비")
    height: int = Field(..., description="이미지 높이")
    model: str = Field(..., description="사용된 생성 모델명")
    seed: Optional[int] = Field(None, description="이미지 생성 시드값")
    text_safe_area: Optional[SafeArea] = Field(None, description="문구가 삽입될 안전 영역")
    latency_ms: int = Field(..., description="생성 소요 시간 (밀리초)")
    estimated_cost_usd: float = Field(0.0, description="예상 소요 비용 (USD)")


class RunMetrics(BaseModel):
    """실행 성능 및 메트릭 정보."""
    latency_ms: int = Field(..., description="전체 파이프라인 소요 시간 (ms)")
    estimated_cost_usd: float = Field(0.0, description="총 예상 비용")
    copy_model: Optional[str] = Field(None, description="사용한 텍스트 모델")
    image_model: Optional[str] = Field(None, description="사용한 이미지 모델")


class ErrorBody(BaseModel):
    """작업 실패 시 에러 상세 정보."""
    code: str = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")
    details: List[dict[str, Any]] = Field(default_factory=list, description="상세 에러 항목")


class GenerationResult(BaseModel):
    """최종 생성 완료 결과 스키마."""
    mode: InputMode = Field(..., description="입력 모드 (텍스트/이미지 조합)")
    copy: Optional[CopyResult] = Field(None, description="광고 문구 결과")
    assets: List[GeneratedAsset] = Field(default_factory=list, description="생성된 시각 자산 목록")
    metrics: RunMetrics = Field(..., description="실행 메트릭")
    warnings: List[str] = Field(default_factory=list, description="경고 메시지 목록")


class JobStatusResponse(BaseModel):
    """비동기 Job 상태 조회 응답 스키마."""
    request_id: str = Field(..., description="작업 고유 ID")
    state: JobState = Field(..., description="작업 진행 상태 (pending, processing, done, failed)")
    progress: Optional[float] = Field(None, description="진행률 (0.0 ~ 1.0)")
    result: Optional[GenerationResult] = Field(None, description="성공 시 생성 결과물")
    error: Optional[ErrorBody] = Field(None, description="실패 시 에러 정보")
    created_at: float = Field(..., description="생성 요청 시각 (timestamp)")
    finished_at: Optional[float] = Field(None, description="완료/실패 시각 (timestamp)")
