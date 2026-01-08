import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from duckduckgo_search import DDGS
import random
import time

# --- 1. 페이지 설정 (모바일 최적화) ---
st.set_page_config(page_title="최애 콜라주", layout="centered") # 모바일은 centered가 보기 편합니다.

# 세션 상태 초기화
if 'collage_items' not in st.session_state:
    st.session_state.collage_items = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 2. 입장 화면 ---
if not st.session_state.user_name:
    st.markdown("<h2 style='text-align: center;'>✨ 나만의 최애 콜라주 ✨</h2>", unsafe_allow_html=True)
    user_input = st.text_input("이름을 입력해주세요", placeholder="예: 제미니")
    if st.button("시작하기", use_container_width=True):
        if user_input:
            st.session_state.user_name = user_input
            st.rerun()
    st.stop()

# --- 3. 조작부 (상단 배치) ---
st.subheader("🛠️ 아이템 추가")
tab1, tab2, tab3 = st.tabs(["📁 업로드", "🔍 검색", "✨ 스티커"])

with tab1:
    files = st.file_uploader("사진 선택", accept_multiple_files=True, type=['jpg', 'png'])
    if st.button("사진 추가", use_container_width=True):
        if files:
            for f in files:
                with st.spinner('누끼 따는 중...'):
                    img = Image.open(f)
                    nobg = remove(img)
                    # 위치 조정을 위해 x, y 좌표 추가 (중앙 근처 랜덤)
                    st.session_state.collage_items.append({
                        "img": nobg, "name": f.name, 
                        "x": random.randint(100, 500), "y": random.randint(200, 600)
                    })
            st.rerun()

with tab2:
    query = st.text_input("검색어 (예: 짱구)", key="search_input")
    if st.button("이미지 검색", use_container_width=True):
        with st.spinner('이미지 찾는 중...'):
            try:
                # 최신 duckduckgo_search 문법 적용
                with DDGS() as ddgs:
                    results = [r for r in ddgs.images(query, max_results=5)]
                    if results:
                        success = False
                        for r in results:
                            try:
                                res = requests.get(r['image'], timeout=5)
                                img = Image.open(BytesIO(res.content))
                                nobg = remove(img)
                                st.session_state.collage_items.append({
                                    "img": nobg, "name": query,
                                    "x": random.randint(100, 500), "y": random.randint(200, 600)
                                })
                                success = True
                                break
                            except: continue
                        if success: st.toast("추가 완료!")
                        else: st.error("이미지를 가져오지 못했어요.")
                    else: st.warning("결과가 없어요.")
            except:
                st.error("검색 기능이 일시적으로 제한되었습니다. 직접 업로드 기능을 권장합니다!")

with tab3:
    stickers = ["❤️", "⭐", "🍀", "🎀", "🔥", "✨", "👑"]
    chosen = st.selectbox("스티커", stickers)
    if st.button("스티커 추가", use_container_width=True):
        s_img = Image.new("RGBA", (200, 200), (0,0,0,0))
        draw = ImageDraw.Draw(s_img)
        draw.text((50, 50), chosen, fill="red", font_size=100)
        st.session_state.collage_items.append({
            "img": s_img, "name": f"스티커 {chosen}",
            "x": random.randint(100, 500), "y": random.randint(200, 600)
        })
        st.rerun()

# --- 4. 위치 조정 슬라이더 (개별 조정 가능) ---
if st.session_state.collage_items:
    st.divider()
    st.subheader("📍 위치 조정")
    idx = st.selectbox("조정할 아이템 선택", range(len(st.session_state.collage_items)), 
                       format_func=lambda x: f"{x+1}번: {st.session_state.collage_items[x]['name']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.collage_items[idx]['x'] = st.slider("가로 위치", 0, 800, st.session_state.collage_items[idx]['x'])
    with col2:
        st.session_state.collage_items[idx]['y'] = st.slider("세로 위치", 0, 1000, st.session_state.collage_items[idx]['y'])
    
    if st.button("🗑️ 선택 삭제", use_container_width=True):
        st.session_state.collage_items.pop(idx)
        st.rerun()

# --- 5. 콜라주 생성 (종이 질감 배경) ---
st.divider()
st.subheader("🖼️ 결과물")

# 캔버스 생성 (크림색 종이 질감 색상)
canvas = Image.new("RGBA", (800, 1100), (245, 242, 230, 255)) # 크림색
draw = ImageDraw.Draw(canvas)

# 제목 추가 (종이 위에 쓴 느낌)
title_text = f"{st.session_state.user_name}의 최애"
draw.text((400, 80), title_text, fill=(80, 70, 60, 200), anchor="mm", font_size=60)

# 아이템 배치
for item in st.session_state.collage_items:
    img = item['img']
    # 크기 최적화
    base_w = 300
    w_percent = (base_w / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    resized = img.resize((base_w, h_size), Image.Resampling.LANCZOS)
    canvas.paste(resized, (item['x'], item['y']), resized)

st.image(canvas, use_container_width=True)

# 저장
out = BytesIO()
canvas.save(out, format="PNG")
st.download_button("💾 콜라주 저장하기", out.getvalue(), "my_collage.png", use_container_width=True)
