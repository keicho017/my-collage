import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from duckduckgo_search import DDGS
import random
import time

# --- 페이지 설정 ---
st.set_page_config(page_title="Favorite Collage Maker", layout="wide")

# 세션 상태 초기화
if 'collage_items' not in st.session_state:
    st.session_state.collage_items = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 1. 이름 입력 화면 ---
if not st.session_state.user_name:
    st.markdown("<h1 style='text-align: center;'>🎨 My Favorite Collage Maker</h1>", unsafe_allow_html=True)
    name = st.text_input("당신의 이름을 입력해주세요:", placeholder="예: 제미니")
    if st.button("시작하기", use_container_width=True):
        if name:
            st.session_state.user_name = name
            st.rerun()
    st.stop()

# 헤더
st.markdown(f"<h1 style='text-align: center; color: #FF69B4;'>💖 {st.session_state.user_name}'s Favorite Things 💖</h1>", unsafe_allow_html=True)

# --- 2. 입력 및 관리 섹션 ---
col_input, col_preview = st.columns([1, 1.5])

with col_input:
    st.subheader("🛠️ 아이템 추가하기")
    
    # 탭으로 구성 (업로드 / 검색 / 스티커)
    tab1, tab2, tab3 = st.tabs(["📁 업로드", "🔍 검색", "✨ 스티커"])
    
    with tab1:
        files = st.file_uploader("사진 선택", accept_multiple_files=True, type=['jpg', 'png'])
        if st.button("사진 추가하기"):
            for f in files:
                with st.spinner(f'{f.name} 누끼 따는 중...'):
                    img = Image.open(f)
                    nobg = remove(img)
                    st.session_state.collage_items.append({"img": nobg, "name": f.name, "show": True})
            st.rerun()

    with tab2:
        keywords = st.text_input("검색어 (쉼표 구분)", placeholder="아이유, 짱구")
        if st.button("이미지 검색 추가"):
            with DDGS() as ddgs:
                names = [n.strip() for n in keywords.split(",") if n.strip()]
                for name in names:
                    try:
                        time.sleep(1.0) # 차단 방지
                        results = list(ddgs.images(name, max_results=1))
                        if results:
                            res = requests.get(results[0]['image'], timeout=10)
                            img = Image.open(BytesIO(res.content))
                            nobg = remove(img)
                            st.session_state.collage_items.append({"img": nobg, "name": name, "show": True})
                    except:
                        st.error(f"'{name}' 검색 실패 (서버 제한)")
            st.rerun()

    with tab3:
        sticker_list = ["❤️", "⭐", "🎀", "🍀", "🔥", "👑", "🍭", "✨"]
        selected_sticker = st.selectbox("스티커 선택", sticker_list)
        if st.button("스티커 추가"):
            # 텍스트를 투명 이미지로 변환
            s_img = Image.new("RGBA", (200, 200), (0,0,0,0))
            draw = ImageDraw.Draw(s_img)
            # 폰트 설정 (기본 폰트 사용)
            draw.text((50, 50), selected_sticker, fill="red", font_size=100)
            st.session_state.collage_items.append({"img": s_img, "name": f"스티커 {selected_sticker}", "show": True})
            st.rerun()

    # --- 레이어 관리 리스트 ---
    st.divider()
    st.subheader("층층이 관리 (레이어)")
    for i, item in enumerate(st.session_state.collage_items):
        l_c1, l_c2, l_c3, l_c4 = st.columns([3, 1, 1, 1])
        l_c1.image(item['img'], width=50) # 작은 미리보기
        if l_c2.button("🔼", key=f"u{i}") and i > 0:
            st.session_state.collage_items[i], st.session_state.collage_items[i-1] = st.session_state.collage_items[i-1], st.session_state.collage_items[i]
            st.rerun()
        if l_c3.button("🔽", key=f"d{i}") and i < len(st.session_state.collage_items)-1:
            st.session_state.collage_items[i], st.session_state.collage_items[i+1] = st.session_state.collage_items[i+1], st.session_state.collage_items[i]
            st.rerun()
        if l_c4.button("🗑️", key=f"r{i}"):
            st.session_state.collage_items.pop(i)
            st.rerun()

# --- 3. 실시간 미리보기 및 결과 ---
with col_preview:
    st.subheader("🖼️ 콜라주 미리보기")
    
    if st.session_state.collage_items:
        # 배경 캔버스
        canvas = Image.new("RGBA", (1200, 800), (255, 255, 255, 255))
        
        # 고정된 랜덤성을 위해 시드 고정 (재실행 시 위치 안 바뀌게 하려면 설정 필요하나 여기선 재미를 위해 랜덤)
        for item in st.session_state.collage_items:
            img = item['img']
            w = random.randint(300, 500)
            h = int(img.height * (w / img.width))
            resized = img.resize((w, h), Image.LANCZOS)
            x, y = random.randint(0, 1200-w), random.randint(0, 800-h)
            canvas.paste(resized, (x, y), resized)
        
        st.image(canvas, use_container_width=True)
        
        # 저장 버튼
        buf = BytesIO()
        canvas.save(buf, format="PNG")
        st.download_button("💾 결과 사진 저장하기", buf.getvalue(), f"{st.session_state.user_name}_collage.png", "image/png", use_container_width=True)
    else:
        st.info("왼쪽에서 사진을 추가하면 여기에 콜라주가 나타납니다!")
