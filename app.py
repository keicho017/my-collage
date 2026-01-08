import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from duckduckgo_search import DDGS
import random
import time

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="My Favorite Collage", layout="wide")

if 'collage_items' not in st.session_state:
    st.session_state.collage_items = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 2. 입장 화면 ---
if not st.session_state.user_name:
    st.markdown("<h1 style='text-align: center;'>🎨 나만의 취향 콜라주 메이커</h1>", unsafe_allow_html=True)
    user_input = st.text_input("당신의 이름을 입력하고 시작하세요!", placeholder="예: 제미니")
    if st.button("콜라주 만들기 시작", use_container_width=True):
        if user_input:
            st.session_state.user_name = user_input
            st.rerun()
    st.stop()

# --- 3. 메인 화면 ---
st.markdown(f"<h1 style='text-align: center; color: #FF69B4;'>💖 {st.session_state.user_name}님의 최애 콜라주 💖</h1>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("🛠️ 아이템 추가")
    tab1, tab2, tab3 = st.tabs(["📁 직접 업로드", "🔍 이미지 검색", "✨ 스티커"])
    
    with tab1:
        uploaded_files = st.file_uploader("사진을 선택하세요", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
        if st.button("업로드 및 배경 제거"):
            if uploaded_files:
                for f in uploaded_files:
                    with st.spinner(f'{f.name} 처리 중...'):
                        img = Image.open(f)
                        nobg = remove(img)
                        st.session_state.collage_items.append({"img": nobg, "name": f.name})
                st.toast(f"{len(uploaded_files)}개의 이미지를 추가했습니다! ✨")
                st.rerun()

    with tab2:
        search_query = st.text_input("검색어 입력", placeholder="예: 짱구, 아이유")
        if st.button("검색어로 추가"):
            if search_query:
                with st.spinner('이미지를 찾는 중...'):
                    try:
                        with DDGS() as ddgs:
                            time.sleep(1.5) # 차단 방지 대기
                            search_results = list(ddgs.images(search_query, max_results=5))
                            
                            if not search_results:
                                st.toast("🔍 검색 결과가 없습니다. 다른 단어로 검색해보세요.", icon="⚠️")
                            else:
                                success = False
                                for result in search_results:
                                    try:
                                        res = requests.get(result['image'], timeout=5)
                                        if res.status_code == 200:
                                            img = Image.open(BytesIO(res.content))
                                            nobg = remove(img)
                                            st.session_state.collage_items.append({"img": nobg, "name": search_query})
                                            success = True
                                            st.toast(f"'{search_query}' 이미지를 찾아서 추가했습니다! 🎉")
                                            break
                                    except:
                                        continue
                                
                                if not success:
                                    st.toast("🚫 이미지 사이트에서 접근을 거부했습니다. 다른 검색어로 시도해보세요.", icon="❌")
                    except Exception as e:
                        st.toast("⏳ 검색 서버가 바쁩니다. 잠시 후 다시 시도하거나 사진을 직접 업로드해주세요.", icon="⚠️")
                st.rerun()

    with tab3:
        stickers = ["❤️", "⭐", "🍀", "🎀", "🔥", "✨", "👑", "🍭"]
        chosen = st.selectbox("스티커 선택", stickers)
        if st.button("스티커 추가"):
            s_img = Image.new("RGBA", (200, 200), (0,0,0,0))
            draw = ImageDraw.Draw(s_img)
            draw.text((50, 50), chosen, fill="red", font_size=100)
            st.session_state.collage_items.append({"img": s_img, "name": f"스티커 {chosen}"})
            st.toast(f"스티커 {chosen} 추가 완료! 💖")
            st.rerun()

    # 레이어 관리
    if st.session_state.collage_items:
        st.divider()
        st.subheader("층층이 관리 (레이어)")
        for i, item in enumerate(st.session_state.collage_items):
            m_c1, m_c2, m_c3, m_c4 = st.columns([1, 4, 1, 1])
            m_c1.image(item['img'], width=40)
            m_c2.write(f"{i+1}층: {item['name']}")
            if m_c3.button("🔼", key=f"up{i}") and i > 0:
                st.session_state.collage_items[i], st.session_state.collage_items[i-1] = st.session_state.collage_items[i-1], st.session_state.collage_items[i]
                st.rerun()
            if m_c4.button("🗑️", key=f"del{i}"):
                st.session_state.collage_items.pop(i)
                st.rerun()

with col_right:
    st.subheader("🖼️ 콜라주 결과물")
    if st.session_state.collage_items:
        canvas = Image.new("RGBA", (1000, 700), (255, 255, 255, 255))
        for item in st.session_state.collage_items:
            img = item['img']
            base_width = 350
            w_percent = (base_width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            resized_img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
            x, y = random.randint(0, 1000 - base_width), random.randint(0, max(0, 700 - h_size))
            canvas.paste(resized_img, (x, y), resized_img)
        st.image(canvas, use_container_width=True)
        
        output = BytesIO()
        canvas.save(output, format="PNG")
        st.download_button("💾 사진 저장", output.getvalue(), "collage.png", "image/png", use_container_width=True)
    else:
        st.info("왼쪽에서 사진을 추가해보세요!")
