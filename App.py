import streamlit as st
import pandas as pd
import time
from datetime import date, datetime
import plotly.express as px

# ---------- 1. 페이지 기본 설정 ----------
st.set_page_config(
    page_title="STUDY DASHBOARD",
    page_icon="📘",
    layout="centered"
)

# 세션 상태 초기화 (데이터 유지용)
if "page" not in st.session_state:
    st.session_state.page = "home"
if "planner" not in st.session_state:
    st.session_state.planner = []
if "routines" not in st.session_state:
    st.session_state.routines = []

# ---------- 2. 디자인 (White & Sky Blue) ----------
st.markdown("""
<style>
    /* 전체 배경 화이트 */
    .stApp { background-color: #FFFFFF; }
    
    /* 카드 스타일 (깔끔한 그림자) */
    .card {
        background: #F8FAFC;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* 타이틀 폰트 */
    .main-title {
        font-family: 'Helvetica', sans-serif;
        color: #2C3E50;
        font-weight: 800;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* 버튼 스타일 (스카이 블루) */
    div.stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        border: none;
        height: 3em;
        font-weight: 600;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background-color: #2980b9;
        color: white;
    }
    
    /* 타이머 숫자 스타일 */
    .timer-box {
        font-size: 3rem;
        font-weight: bold;
        color: #3498db;
        text-align: center;
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #3498db;
        margin: 10px 0;
    }
    
    /* 네비게이션 버튼 (상단) */
    .nav-btn { margin: 5px; }
</style>
""", unsafe_allow_html=True)

# ---------- 3. 상단 네비게이션 ----------
st.markdown("<h1 class='main-title'>STUDY DASHBOARD</h1>", unsafe_allow_html=True)

col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    if st.button("🏠 HOME", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
with col_n2:
    if st.button("✍️ PLANNER", use_container_width=True):
        st.session_state.page = "planner"
        st.rerun()
with col_n3:
    if st.button("📊 STATS", use_container_width=True):
        st.session_state.page = "stats"
        st.rerun()

st.markdown("---")

# ---------- 4. 페이지별 기능 구현 ----------

# [PAGE 1] 홈: 타이머 & 루틴
def home():
    # 1. 뽀모도로 연속 타이머
    st.subheader("⏱️ Focus Timer")
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        f_min = c1.number_input("집중 시간 (분)", 1, 120, 50)
        b_min = c2.number_input("휴식 시간 (분)", 1, 60, 10)
        
        if st.button("Start Continuous Session", use_container_width=True):
            placeholder = st.empty()
            
            # 집중 모드
            total_f = f_min * 60
            for t in range(total_f, -1, -1):
                m, s = divmod(t, 60)
                placeholder.markdown(f"<div class='timer-box'>🔥 FOCUS<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
                time.sleep(1)
            
            st.toast("Focus Complete! Starting Break...")
            
            # 휴식 모드 (자동 전환)
            total_b = b_min * 60
            for t in range(total_b, -1, -1):
                m, s = divmod(t, 60)
                placeholder.markdown(f"<div class='timer-box' style='color:#2ecc71; border-color:#2ecc71;'>☕ BREAK<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
                time.sleep(1)
                
            st.success("Session Cycle Finished!")
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. 루틴 관리
    st.subheader("✅ Daily Routine")
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col_r1, col_r2 = st.columns([4, 1])
        new_routine = col_r1.text_input("새 루틴 입력", label_visibility="collapsed", placeholder="예: 영단어 50개 암기")
        
        if col_r2.button("Add"):
            if new_routine:
                st.session_state.routines.append({"task": new_routine, "done": False})
                st.rerun()
        
        if st.session_state.routines:
            for i, r in enumerate(st.session_state.routines):
                rc1, rc2 = st.columns([5, 1])
                # 체크박스로 완료 상태 토글
                r['done'] = rc1.checkbox(r['task'], value=r['done'], key=f"rout_{i}")
                # 삭제 버튼
                if rc2.button("Del", key=f"del_rout_{i}"):
                    st.session_state.routines.pop(i)
                    st.rerun()
        else:
            st.info("등록된 루틴이 없습니다.")
        st.markdown("</div>", unsafe_allow_html=True)


# [PAGE 2] 플래너: 시간 기록 + 성취도
def planner():
    st.subheader("📝 Study Log")
    
    # 입력 폼
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.form("study_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            # 기존 요청했던 시간 기록 기능들 복구
            subject = col1.text_input("과목명", placeholder="수학")
            content = col2.text_input("공부 내용", placeholder="미적분 문제풀이")
            
            goal_time = col1.number_input("목표 시간 (Hour)", 0.0, 24.0, 1.0, step=0.5)
            actual_time = col2.number_input("실제 시간 (Hour)", 0.0, 24.0, 0.0, step=0.5)
            
            # 성취도 선택 (O, 세모, X)
            achievement = st.radio("성취도", ["Perfect (O)", "So-so (△)", "Bad (X)"], horizontal=True)
            
            submitted = st.form_submit_button("Record Entry")
            
            if submitted:
                # 성취도 기호 변환
                if "Perfect" in achievement: status_icon = "O"
                elif "So-so" in achievement: status_icon = "△"
                else: status_icon = "X"
                
                st.session_state.planner.append({
                    "Date": date.today().strftime("%Y-%m-%d"),
                    "Subject": subject,
                    "Content": content,
                    "Goal(H)": goal_time,
                    "Actual(H)": actual_time,
                    "Status": status_icon
                })
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 데이터 테이블 표시
    if st.session_state.planner:
        df = pd.DataFrame(st.session_state.planner)
        
        # 보기 좋게 컬럼 순서 정렬
        st.dataframe(
            df[["Date", "Subject", "Content", "Goal(H)", "Actual(H)", "Status"]], 
            use_container_width=True,
            hide_index=True
        )
        
        # 간단한 합계 통계
        total_actual = df["Actual(H)"].sum()
        st.caption(f"📌 Total Study Time: {total_actual} Hours")


# [PAGE 3] 통계 & 달력
def stats():
    st.subheader("📊 Statistics & Calendar")
    
    if not st.session_state.planner:
        st.info("아직 데이터가 없습니다. 플래너에 기록을 남겨보세요.")
        return
        
    df = pd.DataFrame(st.session_state.planner)
    
    # 1. 상단 메트릭
    m1, m2, m3 = st.columns(3)
    total_time = df['Actual(H)'].sum()
    avg_time = df['Actual(H)'].mean()
    perfect_count = len(df[df['Status'] == "O"])
    
    m1.metric("Total Hours", f"{total_time}h")
    m2.metric("Avg Hours/Session", f"{avg_time:.1f}h")
    m3.metric("Perfect Days", f"{perfect_count}회")
    
    # 2. 과목별 공부 시간 (파이 차트)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("##### 🔹 Subject Distribution")
    fig_pie = px.pie(df, values='Actual(H)', names='Subject', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 3. 성취도 달력 (Dot Plot)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("##### 🔹 Achievement Calendar")
    
    # 날짜별로 그룹화 (같은 날 여러 과목 공부했을 수 있으므로)
    # 성취도를 점수로 환산: O=3, △=2, X=1
    score_map = {"O": 3, "△": 2, "X": 1}
    df['Score'] = df['Status'].map(score_map)
    
    # 날짜 포맷 통일
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 날짜별 평균 점수 계산
    daily_stats = df.groupby('Date')['Score'].mean().reset_index()
    
    # 버블 차트로 달력처럼 표현
    fig_cal = px.scatter(
        daily_stats, x='Date', y=[1]*len(daily_stats),
        size='Score', color='Score',
        color_continuous_scale='Blues',
        size_max=20,
        hover_data={'Date': True, 'Score': False}
    )
    fig_cal.update_yaxes(visible=False, showticklabels=False)
    fig_cal.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_cal, use_container_width=True)
    st.caption("파란 원이 클수록 그날의 성취도가 높다는 뜻입니다!")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 5. 메인 실행 로직 ----------
if st.session_state.page == "home":
    home()
elif st.session_state.page == "planner":
    planner()
elif st.session_state.page == "stats":
    stats()
