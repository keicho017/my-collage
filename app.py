import streamlit as st
from rembg import remove
from PIL import Image
import requests
from io import BytesIO
from duckduckgo_search import DDGS
import random

# --- 페이지 설정 ---
st.set_page_config(page_title="Favorite Collage Maker", layout="wide")

# 세션 상태 초기화 (이미지 데이터 유지용)
if 'collage_items' not in st.session_state:
    st.session_state.collage_items = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 1. 이름 입력 화면 (Welcome) ---
if not st.session_state.user_name:
    st.markdown("<h1 style='text-align: center;'>🎨 My Favorite Collage Maker</h1>", unsafe_allow_html=True)
    with st.container():
        name = st.text_input("당신의 이름을 입력해주세요:", placeholder="예: 제미니")
        if st.button("시작하기", use_container_width=True):
            if name:
                st.session_state.user_name = name
                st.rerun()
            else:
                st.warning("이름을 입력해야 시작할 수 있어요!")
    st.stop()

# --- 제목 표시 ---
st.markdown(f"<h1 style='text-align: center; color: #FF69B4;'>💖 {st.session_state.user_name}'s Favorite Things 💖</h1>", unsafe_allow_html=True)

# --- 2. 이미지 수집 섹션 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 사진 업로드")
    files = st.file_uploader("사진을 선택하세요", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    if st.button("업로드 완료"):
        for f in files:
            img = Image.open(f)
            # 누끼 따기 적용
            with st.spinner(f'{f.name} 배경 제거 중...'):
                nobg = remove(img)
                st.session_state.collage_items.append({"img": nobg, "name": f.name, "type": "photo"})
        st.rerun()

with col2:
    st.subheader("🔍 이름으로 찾기")
    keywords = st.text_input("연예인, 캐릭터 이름을 ,로 구분 입력", placeholder="예: 아이유, 하니, 짱구")
    if st.button("자동 검색 및 추가"):
        with st.spinner('이미지를 검색하고 누끼를 따는 중...'):
            with DDGS() as ddgs:
                names = [n.strip() for n in keywords.split(",") if n.strip()]
                for name in names:
                    results = list(ddgs.images(name, max_results=1))
                    if results:
                        try:
                            res = requests.get(results[0]['image'], timeout=10)
                            img = Image.open(BytesIO(res.content))
                            nobg = remove(img)
                            st.session_state.collage_items.append({"img": nobg, "name": name, "type": "search"})
                        except:
                            st.error(f"{name} 이미지를 가져오지 못했습니다.")
        st.rerun()

# --- 3. 스티커 라이브러리 (버튼 클릭 시 추가) ---
st.divider()
st.subheader("✨ 스티커 추가")
sticker_col = st.columns(5)
stickers = ["❤️", "⭐", "🎀", "🍀", "🔥"]
for i, s in enumerate(stickers):
    if sticker_col[i].button(f"{s} 스티커 추가"):
        # 텍스트를 이미지로 변환하거나 준비된 이미지가 없으므로 간단한 텍스트 라벨로 대체 (실제로는 이미지 파일 경로 연결 가능)
        st.info(f"{s} 스티커 기능은 이미지 파일이 준비되면 즉시 연결 가능합니다!")

# --- 4. 레이어 관리 (순서 조정 기능) ---
st.divider()
st.subheader("층층이 쌓기 (레이어 관리)")
if not st.session_state.collage_items:
    st.info("아직 추가된 이미지가 없습니다.")
else:
    for i, item in enumerate(st.session_state.collage_items):
        l_col1, l_col2, l_col3, l_col4 = st.columns([4, 1, 1, 1])
        l_col1.write(f"**[{i+1}층]** {item['name']}")
        
        # 위로 이동
        if l_col2.button("🔼", key=f"up_{i}") and i > 0:
            st.session_state.collage_items[i], st.session_state.collage_items[i-1] = st.session_state.collage_items[i-1], st.session_state.collage_items[i]
            st.rerun()
        
        # 아래로 이동
        if l_col3.button("🔽", key=f"down_{i}") and i < len(st.session_state.collage_items) - 1:
            st.session_state.collage_items[i], st.session_state.collage_items[i+1] = st.session_state.collage_items[i+1], st.session_state.collage_items[i]
            st.rerun()

        # 삭제
        if l_col4.button("🗑️", key=f"del_{i}"):
            st.session_state.collage_items.pop(i)
            st.rerun()

# --- 5. 최종 콜라주 생성 및 저장 ---
st.divider()
if st.button("🖼️ 최종 콜라주 생성!", use_container_width=True, type="primary"):
    if not st.session_state.collage_items:
        st.error("이미지를 먼저 추가해주세요!")
    else:
        # 배경 캔버스 생성
        canvas = Image.new("RGBA", (1200, 800), (255, 255, 255, 255))
        
        # 레이어 순서대로 그리기 (리스트의 뒷부분이 가장 위로 올라옴)
        for item in st.session_state.collage_items:
            img = item['img']
            # 랜덤 크기 (조화롭게 조절)
            w = random.randint(350, 550)
            h = int(img.height * (w / img.width))
            resized = img.resize((w, h), Image.Resampling.LANCZOS)
            
            # 랜덤 위치
            x = random.randint(0, 1200 - w)
            y = random.randint(0, 800 - h)
            
            # 합성
            canvas.paste(resized, (x, y), resized)
            
        st.image(canvas, caption="완성된 콜라주! 마음에 드시나요?")
        
        # 다운로드 기능
        buf = BytesIO()
        canvas.save(buf, format="PNG")
        st.download_button(
            label="💾 완성 사진 저장하기",
            data=buf.getvalue(),
            file_name=f"{st.session_state.user_name}_favorite.png",
            mime="image/png",
            use_container_width=True
        )