import asyncio
import torch
from transformers import pipeline


class ModelService:

  def __init__(self):
    print("Loading lightweight Qwen AI model (0.5B)...")
    self.device = 0 if torch.cuda.is_available() else -1

    model_id = "Qwen/Qwen2.5-0.5B-Instruct"

    try:
      self.generator = pipeline(
          "text-generation",
          model=model_id,
          device=self.device,
          torch_dtype=torch.float32,
      )
      print("Qwen 0.5B Model loaded successfully!")
    except Exception as e:
      print(f"Model load error: {e}")
      self.generator = None

  def predict(self, text: str) -> dict:
    if not self.generator:
      return {
          "input_text": text,
          "copy": f"시스템 대체 응답: {text}",
          "status": "error",
      }

    prompt = f"광고 카피를 짧고 매력적으로 작성해줘.\n요청: {text}\n카피:"

    # 토큰 제한을 최소화하여 연산 속도 극대화
    outputs = self.generator(prompt, max_new_tokens=60, do_sample=False)

    generated_text = outputs[0]["generated_text"]
    return {
        "input_text": text,
        "copy": generated_text.strip(),
        "status": "success" if generated_text else "error",
    }

  async def predict_async(self, text: str) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, self.predict, text)


model_service = ModelService()