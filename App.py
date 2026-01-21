import streamlit as st
import pandas as pd
import random
import time
import calendar
from datetime import date, datetime
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

# ---------- 2. 커스텀 스타일 (빨간색 제거 & UI 최적화) ----------
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    
    .card {
        background: white; padding: 1.5rem; border-radius: 20px;
        margin-bottom: 1.5rem; border: 1px solid #E6F3FF;
        box-shadow: 0 4px 15px rgba(135, 206, 250, 0.1);
    }
    
    .main-title {
        font-size: 2.2rem; font-weight: 800; color: #5DADE2;
        text-align: center; margin-bottom: 1rem;
    }

    /* 달력 그리드 */
    .race-container {
        display: grid; grid-template-columns: repeat(7, 1fr);
        gap: 8px; margin-top: 10px;
    }
    .race-box {
        aspect-ratio: 1 / 1; background-color: #F8F9FA;
        border: 2px solid #E6F3FF; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; color: #BDC3C7; font-size: 0.8rem;
    }
    .race-box.today { border: 2px solid #5DADE2; color: #5DADE2; background-color: #E1F5FE; }
    .race-box.completed { background-color: #87CEFA; border-color: #5DADE2; color: white; }

    /* [수정] 모든 빨간색 요소 제거 (슬라이더 숫자 및 라디오 버튼) */
    /* 1. 슬라이더 상단 숫자 */
    div[data-testid="stSliderTickBar"] span, span[data-baseweb="typography"] {
        color: #5DADE2 !important;
    }
    /* 2. 슬라이더 트랙 및 핸들 */
    div[data-baseweb="slider"] > div > div { background: #E6F3FF !important; }
    div[data-baseweb="slider"] > div > div > div { background: #FFFFFF !important; border: 1px solid #B3E5FC; }
    div[role="slider"] { background-color: #FFFFFF !important; border: 2px solid #87CEFA !important; }

    /* 3. 라디오 버튼(상태 표시) 빨간색 제거 */
    div[data-baseweb="radio"] div[data-testid="stWidgetLabel"] p { color: #5DADE2 !important; }
    div[data-baseweb="radio"] label div { border-color: #87CEFA !important; }
    div[data-baseweb="radio"] label div[dir] { background-color: #87CEFA !important; }

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

# ---------- 4. 페이지 함수 ----------

def home():
    st.markdown("<h1 class='main-title'>☁️ STUDY DASHBOARD</h1>", unsafe_allow_html=True)
    
    # ⏱️ 뽀모도로 타이머
    st.markdown("<div class='card'><div style='font-weight:700; color:#5DADE2;'>⏱️ 집중 & 휴식 타이머</div>", unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    f_time = tc1.number_input("집중(분)", 1, 120, 25)
    b_time = tc2.number_input("휴식(분)", 1, 60, 5)
    
    if st.button("🚀 타이머 시작", use_container_width=True):
        placeholder = st.empty()
        for i in range(f_time * 60, -1, -1):
            m, s = divmod(i, 60)
            placeholder.markdown(f"<div class='timer-display' style='font-size:3rem; text-align:center; padding:20px; border:2px solid #E6F3FF; border-radius:20px; color:#5DADE2; font-weight:800;'>FOCUS<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
        st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

    # ✨ 루틴 관리
    st.markdown("<div class='card'><div style='font-weight:700; color:#5DADE2;'>✨ 나의 루틴</div>", unsafe_allow_html=True)
    r_input = st.text_input("루틴 추가")
    if st.button("추가"):
        if r_input: st.session_state.routines.append({"task": r_input, "done": False}); st.rerun()
    for idx, item in enumerate(st.session_state.routines):
        item['done'] = st.checkbox(item['task'], value=item['done'], key=f"r_{idx}")
    st.markdown("</div>", unsafe_allow_html=True)

# [수정된 플래너 페이지: 계획 등록 -> 결과 입력]
def planner():
    st.markdown("<h1 class='main-title'>✍️ DAILY PLANNER</h1>", unsafe_allow_html=True)
    
    # 1. 계획 등록 (먼저 입력)
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        st.subheader("📅 공부 계획 세우기")
        with st.form("plan_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            sub = c1.text_input("과목명")
            con = c2.text_input("공부 내용")
            goal = st.slider("목표 시간 (h)", 0.5, 12.0, 1.0, step=0.5)
            if st.form_submit_button("계획 확정 📌"):
                st.session_state.planner.append({
                    "id": time.time(), "날짜": date.today(), "과목": sub, "내용": con, 
                    "목표": goal, "실제": 0.0, "성취도": "미완료", "완료여부": False
                })
                st.rerun()

    # 2. 결과 입력 (진행 중인 공부)
    st.markdown("### ⏳ 현재 진행 중인 공부")
    for item in st.session_state.planner:
        if not item["완료여부"]:
            with st.expander(f"📍 {item['과목']} : {item['내용']} (목표: {item['목표']}h)"):
                with st.form(key=f"finish_{item['id']}"):
                    actual = st.slider("실제 공부 시간 (h)", 0.0, 12.0, item['목표'], step=0.5)
                    status = st.radio("성취도", ["완벽(O)", "보통(△)", "미흡(X)"], horizontal=True)
                    if st.form_submit_button("공부 완료 기록 ✅"):
                        item["실제"] = actual
                        item["성취도"] = "O" if "완벽" in status else ("△" if "보통" in status else "X")
                        item["완료여부"] = True
                        st.rerun()

    # 3. 완료 목록
    if any(i["완료여부"] for i in st.session_state.planner):
        st.markdown("### 📋 완료된 기록")
        df = pd.DataFrame([i for i in st.session_state.planner if i["완료여부"]])
        st.dataframe(df[['과목', '내용', '목표', '실제', '성취도']], use_container_width=True, hide_index=True)

# [수정된 통계 페이지: 월별 자동 달력]
def stats():
    st.markdown("<h1 class='main-title'>📊 STATISTICS</h1>", unsafe_allow_html=True)
    
    today = now_kst().date()
    year, month = today.year, today.month
    _, last_day = calendar.monthrange(year, month)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader(f"📅 {year}년 {month}월의 레이스")
    
    # 실제 공부 기록 날짜 추출
    done_dates = [i["날짜"] for i in st.session_state.planner if i["완료여부"]]
    
    race_html = "<div class='race-container'>"
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        status_class = ""
        if current_date in done_dates: status_class = "completed"
        elif current_date == today: status_class = "today"
        
        race_html += f"<div class='race-box {status_class}'>{day}</div>"
    race_html += "</div>"
    
    st.markdown(race_html, unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:right; font-size:0.8rem; color:grey; margin-top:10px;'>오늘은 {today.day}일입니다.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 기본 통계 수치
    completed = [i for i in st.session_state.planner if i["완료여부"]]
    if completed:
        df = pd.DataFrame(completed)
        c1, c2 = st.columns(2)
        c1.metric("총 공부 시간", f"{df['실제'].sum()}h")
        c2.metric("오늘의 과목", f"{len(df[df['날짜']==today])}개")

# ---------- 5. 메인 실행 및 하단 네비게이션 ----------

if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats()

st.markdown("<br><br><br><br>", unsafe_allow_html=True) # 하단 여백
st.markdown("---")
nav_col1, nav_col2, nav_col3 = st.columns(3)
if nav_col1.button("🏠 Home", use_container_width=True): st.session_state.page = "home"; st.rerun()
if nav_col2.button("✍️ Planner", use_container_width=True): st.session_state.page = "planner"; st.rerun()
if nav_col3.button("📊 Stats", use_container_width=True): st.session_state.page = "stats"; st.rerun()
