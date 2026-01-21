import streamlit as st
import pandas as pd
from datetime import datetime, date
import random

st.set_page_config(page_title="Study Planner", layout="centered")

# ---------- 상태 ----------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "planner" not in st.session_state:
    st.session_state.planner = []

# ---------- 스타일 ----------
st.markdown("""
<style>
body {
    background-color: #F9FAFB;
}
.card {
    background: white;
    padding: 1rem;
    border-radius: 16px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
.bottom {
    position: fixed;
    bottom: 0;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------- 인용구 ----------
quotes = [
    "오늘의 노력이 내일의 나를 만든다.",
    "지금 포기하면 영원히 여기다.",
    "공부는 배신하지 않는다.",
    "천천히 가도 멈추지만 마라."
]

# ---------- 페이지 ----------
def home():
    st.markdown(f"<div class='card'><h3>📌 오늘의 한 문장</h3><p>{random.choice(quotes)}</p></div>", unsafe_allow_html=True)

    if st.button("🌅 기상 인증"):
        st.success(f"기상 시간: {datetime.now().strftime('%H:%M')}")

    if st.button("🌙 취침 인증"):
        st.success(f"취침 시간: {datetime.now().strftime('%H:%M')}")

def planner():
    st.markdown("<div class='card'><h3>✍️ 오늘의 플래너</h3></div>", unsafe_allow_html=True)

    subject = st.text_input("과목")
    content = st.text_input("공부 내용")
    goal = st.number_input("목표 시간 (시간)", 0.0, 24.0)
    actual = st.number_input("실제 공부 시간 (시간)", 0.0, 24.0)

    if st.button("➕ 추가"):
        st.session_state.planner.append({
            "날짜": date.today(),
            "과목": subject,
            "내용": content,
            "목표": goal,
            "실제": actual
        })

    if st.session_state.planner:
        df = pd.DataFrame(st.session_state.planner)
        st.dataframe(df)
        st.success(f"총 공부 시간: {df['실제'].sum()} 시간")

def stats():
    if not st.session_state.planner:
        st.info("아직 데이터가 없어.")
        return

    df = pd.DataFrame(st.session_state.planner)
    st.bar_chart(df.groupby("과목")["실제"].sum())

# ---------- 네비 ----------
if st.session_state.page == "home":
    home()
elif st.session_state.page == "planner":
    planner()
elif st.session_state.page == "stats":
    stats()

st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🏠 홈"):
        st.session_state.page = "home"
with c2:
    if st.button("✍️ 플래너"):
        st.session_state.page = "planner"
with c3:
    if st.button("📊 통계"):
        st.session_state.page = "stats"
