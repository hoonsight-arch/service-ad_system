from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# get_db 임포트 추가 (프로젝트 구조에 맞게 경로 확인 필요)
from service_ad_system.database import get_db 
from service_ad_system.services.model_service import model_service

router = APIRouter(prefix="/ai", tags=["AI Inference"])

class PredictRequest(BaseModel):
    text: str = Field(..., description="분석할 텍스트")

@router.post("/predict")
async def run_prediction(payload: PredictRequest, db: AsyncSession = Depends(get_db)):
    try:
        # 비동기 방식으로 모델 추론 실행
        prediction_result = await model_service.predict_async(payload.text)
        return {
            "status": "success",
            "data": prediction_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))