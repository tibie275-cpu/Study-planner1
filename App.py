import streamlit as st
import time
import pandas as pd
import plotly.express as px # 차트를 위해 추가 설치 필요: pip install plotly

# 페이지 설정
st.set_page_config(page_title="AI 스터디 플래너 PRO", layout="wide")

# 1. 커스텀 CSS (디자인)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #4A90E2;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .timer-box {
        text-align: center;
        padding: 20px;
        background: #262730;
        color: #00FF41;
        border-radius: 20px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 50px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 사이드바 - 설정
with st.sidebar:
    st.title("⚙️ 설정")
    total_hours = st.slider("하루 가용 시간 (시간)", 1, 15, 8)
    st.info("과목을 추가하고 아래 타이머를 활용해 보세요.")

# 3. 메인 화면 - 상단 대시보드
st.title("📚 스마트 AI 스터디 플래너")
col1, col2, col3 = st.columns(3)

# 예시 데이터 (실제 데이터와 연동 필요)
subjects = st.session_state.get('subjects', [])
total_planned = sum([s['hours'] for s in subjects]) if subjects else 0

col1.metric("총 과목 수", f"{len(subjects)}개")
col2.metric("계획된 시간", f"{total_planned}시간")
col3.metric("남은 가용 시간", f"{total_hours - total_planned}시간")

# 4. 중앙 레이아웃 - 입력 및 차트
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📝 과목 추가")
    with st.form("subject_form", clear_on_submit=True):
        sub_name = st.text_input("과목명")
        sub_priority = st.select_slider("우선순위", options=range(1, 11))
        sub_hours = st.number_input("배정 시간", min_value=1)
        submitted = st.form_submit_button("과목 추가")
        
        if submitted:
            if 'subjects' not in st.session_state:
                st.session_state.subjects = []
            st.session_state.subjects.append({"name": sub_name, "priority": sub_priority, "hours": sub_hours})
            st.rerun()

with right_col:
    st.subheader("📊 과목별 비중")
    if subjects:
        df = pd.DataFrame(subjects)
        fig = px.pie(df, values='hours', names='name', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("과목을 추가하면 차트가 표시됩니다.")

# 5. ⏱️ 뽀모도로 타이머 섹션 (추가 제안 기능)
st.divider()
st.subheader("⏱️ 집중 뽀모도로 타이머")

t_col1, t_col2 = st.columns([1, 2])

with t_col1:
    timer_type = st.radio("모드 선택", ["Focus (25m)", "Short Break (5m)", "Long Break (15m)"])
    minutes = 25 if "Focus" in timer_type else (5 if "Short" in timer_type else 15)
    
    if st.button("타이머 시작"):
        ph = st.empty()
        for i in range(minutes * 60, -1, -1):
            mins, secs = divmod(i, 60)
            ph.markdown(f'<div class="timer-box">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
            time.sleep(1)
        st.balloons()
        st.success("고생하셨습니다! 잠시 휴식을 취하세요.")

with t_col2:
    st.write("### 💡 오늘의 팁")
    st.info("가장 우선순위가 높은 과목부터 타이머를 맞춰 시작해 보세요!")
    # 여기에 생성된 스케줄표(표)를 배치하면 좋습니다.
    if subjects:
        st.dataframe(pd.DataFrame(subjects), use_container_width=True)
