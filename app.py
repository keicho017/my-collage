import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from duckduckgo_search import DDGS
import random
import time
import os

# --- [폰트 해결] 한글 폰트 다운로드 함수 ---
def get_font():
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        # 나눔고딕 폰트 파일이 없으면 인터넷에서 가져옵니다.
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
        res = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(res.content)
    return font_path

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="최애 콜라주", layout="centered")

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

# --- 3. 아이템 추가 ---
st.subheader("🛠️ 아이템 추가")
tab1, tab2, tab3 = st.tabs(["📁 업로드", "🔍 검색", "✨ 스티커"])

with tab1:
    files = st.file_uploader("사진 선택", accept_multiple_files=True, type=['jpg', 'png'])
    if st.button("사진 추가", use_container_width=True):
        for f in files:
            with st.spinner('배경 제거 중...'):
                img = Image.open(f).convert("RGBA")
                nobg = remove(img)
                st.session_state.collage_items.append({
                    "img": nobg, "name": f.name, "x": 100, "y": 200, "size": 300, "rotation": 0
                })
        st.rerun()

# (검색 및 스티커 탭은 이전과 동일하되 "rotation" 값을 초기값 0으로 추가함)
with tab2:
    query = st.text_input("검색어 입력")
    if st.button("이미지 검색 및 추가", use_container_width=True):
        with st.spinner('검색 중...'):
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.images(query, max_results=3))
                    if results:
                        res = requests.get(results[0]['image'], timeout=5)
                        img = Image.open(BytesIO(res.content)).convert("RGBA")
                        nobg = remove(img)
                        st.session_state.collage_items.append({
                            "img": nobg, "name": query, "x": 100, "y": 200, "size": 300, "rotation": 0
                        })
            except: st.error("검색 실패! 직접 업로드해주세요.")
        st.rerun()

with tab3:
    stickers = ["❤️", "⭐", "🍀", "🎀", "🔥", "✨", "👑"]
    chosen = st.selectbox("스티커 선택", stickers)
    if st.button("스티커 추가", use_container_width=True):
        s_img = Image.new("RGBA", (300, 300), (0,0,0,0))
        draw = ImageDraw.Draw(s_img)
        draw.text((150, 150), chosen, fill="red", font_size=150, anchor="mm")
        st.session_state.collage_items.append({
            "img": s_img, "name": f"스티커 {chosen}", "x": 100, "y": 200, "size": 200, "rotation": 0
        })
        st.rerun()

# --- 4. 위치, 크기, 회전 및 레이어 관리 ---
if st.session_state.collage_items:
    st.divider()
    st.subheader("📍 아이템 상세 조정")
    
    idx = st.selectbox("조정할 사진 선택", range(len(st.session_state.collage_items)), 
                       format_func=lambda x: f"{x+1}번: {st.session_state.collage_items[x]['name']}")
    
    item = st.session_state.collage_items[idx]
    
    # 조작 버튼들
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🔼 위로"):
        if idx < len(st.session_state.collage_items) - 1:
            st.session_state.collage_items[idx], st.session_state.collage_items[idx+1] = st.session_state.collage_items[idx+1], st.session_state.collage_items[idx]
            st.rerun()
    if c2.button("🔽 아래로"):
        if idx > 0:
            st.session_state.collage_items[idx], st.session_state.collage_items[idx-1] = st.session_state.collage_items[idx-1], st.session_state.collage_items[idx]
            st.rerun()
    
    # 슬라이더 조절
    item['x'] = st.slider("가로 위치", 0, 800, item['x'])
    item['y'] = st.slider("세로 위치", 0, 1000, item['y'])
    item['size'] = st.slider("크기 조절", 50, 800, item['size'])
    item['rotation'] = st.slider("회전 각도 (도)", -180, 180, item['rotation'])

    if st.button("🗑️ 선택 삭제", use_container_width=True):
        st.session_state.collage_items.pop(idx)
        st.rerun()

# --- 5. 최종 콜라주 그리기 ---
st.divider()
canvas = Image.new("RGBA", (800, 1100), (245, 242, 230, 255))
draw = ImageDraw.Draw(canvas)

# 제목 추가 (폰트 로드 및 한글 적용)
try:
    font_p = get_font()
    font = ImageFont.truetype(font_p, 60)
    title_text = f"{st.session_state.user_name}의 최애"
    draw.text((400, 100), title_text, fill=(70, 60, 50, 220), anchor="mm", font=font)
except:
    draw.text((400, 100), f"{st.session_state.user_name}'s Best", fill=(70, 60, 50, 220), anchor="mm")

# 아이템 배치 로직
for item in st.session_state.collage_items:
    img = item['img']
    # 1. 크기 조절
    w = item['size']
    h = int(img.height * (w / img.width))
    resized = img.resize((w, h), Image.Resampling.LANCZOS)
    
    # 2. 회전 (expand=True로 해야 이미지가 잘리지 않음)
    rotated = resized.rotate(item['rotation'], expand=True, resample=Image.BICUBIC)
    
    # 3. 붙이기
    canvas.paste(rotated, (item['x'], item['y']), rotated)

st.image(canvas, use_container_width=True)

out = BytesIO()
canvas.save(out, format="PNG")
st.download_button("💾 콜라주 저장하기", out.getvalue(), "collage.png", use_container_width=True)
