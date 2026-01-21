import streamlit as st
import pandas as pd
import random
import time
from datetime import date, datetime
from zoneinfo import ZoneInfo
import plotly.express as px

# ---------- 1. 설정 및 핑크 테마 ----------
st.set_page_config(page_title="모찌의 핑크 스터디", page_icon="🌸", layout="centered")

if "page" not in st.session_state: st.session_state.page = "home"
if "planner" not in st.session_state: st.session_state.planner = []
if "routines" not in st.session_state: st.session_state.routines = []

# 핑크빛 커스텀 스타일
st.markdown("""
<style>
    .stApp { background-color: #FFF5F7; }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 25px;
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px rgba(255, 182, 193, 0.2);
        border: 2px solid #FFD1DC;
    }
    .main-title {
        font-family: 'Nanum Gothic', sans-serif;
        color: #FF85A2;
        text-align: center;
        font-weight: 900;
    }
    div.stButton > button {
        background-color: #FFB6C1;
        color: white;
        border-radius: 20px;
        border: none;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #FF85A2;
        color: white;
    }
    .timer-display {
        font-size: 3.5rem;
        font-weight: 900;
        color: #FF4D6D;
        text-align: center;
        background: #FFF0F3;
        border-radius: 30px;
        padding: 15px;
        border: 3px dashed #FFB6C1;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 2. 기능 구현 ----------

def home():
    st.markdown("<h1 class='main-title'>🌸 MOZZI STUDY 🌸</h1>", unsafe_allow_html=True)
    
    # [1] 연속 뽀모도로 타이머
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#FF85A2;'>⏱️ 쉬지않고 달리기!</h3>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2)
    f_min = col_t1.number_input("집중(분)", 1, 120, 25)
    b_min = col_t2.number_input("휴식(분)", 1, 60, 5)
    
    if st.button("💗 연속 타이머 시작!", use_container_width=True):
        ph = st.empty()
        # 집중 시간
        for t in range(f_min * 60, -1, -1):
            m, s = divmod(t, 60)
            ph.markdown(f"<div class='timer-display'>🔥 집중!<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
        st.toast("집중 끝! 바로 휴식 시작할게요 🍬")
        
        # 휴식 시간 바로 시작
        for t in range(b_min * 60, -1, -1):
            m, s = divmod(t, 60)
            ph.markdown(f"<div class='timer-display'>🍬 휴식~<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
        st.balloons()
        st.success("한 세트 완료! 정말 대단해요 🧸")
    st.markdown("</div>", unsafe_allow_html=True)

    # [2] 나만의 루틴 작성
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#FF85A2;'>✨ 데일리 루틴</h3>", unsafe_allow_html=True)
    new_rt = st.text_input("새 루틴 추가 (예: 물 1L 마시기)", key="rt_input")
    if st.button("➕ 추가"):
        if new_rt:
            st.session_state.routines.append({"task": new_rt, "done": False})
            st.rerun()
    
    for idx, rt in enumerate(st.session_state.routines):
        col_rt1, col_rt2 = st.columns([4, 1])
        rt['done'] = col_rt1.checkbox(rt['task'], value=rt['done'], key=f"rt_{idx}")
        if col_rt2.button("🗑️", key=f"del_{idx}"):
            st.session_state.routines.pop(idx)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def planner():
    st.markdown("<h1 class='main-title'>✍️ 플래너 기록</h1>", unsafe_allow_html=True)
    
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        with st.form("plan_form"):
            sub = st.text_input("과목명")
            res = st.radio("성취도 선택", ["🤩 완벽(O)", "🤨 보통(△)", "😭 미흡(X)"], horizontal=True)
            submitted = st.form_submit_button("기록하기 🎀")
            if submitted:
                st.session_state.planner.append({
                    "date": date.today(),
                    "subject": sub,
                    "status": res[0] # 첫 글자 아이콘만 저장
                })
                st.rerun()

    if st.session_state.planner:
        df = pd.DataFrame(st.session_state.planner)
        st.write("### 💖 나의 기록")
        st.table(df)

def calendar_view():
    st.markdown("<h1 class='main-title'>📅 성취도 달력</h1>", unsafe_allow_html=True)
    
    if not st.session_state.planner:
        st.info("기록이 있어야 달력을 꾸밀 수 있어요! 🌸")
        return

    df = pd.DataFrame(st.session_state.planner)
    df['date'] = pd.to_datetime(df['date'])
    
    # 귀여운 도트형 달력 시각화 (성취도를 점수로 환산)
    score_map = {"🤩": 3, "🤨": 2, "😭": 1}
    df['score'] = df['status'].map(score_map)
    daily_score = df.groupby('date')['score'].sum().reset_index()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    fig = px.scatter(daily_score, x='date', y=[1]*len(daily_score), size='score', 
                     color='score', color_continuous_scale='PuRd',
                     title="나의 핑크빛 공부 기록 🐾")
    fig.update_layout(yaxis_visible=False, height=200, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<p style='text-align:center;'>큰 방울일수록 열공했다는 뜻이에요! 🎀</p></div>", unsafe_allow_html=True)

# ---------- 3. 네비게이션 ----------
st.markdown("<br><br>", unsafe_allow_html=True)
n1, n2, n3 = st.columns(3)
if n1.button("🏠 홈"): st.session_state.page = "home"; st.rerun()
if n2.button("✍️ 기록"): st.session_state.page = "planner"; st.rerun()
if n3.button("📅 달력"): st.session_state.page = "calendar"; st.rerun()

if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "calendar": calendar_view()
