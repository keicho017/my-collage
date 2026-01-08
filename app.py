import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from duckduckgo_search import DDGS
import random
import time

# --- 1. 페이지 설정 (모바일 최적화) ---
st.set_page_config(page_title="최애 콜라주", layout="centered")

if 'collage_items' not in st.session_state:
    st.session_state.collage_items = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'target_idx' not in st.session_state:
    st.session_state.target_idx = 0

# --- 2. 입장 화면 ---
if not st.session_state.user_name:
    st.markdown("<h2 style='text-align: center;'>✨ 나만의 최애 콜라주 ✨</h2>", unsafe_allow_html=True)
    user_input = st.text_input("이름을 입력해주세요", placeholder="예: 제미니")
    if st.button("시작하기", use_container_width=True):
        if user_input:
            st.session_state.user_name = user_input
            st.rerun()
    st.stop()

# --- 3. 아이템 추가 섹션 ---
st.subheader("🛠️ 아이템 추가")
tab1, tab2, tab3 = st.tabs(["📁 업로드", "🔍 검색", "✨ 스티커"])

with tab1:
    files = st.file_uploader("사진 선택", accept_multiple_files=True, type=['jpg', 'png'])
    if st.button("사진 추가", use_container_width=True):
        for f in files:
            with st.spinner('배경 제거 중...'):
                img = Image.open(f)
                nobg = remove(img)
                st.session_state.collage_items.append({
                    "img": nobg, "name": f.name, "x": 100, "y": 200, "size": 300
                })
        st.rerun()

with tab2:
    query = st.text_input("검색어 입력")
    if st.button("이미지 검색 및 추가", use_container_width=True):
        with st.spinner('검색 중...'):
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.images(query, max_results=3))
                    if results:
                        res = requests.get(results[0]['image'], timeout=5)
                        img = Image.open(BytesIO(res.content))
                        nobg = remove(img)
                        st.session_state.collage_items.append({
                            "img": nobg, "name": query, "x": 100, "y": 200, "size": 300
                        })
                        st.toast("추가되었습니다!")
            except:
                st.error("검색이 어렵습니다. 직접 업로드를 이용해주세요!")
        st.rerun()

with tab3:
    stickers = ["❤️", "⭐", "🍀", "🎀", "🔥", "✨", "👑"]
    chosen = st.selectbox("스티커 선택", stickers)
    if st.button("스티커 추가", use_container_width=True):
        s_img = Image.new("RGBA", (200, 200), (0,0,0,0))
        draw = ImageDraw.Draw(s_img)
        draw.text((50, 50), chosen, fill="red", font_size=100)
        st.session_state.collage_items.append({
            "img": s_img, "name": f"스티커 {chosen}", "x": 100, "y": 200, "size": 200
        })
        st.rerun()

# --- 4. 위치 및 레이어 관리 (모바일 핵심 조작부) ---
if st.session_state.collage_items:
    st.divider()
    st.subheader("📍 위치 및 순서 조정")
    
    # 조작할 대상 선택
    idx = st.selectbox("조정할 사진 선택", range(len(st.session_state.collage_items)), 
                       format_func=lambda x: f"{x+1}번: {st.session_state.collage_items[x]['name']}")
    st.session_state.target_idx = idx
    
    # 레이어 및 크기 조절 버튼
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🔼 위로"):
        if idx < len(st.session_state.collage_items) - 1:
            st.session_state.collage_items[idx], st.session_state.collage_items[idx+1] = st.session_state.collage_items[idx+1], st.session_state.collage_items[idx]
            st.rerun()
    if c2.button("🔽 아래로"):
        if idx > 0:
            st.session_state.collage_items[idx], st.session_state.collage_items[idx-1] = st.session_state.collage_items[idx-1], st.session_state.collage_items[idx]
            st.rerun()
    if c3.button("➕ 크게"):
        st.session_state.collage_items[idx]['size'] += 20
        st.rerun()
    if c4.button("➖ 작게"):
        st.session_state.collage_items[idx]['size'] -= 20
        st.rerun()

    # 상세 좌표 입력 (터치 대신 슬라이더가 모바일 정확도는 더 높음)
    st.session_state.collage_items[idx]['x'] = st.slider("가로 위치", 0, 700, st.session_state.collage_items[idx]['x'])
    st.session_state.collage_items[idx]['y'] = st.slider("세로 위치", 0, 900, st.session_state.collage_items[idx]['y'])

    if st.button("🗑️ 선택 항목 삭제", use_container_width=True):
        st.session_state.collage_items.pop(idx)
        st.rerun()

# --- 5. 최종 콜라주 캔버스 ---
st.divider()
# 캔버스 생성 (구겨진 크림색 종이 느낌)
canvas = Image.new("RGBA", (800, 1100), (245, 242, 230, 255))
draw = ImageDraw.Draw(canvas)

# 제목 (종이 질감에 어울리는 색상)
title_text = f"{st.session_state.user_name}의 최애"
draw.text((400, 100), title_text, fill=(70, 60, 50, 200), anchor="mm", font_size=60)

# 모든 아이템 그리기
for item in st.session_state.collage_items:
    img = item['img']
    # 사이즈 조정
    w = item['size']
    h = int(img.height * (w / img.width))
    resized = img.resize((w, h), Image.Resampling.LANCZOS)
    canvas.paste(resized, (item['x'], item['y']), resized)

st.image(canvas, use_container_width=True)

# 다운로드
out = BytesIO()
canvas.save(out, format="PNG")
st.download_button("💾 콜라주 저장하기 (꾹 눌러서 저장)", out.getvalue(), "collage.png", use_container_width=True)
