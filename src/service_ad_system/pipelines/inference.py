import os
from huggingface_hub import InferenceClient

class HuggingFacePipeline:
    def __init__(self, copy_model: str = "Qwen/Qwen2.5-7B-Instruct", image_model: str = "stabilityai/stable-diffusion-xl-base-1.0"):
        self.token = os.getenv("HF_TOKEN")
        self.copy_client = InferenceClient(model=copy_model, token=self.token)
        # 이미지나 텍스트 추론 호출

    async def generate(self, data, output_dir):
        # 1. 텍스트 카피 생성 요청
        # 2. 이미지 생성 요청 및 output_dir에 저장
        pass