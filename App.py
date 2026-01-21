import streamlit as st
import pandas as pd
import random
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px

# ---------- 1. 기본 설정 ----------
st.set_page_config(
    page_title="Study Dashboard",
    page_icon="☁️", 
    layout="centered",
)

# 상태 관리 초기화
if "page" not in st.session_state: st.session_state.page = "home"
if "planner" not in st.session_state: st.session_state.planner = []
if "routines" not in st.session_state: st.session_state.routines = []
if "timer_active" not in st.session_state: st.session_state.timer_active = False

# ---------- 2. 커스텀 스타일 (빨간색 제거 & 21일 레이스 그리드) ----------
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    
    /* 카드 디자인 */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(135, 206, 250, 0.1);
        border: 1px solid #E6F3FF;
    }
    
    .main-title {
        font-size: 2.2rem; font-weight: 800; color: #5DADE2;
        text-align: center; margin-bottom: 1rem;
    }
    
    /* 21일 레이스 그리드 스타일 */
    .race-container {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
        margin-top: 10px;
    }
    .race-box {
        aspect-ratio: 1 / 1;
        background-color: #F8F9FA;
        border: 2px solid #E6F3FF;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #BDC3C7;
        font-size: 0.9rem;
    }
    .race-box.completed {
        background-color: #E1F5FE;
        border-color: #81D4FA;
        color: #039BE5;
    }
    .race-box.perfect {
        background-color: #87CEFA;
        border-color: #5DADE2;
        color: white;
    }

    /* 타이머 디스플레이 */
    .timer-display {
        font-size: 4rem; font-weight: 800; color: #5DADE2;
        text-align: center; background: #FFFFFF;
        border-radius: 20px; padding: 30px; margin: 15px 0;
        border: 2px solid #E6F3FF;
    }
    
    /* 슬라이더 빨간색 완전 박멸 */
    div[data-baseweb="slider"] > div > div { background: #E6F3FF !important; }
    div[data-baseweb="slider"] > div > div > div { background: #FFFFFF !important; border: 1px solid #B3E5FC; }
    div[role="slider"] { background-color: #FFFFFF !important; border: 2px solid #87CEFA !important; }
    div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"], span[data-baseweb="typography"] { color: #5DADE2 !important; }
    .stSlider [data-baseweb="slider"] [aria-valuenow] { color: #5DADE2 !important; }

    /* 버튼 스타일 */
    div.stButton > button {
        background-color: #87CEFA; color: white;
        border-radius: 12px; border: none; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #5DADE2; }
</style>
""", unsafe_allow_html=True)

# ---------- 3. 유틸리티 ----------
def now_kst(): return datetime.now(ZoneInfo("Asia/Seoul"))
quotes = ["오늘의 노력이 내일의 나를 만든다.", "공부는 배신하지 않는다.", "느려도 괜찮다. 멈추지만 마라."]

# ---------- 4. 페이지 함수 ----------

# [홈 페이지]
def home():
    st.markdown("<h1 class='main-title'>☁️ STUDY DASHBOARD</h1>", unsafe_allow_html=True)
    
    # 명언
    st.markdown(f"<div class='card'><div style='color:#7FB3D5; font-size:0.9rem;'>Today's Quote</div><div style='font-size:1.1rem; font-weight:600; color:#2E86C1;'>\"{random.choice(quotes)}\"</div></div>", unsafe_allow_html=True)

    # ⏱️ 뽀모도로 타이머
    st.markdown("<div class='card'><div style='font-weight:700; color:#5DADE2;'>⏱️ 집중 & 휴식 타이머</div>", unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    f_time = tc1.number_input("집중(분)", 1, 120, 25)
    b_time = tc2.number_input("휴식(분)", 1, 60, 5)
    
    col_start, col_stop = st.columns(2)
    start_btn = col_start.button("🚀 타이머 시작", use_container_width=True)
    stop_btn = col_stop.button("🛑 중단/종료", use_container_width=True)
    
    if start_btn:
        st.session_state.timer_active = True
        placeholder = st.empty()
        
        # 1. 집중 모드 (NameError 수정됨)
        total_f = f_time * 60
        for i in range(total_f, -1, -1):
            if not st.session_state.timer_active: break
            mins, secs = divmod(i, 60)
            placeholder.markdown(f"<div class='timer-display'><span style='font-size:1.5rem; color:#87CEFA;'>FOCUS</span><br>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            
        if st.session_state.timer_active:
            placeholder.markdown("<div class='timer-display' style='color:#5DADE2;'>TIME UP!<br><span style='font-size:1.5rem;'>휴식 시작</span></div>", unsafe_allow_html=True)
            time.sleep(2)
            # 2. 휴식 모드
            total_b = b_time * 60
            for i in range(total_b, -1, -1):
                if not st.session_state.timer_active: break
                mins, secs = divmod(i, 60)
                placeholder.markdown(f"<div class='timer-display' style='color:#48C9B0; border-color:#48C9B0;'><span style='font-size:1.5rem; color:#48C9B0;'>BREAK</span><br>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
                time.sleep(1)
            if st.session_state.timer_active:
                st.balloons()
                st.session_state.timer_active = False
    
    if stop_btn:
        st.session_state.timer_active = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ✨ 루틴 관리
    st.markdown("<div class='card'><div style='font-weight:700; color:#5DADE2;'>✨ 나의 루틴</div>", unsafe_allow_html=True)
    r_input = st.text_input("루틴 추가", placeholder="할 일을 입력하세요")
    if st.button("추가"):
        if r_input: st.session_state.routines.append({"task": r_input, "done": False}); st.rerun()
    for idx, item in enumerate(st.session_state.routines):
        cc1, cc2 = st.columns([5, 1])
        item['done'] = cc1.checkbox(item['task'], value=item['done'], key=f"r_{idx}")
        if cc2.button("X", key=f"d_{idx}"): st.session_state.routines.pop(idx); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)

# [플래너 페이지 - 초기 버전으로 복구]
def planner():
    st.markdown("<h1 class='main-title'>✍️ DAILY PLANNER</h1>", unsafe_allow_html=True)
    
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        st.subheader("📋 오늘의 공부 기록")
        with st.form("planner_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            sub = c1.text_input("과목명", placeholder="예: 수학")
            con = c2.text_input("공부 내용", placeholder="예: 미분법")
            
            goal = st.slider("목표 시간 (h)", 0.5, 12.0, 1.0, step=0.5)
            actual = st.slider("실제 공부 시간 (h)", 0.0, 12.0, 0.0, step=0.5)
            
            status = st.radio("성취도", ["완벽(O)", "보통(△)", "미흡(X)"], horizontal=True)
            
            if st.form_submit_button("기록 저장 💾"):
                icon = "O" if "완벽" in status else ("△" if "보통" in status else "X")
                st.session_state.planner.append({
                    "날짜": date.today(), "과목": sub, "내용": con, 
                    "목표": goal, "실제": actual, "성취도": icon
                })
                st.rerun()

    if st.session_state.planner:
        st.markdown("### 📋 기록된 리스트")
        df = pd.DataFrame(st.session_state.planner)
        st.dataframe(df[['날짜', '과목', '내용', '목표', '실제', '성취도']], use_container_width=True, hide_index=True)
        if st.button("🗑️ 전체 삭제"):
            st.session_state.planner = []
            st.rerun()
    st.markdown("<br><br><br>", unsafe_allow_html=True)

# [통계 페이지 - 21일 레이스 달력]
def stats():
    st.markdown("<h1 class='main-title'>📊 STATISTICS</h1>", unsafe_allow_html=True)
    
    # 21일 레이스 섹션
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏃 STAGE 1: 21일의 레이스")
    
    # 데이터 정리 (날짜별 최고 성취도 추출)
    df = pd.DataFrame(st.session_state.planner) if st.session_state.planner else pd.DataFrame()
    
    race_html = "<div class='race-container'>"
    for i in range(1, 22):
        # 단순히 1일부터 21일까지 시각적으로 표현 (데이터 매칭 로직)
        status_class = ""
        if not df.empty:
            # 여기서는 예시로 기록이 있는 날을 체크됨으로 표시
            if i <= len(df['날짜'].unique()):
                status_class = "completed"
                if "O" in df.values: status_class = "perfect"
        
        race_html += f"<div class='race-box {status_class}'>{i}</div>"
    race_html += "</div>"
    
    st.markdown(race_html, unsafe_allow_html=True)
    st.markdown("<p style='text-align:right; font-size:0.8rem; color:grey; margin-top:10px;'>기록을 남길 때마다 칸이 채워집니다! 🏆</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("📊 과목별 비중")
            fig = px.pie(df, values='실제', names='과목', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("📈 공부 시간 기록")
            st.metric("총 시간", f"{df['실제'].sum()}h")
            st.metric("기록 횟수", f"{len(df)}회")
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)

# ---------- 5. 메인 렌더링 & 하단 네비게이션 ----------

if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats()

# 하단 네비게이션 (가장 마지막에 렌더링)
st.markdown("---")
nav_col1, nav_col2, nav_col3 = st.columns(3)
if nav_col1.button("🏠 Home", use_container_width=True): st.session_state.page = "home"; st.rerun()
if nav_col2.button("✍️ Planner", use_container_width=True): st.session_state.page = "planner"; st.rerun()
if nav_col3.button("📊 Stats", use_container_width=True): st.session_state.page = "stats"; st.rerun()
