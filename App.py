import streamlit as st
import pandas as pd
import random
import time
from datetime import date, datetime
from zoneinfo import ZoneInfo
import plotly.express as px

# ---------- 1. 기본 설정 및 테마 ----------
st.set_page_config(
    page_title="AI 스마트 스터디 플래너",
    page_icon="📚",
    layout="centered",
)

# 상태 관리 초기화
if "page" not in st.session_state:
    st.session_state.page = "home"
if "planner" not in st.session_state:
    st.session_state.planner = []
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

# ---------- 2. 커스텀 스타일 (고급화) ----------
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp { background-color: #f8f9fa; }
    
    /* 카드 스타일 */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    
    /* 타이틀 디자인 */
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1E293B;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* 타이머 박스 */
    .timer-display {
        font-size: 4rem;
        font-weight: 800;
        color: #4A90E2;
        text-align: center;
        background: #F1F5F9;
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* 하단 고정 네비게이션 느낌의 버튼 스타일 */
    div.stButton > button {
        border-radius: 12px;
        transition: all 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 3. 유틸리티 함수 ----------
def now_kst():
    return datetime.now(ZoneInfo("Asia/Seoul"))

quotes = [
    "오늘의 노력이 내일의 나를 만든다.",
    "지금 포기하면 평생 여기다.",
    "공부하는 고통은 잠깐이지만 못 배운 고통은 평생이다.",
    "느려도 괜찮다. 멈추지만 마라."
]

# ---------- 4. 페이지 구성 함수 ----------

# [홈 페이지]
def home():
    st.markdown("<h1 class='main-title'>🏠 STUDY DASHBOARD</h1>", unsafe_allow_html=True)
    
    # 랜덤 명언 카드
    st.markdown(f"""
    <div class='card'>
        <div style='color:#64748B; font-size:0.9rem; margin-bottom:5px;'>오늘의 한 문장</div>
        <div style='font-size:1.1rem; font-weight:600;'>"{random.choice(quotes)}"</div>
    </div>
    """, unsafe_allow_html=True)

    # 기상/취침 버튼 (상단 요약 기능 추가)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🌅 기상 인증", use_container_width=True):
            st.toast(f"기상 완료! ({now_kst().strftime('%H:%M')})")
    with c2:
        if st.button("🌙 취침 인증", use_container_width=True):
            st.toast(f"오늘 하루 고생했어요! ({now_kst().strftime('%H:%M')})")

    st.divider()

    # [신규 추가] ⏱️ 뽀모도로 타이머 카드
    st.markdown("<div class='card'><div style='font-weight:700; font-size:1.1rem;'>⏱️ 집중 타이머</div>", unsafe_allow_html=True)
    t_col1, t_col2 = st.columns([1, 1])
    
    with t_col1:
        mode = st.radio("모드", ["Focus(25m)", "Break(5m)"], label_visibility="collapsed")
        target_mins = 25 if "Focus" in mode else 5
        
    with t_col2:
        if st.button("🚀 시작", use_container_width=True):
            placeholder = st.empty()
            for i in range(target_mins * 60, -1, -1):
                mins, secs = divmod(i, 60)
                placeholder.markdown(f"<div class='timer-display'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
                time.sleep(1)
            st.balloons()
            st.success("시간 종료! 고생하셨습니다.")
    st.markdown("</div>", unsafe_allow_html=True)

# [플래너 페이지]
def planner():
    st.markdown("<h1 class='main-title'>✍️ DAILY PLANNER</h1>", unsafe_allow_html=True)
    
    with st.expander("➕ 새 학습 계획 추가", expanded=True):
        with st.form("planner_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            sub = col1.text_input("과목명", placeholder="예: 수학")
            con = col2.text_input("공부 내용", placeholder="예: 미분법 문제풀이")
            
            goal = st.slider("목표 시간 (시간)", 0.5, 12.0, 1.0, step=0.5)
            actual = st.slider("실제 공부 시간 (시간)", 0.0, 12.0, 0.0, step=0.5)
            
            if st.form_submit_button("기록하기"):
                st.session_state.planner.append({
                    "날짜": date.today().strftime("%m-%d"),
                    "과목": sub,
                    "내용": con,
                    "목표": goal,
                    "실제": actual,
                    "완료": actual >= goal
                })
                st.rerun()

    if st.session_state.planner:
        st.markdown("### 📋 기록 리스트")
        df = pd.DataFrame(st.session_state.planner)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ 전체 삭제"):
            st.session_state.planner = []
            st.rerun()

# [통계 페이지]
def stats():
    st.markdown("<h1 class='main-title'>📊 STATISTICS</h1>", unsafe_allow_html=True)
    
    if not st.session_state.planner:
        st.info("아직 기록된 공부 데이터가 없어요. 플래너에서 첫 기록을 남겨보세요!")
        return

    df = pd.DataFrame(st.session_state.planner)
    
    # 상단 요약 지표
    c1, c2, c3 = st.columns(3)
    c1.metric("총 공부 시간", f"{df['실제'].sum()}h")
    c2.metric("목표 달성률", f"{(df['완료'].mean()*100):.1f}%")
    c3.metric("최다 과목", df['과목'].mode()[0] if not df.empty else "-")

    # 차트 섹션
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("과목별 시간 비중")
    fig = px.pie(df, values='실제', names='과목', hole=0.4, 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 5. 메인 네비게이션 로직 ----------
if st.session_state.page == "home":
    home()
elif st.session_state.page == "planner":
    planner()
elif st.session_state.page == "stats":
    stats()

# ---------- 6. 하단 고정형 네비게이션 ----------
st.markdown("<br><br>", unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    if st.button("🏠 홈", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
with nav_col2:
    if st.button("✍️ 플래너", use_container_width=True):
        st.session_state.page = "planner"
        st.rerun()
with nav_col3:
    if st.button("📊 통계", use_container_width=True):
        st.session_state.page = "stats"
        st.rerun()
