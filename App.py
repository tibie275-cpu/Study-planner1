import streamlit as st
import pandas as pd
import random
import time
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

# ---------- 2. 커스텀 스타일 (하늘색 테마 & 슬라이더 색상) ----------
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    
    /* 카드 스타일 */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(135, 206, 250, 0.1);
        border: 1px solid #E6F3FF;
    }
    
    /* 타이틀 디자인 */
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        color: #5DADE2;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* 타이머 박스 */
    .timer-display {
        font-size: 3.5rem;
        font-weight: 800;
        color: #56CCF2;
        text-align: center;
        background: #FFFFFF;
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #B3E5FC;
    }
    
    /* 버튼 스타일 */
    div.stButton > button {
        background-color: #87CEFA;
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: bold;
    }
    div.stButton > button:hover { background-color: #5DADE2; }

    /* 슬라이더 색상 변경 (하늘색) */
    div[data-baseweb="slider"] > div > div > div {
        background-color: #87CEFA !important;
    }
    div[role="slider"] {
        background-color: #5DADE2 !important;
        border: 2px solid white;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 3. 유틸리티 ----------
def now_kst(): return datetime.now(ZoneInfo("Asia/Seoul"))
quotes = ["오늘의 노력이 내일의 나를 만든다.", "공부는 배신하지 않는다.", "느려도 괜찮다. 멈추지만 마라."]

# ---------- 4. 페이지 함수 ----------

# [홈 페이지]
def home():
    st.markdown("<h1 class='main-title'>☁️ STUDY DASHBOARD</h1>", unsafe_allow_html=True)
    
    # 랜덤 명언
    st.markdown(f"<div class='card'><div style='color:#7FB3D5; font-size:0.9rem;'>오늘의 한 문장</div><div style='font-size:1.1rem; font-weight:600; color:#2E86C1;'>\"{random.choice(quotes)}\"</div></div>", unsafe_allow_html=True)

    # 기상/취침
    c1, c2 = st.columns(2)
    if c1.button("🌅 기상 인증", use_container_width=True): st.toast(f"기상! ({now_kst().strftime('%H:%M')})")
    if c2.button("🌙 취침 인증", use_container_width=True): st.toast(f"취침! ({now_kst().strftime('%H:%M')})")

    st.divider()

    # 연속 타이머
    st.markdown("<div class='card'><div style='font-weight:700; color:#5DADE2;'>⏱️ 집중 & 휴식 타이머</div>", unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    f_time = tc1.number_input("집중(분)", 1, 120, 25)
    b_time = tc2.number_input("휴식(분)", 1, 60, 5)
    
    if st.button("🚀 연속 타이머 시작", use_container_width=True):
        placeholder = st.empty()
        for i in range(f_time * 60, -1, -1):
            m, s = divmod(i, 60)
            placeholder.markdown(f"<div class='timer-display'>FOCUS<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
        st.toast("집중 끝! 휴식 시작 ☕")
        for i in range(b_time * 60, -1, -1):
            m, s = divmod(i, 60)
            placeholder.markdown(f"<div class='timer-display' style='color:#48C9B0; border-color:#48C9B0;'>BREAK<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
        st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

    # 루틴 관리
    st.markdown("<div class='card'><div style='font-weight:700; color:#5DADE2;'>✨ 나의 루틴</div>", unsafe_allow_html=True)
    r_input = st.text_input("루틴 추가", placeholder="예: 영단어 외우기")
    if st.button("추가"):
        if r_input: st.session_state.routines.append({"task": r_input, "done": False}); st.rerun()
    for idx, item in enumerate(st.session_state.routines):
        cc1, cc2 = st.columns([5, 1])
        item['done'] = cc1.checkbox(item['task'], value=item['done'], key=f"r_{idx}")
        if cc2.button("X", key=f"d_{idx}"): st.session_state.routines.pop(idx); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# [플래너 페이지]
def planner():
    st.markdown("<h1 class='main-title'>✍️ DAILY PLANNER</h1>", unsafe_allow_html=True)
    
    # 1. 계획 입력 (먼저 수행)
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        st.subheader("📅 공부 계획 세우기")
        with st.form("plan_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            sub = col1.text_input("과목명")
            con = col2.text_input("공부 내용")
            goal = st.slider("목표 시간 (시간)", 0.5, 12.0, 1.0, step=0.5)
            
            if st.form_submit_button("계획 등록 📌"):
                st.session_state.planner.append({
                    "id": time.time(), # 고유 ID
                    "날짜": date.today(),
                    "과목": sub,
                    "내용": con,
                    "목표": goal,
                    "실제": 0.0,
                    "성취도": "미완료",
                    "완료여부": False
                })
                st.rerun()

    # 2. 진행 중인 계획 리스트 & 실제 공부 결과 입력
    st.markdown("### ⏳ 현재 진행 중인 공부")
    for idx, item in enumerate(st.session_state.planner):
        if not item["완료여부"]:
            with st.expander(f"📍 {item['과목']} : {item['내용']} (목표: {item['목표']}h)"):
                with st.form(key=f"finish_form_{item['id']}"):
                    actual = st.slider("실제 공부 시간", 0.0, 12.0, item['목표'], step=0.5)
                    status = st.radio("성취도 선택", ["완벽(O)", "보통(△)", "미흡(X)"], horizontal=True)
                    
                    if st.form_submit_button("공부 완료 및 등록 ✅"):
                        icon = "O" if "완벽" in status else ("△" if "보통" in status else "X")
                        item["실제"] = actual
                        item["성취도"] = icon
                        item["완료여부"] = True
                        st.rerun()

    # 3. 완료된 오늘 기록 표시
    if any(i["완료여부"] for i in st.session_state.planner):
        st.markdown("### 📋 완료된 기록")
        done_list = [i for i in st.session_state.planner if i["완료여부"]]
        df = pd.DataFrame(done_list)
        st.dataframe(df[['과목', '내용', '목표', '실제', '성취도']], use_container_width=True, hide_index=True)
        
        if st.button("🗑️ 전체 데이터 초기화"):
            st.session_state.planner = []
            st.rerun()

# [통계 페이지]
def stats():
    st.markdown("<h1 class='main-title'>📊 STATISTICS</h1>", unsafe_allow_html=True)
    completed_plans = [i for i in st.session_state.planner if i["완료여부"]]
    
    if not completed_plans:
        st.info("완료된 데이터가 없습니다. 플래너에서 공부를 완료해주세요!")
        return

    df = pd.DataFrame(completed_plans)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("총 공부 시간", f"{df['실제'].sum()}h")
    c2.metric("오늘 완료 과목", f"{len(df)}개")
    c3.metric("최다 과목", df['과목'].mode()[0])

    # 과목별 차트
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    fig = px.pie(df, values='실제', names='과목', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 성취도 달력
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📅 성취도 달력")
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['점수'] = df['성취도'].map({"O": 3, "△": 2, "X": 1})
    daily = df.groupby('날짜')['점수'].mean().reset_index()
    
    fig_cal = px.scatter(daily, x='날짜', y=[1]*len(daily), size='점수', color='점수',
                         color_continuous_scale='Blues')
    fig_cal.update_yaxes(visible=False); fig_cal.update_layout(height=200)
    st.plotly_chart(fig_cal, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 5. 네비게이션 ----------
if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats()

st.markdown("<br><br><hr>", unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns(3)
if nav_col1.button("🏠 홈", use_container_width=True): st.session_state.page = "home"; st.rerun()
if nav_col2.button("✍️ 플래너", use_container_width=True): st.session_state.page = "planner"; st.rerun()
if nav_col3.button("📊 통계", use_container_width=True): st.session_state.page = "stats"; st.rerun()
