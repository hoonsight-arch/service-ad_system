import requests
import streamlit as st

st.set_page_config(page_title="소상공인 AI 광고 생성기", page_icon="🛍️", layout="centered")

st.title("🛍️ 소상공인 맞춤형 AI 광고 텍스트 생성기")
st.write(
    "Qwen 오픈소스 AI를 활용해 매장 홍보 문구와 해시태그를 빠르게 생성합니다."
)

# 사용자 입력 섹션
with st.form("ad_form"):
  st.subheader("📝 광고 기획 정보 입력")
  business_type = st.text_input(
      "업종 및 매장 이름", "우리 동네 수제 베이커리 '달콤샌드'"
  )
  target_audience = st.text_input("타겟 고객층", "인근 직장인 및 2030 데이트족")
  event_details = st.text_area(
      "홍보 내용 및 이벤트 설명",
      "신메뉴 출시 기념 아메리카노 1+1 및 샌드위치 10% 할인 이벤트 진행 중!",
  )

  submitted = st.form_submit_button("✨ Qwen AI 맞춤형 광고 생성하기")

API_BASE_URL = "http://127.0.0.1:8000"

if submitted:
  if not business_type.strip() or not event_details.strip():
    st.warning("모든 항목을 입력해주세요!")
  else:
    with st.status(
        "🚀 Qwen AI가 홍보 카피를 작성 중입니다...", expanded=True
    ) as status:
      try:
        response = requests.post(
            f"{API_BASE_URL}/generate/content",
            json={
                "product_name": business_type,
                "prompt": f"[타겟층: {target_audience}] {event_details}",
                "sns_platform": "일반 마케팅",
            },
        )

        if response.status_code != 200:
          st.error(f"서버 요청 실패: {response.text}")
          status.update(label="생성 실패", state="error", expanded=True)
          st.stop()

        res_data = response.json()
        final_result = res_data.get("data", {})

        status.update(
            label="✨ 광고 텍스트 제작 완료!", state="complete", expanded=False
        )

      except Exception as e:
        st.error(
            f"서버와 통신할 수 없습니다. 백엔드 실행 상태를 확인하세요. (에러: {e})"
        )
        status.update(label="통신 에러", state="error", expanded=True)

    if "final_result" in locals() and final_result:
      st.divider()
      st.success("🎉 소상공인 맞춤형 광고 패키지가 완성되었습니다!")

      # 탭을 나누어 깔끔하게 텍스트와 해시태그만 출력
      tab1, tab2 = st.tabs(["📱 생성된 광고 카피", "🏷️ 추천 해시태그"])

      with tab1:
        st.subheader("최적화 홍보 문구")
        ai_copy = final_result.get("copy", "생성된 문구가 없습니다.")
        st.text_area("Qwen AI 생성 결과", ai_copy, height=200)

      with tab2:
        st.subheader("맞춤 해시태그 조합")
        hashtags = f"#{business_type.replace(' ', '')} #소상공인마케팅 #신메뉴할인 #동네맛집추천 #이벤트중"
        st.code(hashtags, language="text")