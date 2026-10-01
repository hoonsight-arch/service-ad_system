from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from service_ad_system.database import get_db
from service_ad_system.services.model_service import model_service

router = APIRouter(prefix="/generate", tags=["Ad Generation"])


class AdGenerateRequest(BaseModel):
  product_name: str = Field(..., description="매장 이름 또는 업종")
  prompt: str = Field(..., description="이벤트 및 홍보 내용")
  sns_platform: str = Field("일반 마케팅", description="광고 활용 매체")


@router.post("/content")
async def generate_ad_content(
    payload: AdGenerateRequest, db: AsyncSession = Depends(get_db)
):
  try:
    input_text = (
        f"매장/상품 이름: {payload.product_name}\n이벤트 내용:"
        f" {payload.prompt}"
    )
    result = await model_service.predict_async(input_text)
    return {
        "status": "success",
        "sns_platform": payload.sns_platform,
        "data": result,
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))