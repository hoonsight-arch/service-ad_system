from openai import OpenAI

#open api key
API_KEY = "OPEN_API_KEY"

print("🔄 OpenAI API 연결 테스트를 시작합니다...")

try:
    client = OpenAI(api_key=OPEN_API_KEY)
    
    # 가장 가볍고 저렴한 text-embedding-3-small 모델로 테스트 요청
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="IP 및 API 키 정상 작동 테스트"
    )
    
    print("\n✅ [성공] API 키가 로컬 PC에서 완벽하게 작동합니다!")
    # 👇 [수정 완료] response.data[0].embedding으로 변경하여 리스트의 첫 번째 요소 지정
    print(f"📦 생성된 임베딩 벡터 차원 수: {len(response.data[0].embedding)}차원")
    print("👉 VM을 쓰지 않고 로컬 PC에서 프로젝트를 진행하셔도 안전합니다.")

except Exception as e:
    error_message = str(e)
    print("\n❌ [실패] API 호출 중 에러가 발생했습니다.")
    print(f"🚨 에러 내용: {error_message}")
    
    if "403" in error_message or "Permission" in error_message:
        print("\n⚠️ [원인 분석] 부트캠프 회사에서 제공한 VM 환경의 IP에서만 접근하도록 보안이 걸려있을 확률이 높습니다. 이 경우 VM을 사용하셔야 합니다.")
    elif "401" in error_message or "Incorrect API key" in error_message:
        print("\n⚠️ [원인 분석] API 키 값이 정확하게 입력되지 않았거나 만료된 키일 수 있습니다. 오타가 없는지 다시 확인해 보세요.")