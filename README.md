# 소상공인 맞춤형 AI 광고 텍스트 생성 서비스 (service_ad_system)
(이태훈 TAE HOON LEE)

초경량 오픈소스 AI 모델(Qwen2.5-0.5B-Instruct)과 FastAPI, Streamlit을 활용하여 local 저사양 환경에서도 소상공인이 손쉽게 매장 홍보 문구와 해시태그를 생성할 수 있는 AI 광고 텍스트 제작 플랫폼입니다.

# 1. 프로젝트 개요 (Overview)
소상공인들이 SNS 마케팅 콘텐츠(인스타그램 홍보 문구, 이벤트 텍스트 등)를 직접 제작하는 데 겪는 시간적·비용적 부담을 줄여주기 위해 기획된 개인 포트폴리오 프로젝트입니다.

하드웨어 제약이 있는 로컬 환경에서도 구동될 수 있게 무거운 멀티모달(이미지) 대신 Huggingface API와 연동하여 초경량 텍스트 생성 모델(Qwen2.5-0.5B-Instruct)을 로컬에 최적화하여 빠르고 안정적인 마케팅 카피 생성 결과를 제공합니다.

# 2. 시스템 아키텍처 및 기술 스택 (Tech Stack)
Backend: FastAPI, Python 3.10+, Uvicorn

Database & ORM: SQLite (비동기 처리), SQLAlchemy (Async)

AI Model: HuggingFace Transformers (Qwen/Qwen2.5-0.5B-Instruct)

Frontend: Streamlit (대시보드 UI)

Observability & Ops: Loguru (구조화된 로깅), Prometheus (메트릭 수집)

# 3. 프로젝트 디렉토리 구조 (Directory Structure)
프로젝트는 유지보수성과 확장성이 뛰어난 src-layout 아키텍처를 채택하고 있습니다.

Plaintext

service_ad_system/

├── alembic/                # 비동기 DB 마이그레이션 환경

├── src/

│   └── service_ad_system/

│       ├── api/            # FastAPI 라우터 설정

│       ├── core/           # 환경 변수 및 설정 관리 (config.py)

│       ├── frontend/       # Streamlit 프론트엔드 대시보드 (app.py)

│       ├── services/       # Qwen 0.5B 모델 추론 서비스 (model_service.py)

│       ├── models/         # SQLAlchemy DB 테이블 모델

│       └── main.py         # FastAPI 애플리케이션 진입점

├── pyproject.toml          # 패키지 및 의존성 관리 설정

└── README.md

# 4. 주요 기능 (Key Features)

AI 맞춤형 광고 텍스트 생성

Qwen/Qwen2.5-0.5B-Instruct 모델을 활용해 업종과 이벤트 내용에 맞춘 트렌디하고 감성적인 마케팅 문구를 생성합니다.

맞춤 해시태그 자동 조합
입력된 매장 이름과 업종을 기반으로 SNS 마케팅에 즉시 활용할 수 있는 해시태그 조합을 실시간으로 제공합니다.

저사양 환경 최적화
불필요한 이미지 생성 모듈을 배제하고 토큰 길이를 최적화(max_new_tokens=60)하여 
로컬 CPU 환경에서도 렉과 다운 현상 없이 쾌적하게 구동됩니다.

# 5. 로컬 실행 및 설치 방법 (Getting Started)

(5-1) 저장소 클론 및 패키지 설치
Bash
git clone <repository-url>
cd service_ad_system
pip install -e .[dev]

(5-2) FastAPI 백엔드 서버 실행
Bash
python -m uvicorn service_ad_system.main:app --reload --port 8000

(5-3) Streamlit 프론트엔드 실행 (새로운 터미널 창)

Bash
streamlit run src/service_ad_system/frontend/app.py --server.port 8501

# 6.향후 업데이트 계획 (Roadmap)
인프라 확장: 단일 프로세스 메모리 한계를 극복하기 위한 Celery + Redis 기반 분산 백그라운드 큐 도입

마케팅 채널 연동: 네이버 스마트스토어, 인스타그램, 페이스북 API를 연동하여 생성된 광고 문구와 이미지를 원클릭으로 자동 업로드 기능 추가

사용자 인증: JWT 기반 로그인 및 소상공인별 API 사용량 관리 기능 구축

# 7.프로젝트 보고서 및 업무일지

본 프로젝트의 기획 배경, 시스템 아키텍처 및 트러블슈팅 내용이 담긴 보고서입니다.

[프로젝트 보고서 확인하기](./docs/소상공인%20맞춤형%20AI%20광고%20서비스(Service_AD_System)%20프로젝트%20보고서%20이태훈.pdf)
### 📊 프로젝트 업무일지 (PDF 보고서)

* [📥 프로젝트 업무일지 PDF 다운로드 및 확인하기](./docs/소상공인%20맞춤형%20AI%20광고%20서비스(Service_AD_System)%20프로젝트%20보고서%20이태훈.pdf)