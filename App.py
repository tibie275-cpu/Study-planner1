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

# ---------- 2. 커스텀 스타일 (화이트 & 미니멀 스카이블루) ----------
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    
    /* 카드 스타일 */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(135, 206, 250, 0.1);
        border: 1px solid #E6F3FF;
    }
    
    /* 타이틀 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #5DADE2;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* 타이머 박스 */
    .timer-display {
        font-size: 4rem;
        font-weight: 800;
        color: #5DADE2;
        text-align: center;
        background: #FFFFFF;
        border-radius: 20px;
        padding: 30px;
        margin: 15px 0;
        border: 2px solid #E6F3FF;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* 버튼 스타일 */
    div.stButton > button {
        background-color: #87CEFA;
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }
    div.stButton > button:hover { background-color: #5DADE2; }

    /* [수정] 슬라이더(조절 바) 화이트 테마 디자인 */
    /* 1. 슬라이더 전체 트랙 배경 */
    div[data-baseweb="slider"] > div {
        background-color: transparent !important;
    }
    /* 2. 비활성 트랙 색상 (연한 하늘색으로 가이드라인만) */
    div[data-baseweb="slider"] > div > div {
        background-color: #E6F3FF !important;
    }
    /* 3. 활성 트랙 색상 (깔끔한 화이트) */
    div[data-baseweb="slider"] > div > div > div {
        background-color: #FFFFFF !important;
        border: 1px solid #B3E5FC;
    }
    /* 4. 조절 버튼 (핸들) - 화이트 & 그림자 */
    div[role="slider"] {
        background-color: #FFFFFF !important;
        border: 2px solid #87CEFA !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
        width: 20px !important;
        height: 20px !important;
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
    
    # 명언 카드
    st.markdown(f"<div class='card'><div style='color:#7FB3D5; font-size:0.9rem;'>Today's Quote</div><div style='font-size:1.1rem; font-weight:600; color:#2E86C1;'>\"{random.choice(quotes)}\"</div></div>", unsafe_allow_html=True)

    # 기상/취침
    c1, c2 = st.columns(2)
    if c1.button("🌅 기상 인증", use_container_width=True): st.toast("Good Morning! ☀️")
    if c2.button("🌙 취침 인증", use_container_width=True): st.toast("Good Night! 😴")

    st.divider()

    # [수정] 연속 타이머 (종료 알림 강화)
    st.markdown("<div class='card'><div style='font-weight:700; color:#5DADE2;'>⏱️ 집중 & 휴식 타이머</div>", unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    f_time = tc1.number_input("집중(분)", 1, 120, 25)
    b_time = tc2.number_input("휴식(분)", 1, 60, 5)
    
    if st.button("🚀 타이머 시작 (연속)", use_container_width=True):
        placeholder = st.empty()
        
        # 1. 집중 모드
        for i in range(f_time * 60, -1, -1):
            m, s = divmod(i, 60)
            placeholder.markdown(f"<div class='timer-display'><span style='font-size:1.5rem; color:#87CEFA;'>FOCUS</span><br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            
        # [추가] 집중 종료 알림
        placeholder.markdown("<div class='timer-display' style='color:#FFB6C1; border-color:#FFB6C1;'>TIME UP!<br><span style='font-size:1.5rem;'>휴식을 시작합니다</span></div>", unsafe_allow_html=True)
        st.toast("집중 시간이 끝났습니다! ☕")
        time.sleep(2)
        
        # 2. 휴식 모드
        for i in range(b_time * 60, -1, -1):
            m, s = divmod(i, 60)
            placeholder.markdown(f"<div class='timer-display' style='color:#48C9B0; border-color:#48C9B0;'><span style='font-size:1.5rem; color:#48C9B0;'>BREAK</span><br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
        
        # [추가] 전체 종료 알림
        placeholder.markdown("<div class='timer-display' style='color:#5DADE2;'>FINISH!<br><span style='font-size:1.5rem;'>세트 완료</span></div>", unsafe_allow_html=True)
        st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

    # 루틴 관리
    st.markdown("<div class='card'><div style='font-weight:700; color:#5DADE2;'>✨ 나의 루틴</div>", unsafe_allow_html=True)
    r_input = st.text_input("루틴 추가", placeholder="할 일을 입력하세요")
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
    
    # 1. 계획 입력
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        st.subheader("📅 계획 등록")
        with st.form("plan_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            sub = col1.text_input("과목명")
            con = col2.text_input("공부 내용")
            # [수정] 화이트 테마 슬라이더 적용 구간
            goal = st.slider("목표 시간 (h)", 0.5, 12.0, 1.0, step=0.5)
            
            if st.form_submit_button("계획 확정"):
                st.session_state.planner.append({
                    "id": time.time(),
                    "날짜": date.today(),
                    "과목": sub,
                    "내용": con,
                    "목표": goal,
                    "실제": 0.0,
                    "성취도": "미완료",
                    "완료여부": False
                })
                st.rerun()

    # 2. 진행 중인 계획
    st.markdown("### ⏳ 공부 중")
    for idx, item in enumerate(st.session_state.planner):
        if not item["완료여부"]:
            with st.expander(f"📍 {item['과목']} : {item['내용']}"):
                with st.form(key=f"finish_form_{item['id']}"):
                    # [수정] 화이트 테마 슬라이더 적용 구간
                    actual = st.slider("실제 공부 시간 (h)", 0.0, 12.0, item['목표'], step=0.5)
                    status = st.radio("성취도", ["완벽(O)", "보통(△)", "미흡(X)"], horizontal=True)
                    
                    if st.form_submit_button("완료 기록하기"):
                        icon = "O" if "완벽" in status else ("△" if "보통" in status else "X")
                        item["실제"] = actual
                        item["성취도"] = icon
                        item["완료여부"] = True
                        st.rerun()

    # 3. 완료 목록
    if any(i["완료여부"] for i in st.session_state.planner):
        st.markdown("### 📋 완료 기록")
        done_list = [i for i in st.session_state.planner if i["완료여부"]]
        df = pd.DataFrame(done_list)
        st.dataframe(df[['과목', '내용', '목표', '실제', '성취도']], use_container_width=True, hide_index=True)

# [통계 페이지]
def stats():
    st.markdown("<h1 class='main-title'>📊 STATISTICS</h1>", unsafe_allow_html=True)
    completed_plans = [i for i in st.session_state.planner if i["완료여부"]]
    
    if not completed_plans:
        st.info("기록된 데이터가 없습니다.")
        return

    df = pd.DataFrame(completed_plans)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", f"{df['실제'].sum()}h")
    c2.metric("Subjects", f"{len(df)}")
    c3.metric("Best", df['과목'].mode()[0])

    # 파이 차트
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    fig = px.pie(df, values='실제', names='과목', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 성취도 달력
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📅 Achievement Calendar")
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['점수'] = df['성취도'].map({"O": 3, "△": 2, "X": 1})
    daily = df.groupby('날짜')['점수'].mean().reset_index()
    
    fig_cal = px.scatter(daily, x='날짜', y=[1]*len(daily), size='점수', color='점수', color_continuous_scale='Blues')
    fig_cal.update_yaxes(visible=False); fig_cal.update_layout(height=200)
    st.plotly_chart(fig_cal, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 5. 네비게이션 ----------
st.markdown("<br><br><hr>", unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns(3)
if nav_col1.button("🏠 Home", use_container_width=True): st.session_state.page = "home"; st.rerun()
if nav_col2.button("✍️ Planner", use_container_width=True): st.session_state.page = "planner"; st.rerun()
if nav_col3.button("📊 Stats", use_container_width=True): st.session_state.page = "stats"; st.rerun()

if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats()
