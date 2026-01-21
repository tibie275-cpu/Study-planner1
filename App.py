import streamlit as st
import pandas as pd
import time
from datetime import date, datetime
from zoneinfo import ZoneInfo
import plotly.express as px

# ---------- 1. 설정 및 깔끔한 테마 (Sky Blue) ----------
st.set_page_config(page_title="STUDY DASHBOARD", page_icon="📝", layout="centered")

if "page" not in st.session_state: st.session_state.page = "home"
if "planner" not in st.session_state: st.session_state.planner = []
if "routines" not in st.session_state: st.session_state.routines = []

# 깔끔한 블루 & 화이트 스타일
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .card {
        background: #F8FAFC;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
    }
    .main-title {
        font-family: 'Inter', sans-serif;
        color: #1E293B;
        text-align: center;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    div.stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 500;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background-color: #2980b9;
        border: none;
    }
    .timer-display {
        font-size: 3rem;
        font-weight: 700;
        color: #3498db;
        text-align: center;
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 2px solid #3498db;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 2. 상단 네비게이션 ----------
st.markdown("<h1 class='main-title'>STUDY DASHBOARD</h1>", unsafe_allow_html=True)
n1, n2, n3 = st.columns(3)
if n1.button("🏠 Home", use_container_width=True): st.session_state.page = "home"; st.rerun()
if n2.button("✍️ Planner", use_container_width=True): st.session_state.page = "planner"; st.rerun()
if n3.button("📊 Stats", use_container_width=True): st.session_state.page = "stats"; st.rerun()
st.divider()

# ---------- 3. 각 페이지 기능 ----------

def home():
    # [1] 연속 뽀모도로 타이머
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("⏱️ Focus & Break Timer")
        col_t1, col_t2 = st.columns(2)
        f_min = col_t1.number_input("집중 시간(분)", 1, 120, 25)
        b_min = col_t2.number_input("휴식 시간(분)", 1, 60, 5)
        
        if st.button("Start Continuous Timer", use_container_width=True):
            ph = st.empty()
            # 집중 모드
            total_f = f_min * 60
            for t in range(total_f, -1, -1):
                m, s = divmod(t, 60)
                ph.markdown(f"<div class='timer-display'>Focus Mode<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
                time.sleep(1)
            
            st.toast("Focus session ended. Starting break.")
            
            # 휴식 모드 자동 시작
            total_b = b_min * 60
            for t in range(total_b, -1, -1):
                m, s = divmod(t, 60)
                ph.markdown(f"<div class='timer-display' style='color:#2ecc71; border-color:#2ecc71;'>Break Mode<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
                time.sleep(1)
            st.success("One cycle completed!")
        st.markdown("</div>", unsafe_allow_html=True)

    # [2] 루틴 관리
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("✨ Daily Routine")
    new_rt = st.text_input("Add a new routine", key="rt_input")
    if st.button("Add Task"):
        if new_rt:
            st.session_state.routines.append({"task": new_rt, "done": False})
            st.rerun()
    
    for idx, rt in enumerate(st.session_state.routines):
        col_rt1, col_rt2 = st.columns([5, 1])
        rt['done'] = col_rt1.checkbox(rt['task'], value=rt['done'], key=f"rt_{idx}")
        if col_rt2.button("Delete", key=f"del_{idx}"):
            st.session_state.routines.pop(idx)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def planner():
    st.subheader("✍️ Daily Study Log")
    
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        with st.form("plan_form"):
            sub = st.text_input("과목명")
            # 성취도를 OX△로 간결하게 표기
            res = st.select_slider("성취도 정도", options=["X", "△", "O"])
            submitted = st.form_submit_button("Save Record")
            if submitted:
                st.session_state.planner.append({
                    "date": date.today(),
                    "subject": sub,
                    "status": res
                })
                st.rerun()

    if st.session_state.planner:
        df = pd.DataFrame(st.session_state.planner)
        st.write("### History")
        st.dataframe(df, use_container_width=True, hide_index=True)

def stats_view():
    st.subheader("📊 Statistics")
    
    if not st.session_state.planner:
        st.info("기록이 없습니다.")
        return

    df = pd.DataFrame(st.session_state.planner)
    
    # 성취도 점수화 달력 차트
    score_map = {"O": 3, "△": 2, "X": 1}
    df['score'] = df['status'].map(score_map)
    daily_score = df.groupby('date')['score'].sum().reset_index()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    fig = px.scatter(daily_score, x='date', y=[1]*len(daily_score), size='score', 
                     color='score', color_continuous_scale='Blues',
                     title="Daily Achievement")
    fig.update_layout(yaxis_visible=False, height=250)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 4. 페이지 실행 ----------
if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats_view()
