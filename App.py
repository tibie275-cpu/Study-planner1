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
if "pomodoro_running" not in st.session_state: st.session_state.pomodoro_running = False
if "pomodoro_stop" not in st.session_state: st.session_state.pomodoro_stop = False

# ---------- 2. 커스텀 스타일 ----------
st.markdown("""
<style>
.stApp { background-color: #FFFFFF; }

.card {
    background: white; padding: 1.5rem; border-radius: 20px;
    margin-bottom: 1.5rem; border: 1px solid #EEEEEE;
}

.main-title {
    font-size: 2.2rem; font-weight: 800; color: #333333;
    text-align: center; margin-bottom: 1rem;
}

.race-container {
    display: grid; grid-template-columns: repeat(7, 1fr);
    gap: 8px; margin-top: 10px;
}
.race-box {
    aspect-ratio: 1 / 1; background-color: #FAFAFA;
    border: 1px solid #DDDDDD; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-weight: bold; color: #999999; font-size: 0.8rem;
}
.race-box.today { border: 2px solid #333333; color: #333333; }
.race-box.completed { background-color: #333333; color: white; }

span[data-baseweb="slider"] span { color: #444444 !important; }

div.stButton > button {
    background-color: #333333; color: white;
    border-radius: 12px; border: none; font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------- 3. 유틸 ----------
def now_kst():
    return datetime.now(ZoneInfo("Asia/Seoul"))

# ---------- 4. 페이지 ----------
def home():
    st.markdown("<h1 class='main-title'>STUDY DASHBOARD</h1>", unsafe_allow_html=True)

    QUOTES = [
        "오늘의 집중이 내일의 실력이다.",
        "완벽보다 완료.",
        "지금 하는 게 제일 빠르다.",
        "공부는 배신하지 않는다."
    ]
    st.markdown(
        f"<p style='text-align:center;font-style:italic;'>“{QUOTES[date.today().toordinal() % len(QUOTES)]}”</p>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='card'><b>⏱️ 뽀모도로</b>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    f_time = c1.number_input("집중(분)", 1, 120, 25)
    b_time = c2.number_input("휴식(분)", 1, 60, 5)

    b1, b2 = st.columns(2)
    start = b1.button("시작", use_container_width=True)
    stop = b2.button("정지", use_container_width=True)

    if stop:
        st.session_state.pomodoro_stop = True
        st.session_state.pomodoro_running = False

    if start and not st.session_state.pomodoro_running:
        st.session_state.pomodoro_running = True
        st.session_state.pomodoro_stop = False
        ph = st.empty()

        for i in range(f_time * 60, -1, -1):
            if st.session_state.pomodoro_stop: break
            m, s = divmod(i, 60)
            ph.markdown(f"<h2 style='text-align:center;'>FOCUS<br>{m:02d}:{s:02d}</h2>", unsafe_allow_html=True)
            time.sleep(1)

        if not st.session_state.pomodoro_stop:
            for i in range(b_time * 60, -1, -1):
                if st.session_state.pomodoro_stop: break
                m, s = divmod(i, 60)
                ph.markdown(f"<h2 style='text-align:center;'>BREAK<br>{m:02d}:{s:02d}</h2>", unsafe_allow_html=True)
                time.sleep(1)
            st.balloons()

        st.session_state.pomodoro_running = False

    st.markdown("</div>", unsafe_allow_html=True)

def planner():
    st.markdown("<h1 class='main-title'>DAILY PLANNER</h1>", unsafe_allow_html=True)

    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        with st.form("plan"):
            s1, s2 = st.columns(2)
            sub = s1.text_input("과목")
            con = s2.text_input("내용")
            goal = st.slider("목표(h)", 0.5, 12.0, 1.0, 0.5)
            if st.form_submit_button("추가"):
                st.session_state.planner.append({
                    "날짜": date.today(), "과목": sub, "내용": con,
                    "목표": goal, "실제": 0.0, "완료여부": False
                })
                st.rerun()

    for i in st.session_state.planner:
        if not i["완료여부"]:
            with st.expander(f"{i['과목']} - {i['내용']}"):
                a = st.slider("실제(h)", 0.0, 12.0, i["목표"], 0.5)
                if st.button("완료"):
                    i["실제"] = a
                    i["완료여부"] = True
                    st.rerun()

def stats():
    st.markdown("<h1 class='main-title'>STATISTICS</h1>", unsafe_allow_html=True)

    today = now_kst().date()
    year, month = today.year, today.month
    _, last = calendar.monthrange(year, month)

    done = [i for i in st.session_state.planner if i["완료여부"]]
    done_dates = [i["날짜"] for i in done]

    grid = "<div class='race-container'>"
    for d in range(1, last + 1):
        cd = date(year, month, d)
        cls = "completed" if cd in done_dates else "today" if cd == today else ""
        grid += f"<div class='race-box {cls}'>{d}</div>"
    grid += "</div>"
    st.markdown(grid, unsafe_allow_html=True)

    if done:
        df = pd.DataFrame(done)
        df["날짜"] = pd.to_datetime(df["날짜"])
        st.metric("총 공부시간", f"{df['실제'].sum()}h")

        subj = df.groupby("과목")["실제"].sum().reset_index()
        st.plotly_chart(px.bar(subj, x="과목", y="실제"), use_container_width=True)

        week = df[df["날짜"] >= pd.Timestamp(today) - pd.Timedelta(days=6)]
        month_df = df[df["날짜"].dt.month == month]
        st.metric("주간", f"{week['실제'].sum()}h")
        st.metric("월간", f"{month_df['실제'].sum()}h")

# ---------- 5. 실행 ----------
if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats()

st.markdown("---")
c1, c2, c3 = st.columns(3)
if c1.button("Home"): st.session_state.page = "home"; st.rerun()
if c2.button("Planner"): st.session_state.page = "planner"; st.rerun()
if c3.button("Stats"): st.session_state.page = "stats"; st.rerun()
