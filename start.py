import sys
import os
import uvicorn

# src 폴더를 파이썬 경로에 강제로 영구 등록합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "service_ad_system", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

if __name__ == "__main__":
    # --reload를 제거하여 경로 증발 원인을 원천 차단합니다.
    uvicorn.run(
        "service_ad_system.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )