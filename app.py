import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from duckduckgo_search import DDGS
import random
import time

# --- 1. 페이지 설정 및 스타일 ---
st.set_page_config(page_title="My Favorite Collage", layout="wide")

# 세션 상태(데이터 저장소) 초기화
if 'collage_items' not in st.session_state:
    st.session_state.collage_items = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 2. 입장 화면 (이름 입력) ---
if not st.session_state.user_name:
    st.markdown("<h1 style='text-align: center;'>🎨 나만의 취향 콜라주 메이커</h1>", unsafe_allow_html=True)
    user_input = st.text_input("당신의 이름을 입력하고 시작하세요!", placeholder="예: 제미니")
    if st.button("콜라주 만들기 시작", use_container_width=True):
        if user_input:
            st.session_state.user_name = user_input
            st.rerun()
    st.stop()

# --- 3. 메인 화면 헤더 ---
st.markdown(f"<h1 style='text-align: center; color: #FF69B4;'>💖 {st.session_state.user_name}님의 최애 콜라주 💖</h1>", unsafe_allow_html=True)

# 왼쪽 조작창 / 오른쪽 미리보기창 분할
col_left, col_right = st.columns([1, 1.2])

# --- 4. 왼쪽: 사진 추가 및 관리 ---
with col_left:
    st.subheader("🛠️ 아이템 추가")
    
    tab1, tab2, tab3 = st.tabs(["📁 직접 업로드", "🔍 이미지 검색", "✨ 스티커"])
    
    # [탭 1] 직접 업로드 (가장 확실한 방법)
    with tab1:
        uploaded_files = st.file_uploader("사진을 선택하세요 (여러 장 가능)", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
        if st.button("업로드 및 배경 제거"):
            if uploaded_files:
                for f in uploaded_files:
                    with st.spinner(f'{f.name} 처리 중...'):
                        img = Image.open(f)
                        nobg = remove(img)
                        st.session_state.collage_items.append({"img": nobg, "name": f.name})
                st.rerun()
            else:
                st.warning("파일을 먼저 선택해주세요!")

    # [탭 2] 이미지 검색 (강화된 버전)
    with tab2:
        search_query = st.text_input("검색어 입력 (예: 짱구, 아이유)", placeholder="검색어를 입력하세요")
        if st.button("검색어로 추가"):
            if search_query:
                with st.spinner('이미지를 찾는 중...'):
                    try:
                        with DDGS() as ddgs:
                            # 차단 방지를 위해 검색 전 대기 및 여러 개 검색 시도
                            time.sleep(1.5)
                            search_results = list
