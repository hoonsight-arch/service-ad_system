import os
from typing import Any, Dict
from huggingface_hub import InferenceClient

class HuggingFacePipeline:
    """
    HuggingFace InferenceClient를 활용하여 
    소상공인 맞춤형 광고 문구(텍스트)와 광고 이미지(비주얼)를 생성하는 파이프라인
    """
    def __init__(
        self,
        copy_model: str = None,   # 기본값 비워두기
        image_model: str = None   # 기본값 비워두기
    ):
        # 1. 환경 변수 토큰 확인
        self.token = os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN")
        if not self.token:
            raise ValueError("HF_TOKEN 또는 HF_API_TOKEN 환경 변수가 설정되어 있지 않습니다. 토큰을 확인해주세요.")
            
        # 2. 텍스트 생성 모델 ID (인자가 없으면 .env나 기본값 사용)
        self.copy_model = copy_model or os.getenv("VLM_MODEL_ID", "Qwen/Qwen2.5-7B-Instruct")
        
        # 3. 이미지 생성 모델 ID 
        self.image_model = image_model or os.getenv("IMAGE_MODEL_ID", "stabilityai/stable-diffusion-xl-base-1.0")

        # 4. 확정된 모델 이름으로 클라이언트 초기화
        self.copy_client = InferenceClient(model=self.copy_model, token=self.token)
        self.image_client = InferenceClient(token=self.token)


    async def generate(self, prompt: str, output_dir: str) -> Dict[str, Any]:
        """
        입력된 프롬프트를 바탕으로 광고 카피와 이미지를 비동기로 생성하고 저장합니다.
        """
        # 1. 텍스트 카피 생성 요청 (Qwen2.5 챗 컴완션 활용)
        messages = [{"role": "user", "content": prompt}]
        
        response = self.copy_client.chat_completion(
            messages=messages, 
            max_tokens=500,
            temperature=0.7
        )
        generated_copy = response.choices[0].message.content

        # 2. 이미지 생성 요청 (SDXL 모델 활용)
        image = self.image_client.text_to_image(
            prompt=prompt, 
            model=self.image_model
        )

        # 3. 지정된 output_dir에 이미지 저장
        os.makedirs(output_dir, exist_ok=True)
        image_path = os.path.join(output_dir, "generated_ad.png")
        image.save(image_path)

        return {
            "copy": generated_copy,
            "image_path": image_path
        }


def build_pipeline(copy_provider: str, image_provider: str = "hf"):
    """
    전달받은 copy_provider 설정값에 따라 적절한 AI 파이프라인을 반환합니다.
    """
    provider = copy_provider.lower()
    
    if provider in ["hf", "huggingface"]:
        # 허깅페이스 파이프라인 반환 (모델명 생략 가능)
        return HuggingFacePipeline()
    elif provider == "openai":
        # 기존 OpenAI 파이프라인 반환 로직
        pass
    else:
        raise ValueError(f"지원하지 않는 Provider입니다: {copy_provider}")