import streamlit as st
import pandas as pd
import random
import time
from datetime import date, datetime
from zoneinfo import ZoneInfo
import plotly.express as px

# ---------- 1. 기본 설정 ----------
st.set_page_config(
    page_title="Study Planner",
    page_icon="☁️", # 아이콘 구름으로 변경
    layout="centered",
)

# 상태 관리 초기화
if "page" not in st.session_state:
    st.session_state.page = "home"
if "planner" not in st.session_state:
    st.session_state.planner = []
if "routines" not in st.session_state:
    st.session_state.routines = []

# ---------- 2. 커스텀 스타일 (연한 하늘색 테마) ----------
st.markdown("""
<style>
    /* 전체 배경: 아주 연한 화이트 블루 */
    .stApp { background-color: #F0F8FF; }
    
    /* 카드 스타일 */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(135, 206, 250, 0.1); /* 하늘색 그림자 */
        border: 1px solid #E6F3FF;
    }
    
    /* 타이틀 디자인 */
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        color: #5DADE2; /* 진한 하늘색 텍스트 */
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* 타이머 박스 */
    .timer-display {
        font-size: 3.5rem;
        font-weight: 800;
        color: #56CCF2; /* 밝은 하늘색 숫자 */
        text-align: center;
        background: #FFFFFF;
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #B3E5FC;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* 버튼 스타일 (연한 하늘색) */
    div.stButton > button {
        background-color: #87CEFA; /* Light Sky Blue */
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #5DADE2;
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
    st.markdown("<h1 class='main-title'>☁️ STUDY DASHBOARD</h1>", unsafe_allow_html=True)
    
    # 랜덤 명언
    st.markdown(f"""
    <div class='card'>
        <div style='color:#7FB3D5; font-size:0.9rem; margin-bottom:5px;'>오늘의 한 문장</div>
        <div style='font-size:1.1rem; font-weight:600; color:#2E86C1;'>"{random.choice(quotes)}"</div>
    </div>
    """, unsafe_allow_html=True)

    # 기상/취침
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🌅 기상 인증", use_container_width=True):
            st.toast(f"기상 완료! ({now_kst().strftime('%H:%M')})")
    with c2:
        if st.button("🌙 취침 인증", use_container_width=True):
            st.toast(f"수고하셨어요! ({now_kst().strftime('%H:%M')})")

    st.divider()

    # [수정됨] ⏱️ 연속 뽀모도로 타이머 (사용자 설정 + 연속 모드)
    st.markdown("<div class='card'><div style='font-weight:700; font-size:1.1rem; color:#5DADE2;'>⏱️ 집중 & 휴식 타이머</div>", unsafe_allow_html=True)
    
    # 시간 설정
    tc1, tc2 = st.columns(2)
    f_time = tc1.number_input("집중(분)", 1, 120, 25)
    b_time = tc2.number_input("휴식(분)", 1, 60, 5)
    
    if st.button("🚀 연속 타이머 시작", use_container_width=True):
        placeholder = st.empty()
        
        # 1. 집중 모드
        for i in range(f_time * 60, -1, -1):
            mins, secs = divmod(i, 60)
            placeholder.markdown(f"<div class='timer-display'>FOCUS<br>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
        
        st.toast("집중 끝! 꿀같은 휴식 시작 ☁️")
        
        # 2. 휴식 모드 (자동 전환)
        for i in range(b_time * 60, -1, -1):
            mins, secs = divmod(i, 60)
            placeholder.markdown(f"<div class='timer-display' style='color:#76D7C4; border-color:#76D7C4;'>BREAK<br>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            
        st.balloons()
        st.success("한 세트 완주 성공! 대단해요 👍")
    st.markdown("</div>", unsafe_allow_html=True)

    # [추가됨] ✅ 데일리 루틴
    st.markdown("<div class='card'><div style='font-weight:700; font-size:1.1rem; color:#5DADE2;'>✨ 나의 루틴</div>", unsafe_allow_html=True)
    
    r_col1, r_col2 = st.columns([4, 1])
    new_routine = r_col1.text_input("루틴 추가", label_visibility="collapsed", placeholder="예: 물 마시기")
    if r_col2.button("추가"):
        if new_routine:
            st.session_state.routines.append({"task": new_routine, "done": False})
            st.rerun()
            
    if st.session_state.routines:
        for idx, item in enumerate(st.session_state.routines):
            cc1, cc2 = st.columns([5, 1])
            item['done'] = cc1.checkbox(item['task'], value=item['done'], key=f"r_{idx}")
            if cc2.button("X", key=f"d_{idx}"):
                st.session_state.routines.pop(idx)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# [플래너 페이지]
def planner():
    st.markdown("<h1 class='main-title'>✍️ DAILY PLANNER</h1>", unsafe_allow_html=True)
    
    # 입력 폼 (시간 기록 유지 + 성취도 추가)
    with st.expander("➕ 학습 기록하기", expanded=True):
        with st.form("planner_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            sub = col1.text_input("과목명", placeholder="예: 수학")
            con = col2.text_input("공부 내용", placeholder="예: 미분법")
            
            goal = st.slider("목표 시간 (시간)", 0.5, 12.0, 1.0, step=0.5)
            actual = st.slider("실제 공부 시간 (시간)", 0.0, 12.0, 0.0, step=0.5)
            
            # [추가됨] 성취도 (달력을 위해 필요)
            status = st.radio("성취도", ["완벽(O)", "보통(△)", "미흡(X)"], horizontal=True)
            
            if st.form_submit_button("기록 저장"):
                # 기호 변환
                icon = "O" if "완벽" in status else ("△" if "보통" in status else "X")
                
                st.session_state.planner.append({
                    "날짜": date.today(), # datetime 객체 유지
                    "과목": sub,
                    "내용": con,
                    "목표": goal,
                    "실제": actual,
                    "완료": actual >= goal,
                    "성취도": icon
                })
                st.rerun()

    if st.session_state.planner:
        st.markdown("### 📋 오늘의 공부")
        df = pd.DataFrame(st.session_state.planner)
        
        # 날짜 포맷 깔끔하게 보여주기용 복사본
        view_df = df.copy()
        view_df['날짜'] = pd.to_datetime(view_df['날짜']).dt.strftime('%m-%d')
        st.dataframe(view_df[['날짜', '과목', '내용', '목표', '실제', '성취도']], use_container_width=True, hide_index=True)
        
        if st.button("🗑️ 초기화"):
            st.session_state.planner = []
            st.rerun()

# [통계 페이지]
def stats():
    st.markdown("<h1 class='main-title'>📊 STATISTICS</h1>", unsafe_allow_html=True)
    
    if not st.session_state.planner:
        st.info("데이터가 없습니다. 플래너를 작성해주세요!")
        return

    df = pd.DataFrame(st.session_state.planner)
    
    # 상단 요약
    c1, c2, c3 = st.columns(3)
    c1.metric("총 공부 시간", f"{df['실제'].sum()}h")
    c2.metric("목표 달성률", f"{(df['완료'].mean()*100):.0f}%")
    c3.metric("최다 과목", df['과목'].mode()[0])

    # 1. 과목별 비중 (파이 차트)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔹 과목별 시간 비중")
    fig = px.pie(df, values='실제', names='과목', hole=0.4, 
                 color_discrete_sequence=px.colors.sequential.Blues) # 하늘색 계열
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # [추가됨] 2. 성취도 달력
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📅 성취도 달력")
    
    # 데이터 전처리
    df['날짜'] = pd.to_datetime(df['날짜'])
    score_map = {"O": 3, "△": 2, "X": 1}
    df['점수'] = df['성취도'].map(score_map)
    
    # 날짜별 평균 점수
    daily = df.groupby('날짜')['점수'].mean().reset_index()
    
    fig_cal = px.scatter(daily, x='날짜', y=[1]*len(daily), 
                         size='점수', color='점수',
                         color_continuous_scale='Blues', # 하늘색 스케일
                         title="파란 점이 클수록 완벽한 하루! 💙")
    fig_cal.update_yaxes(visible=False, showticklabels=False)
    fig_cal.update_layout(height=200)
    st.plotly_chart(fig_cal, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 5. 메인 네비게이션 (하단 유지) ----------
if st.session_state.page == "home":
    home()
elif st.session_state.page == "planner":
    planner()
elif st.session_state.page == "stats":
    stats()

st.markdown("<br><br><hr>", unsafe_allow_html=True)
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
