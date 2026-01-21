import streamlit as st
import pandas as pd
import random
import time
import calendar
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px

# ---------- 기본 설정 ----------
st.set_page_config(
    page_title="Study Dashboard",
    page_icon="☁️",
    layout="centered",
)

# ---------- 상태 ----------
if "page" not in st.session_state: st.session_state.page = "home"
if "planner" not in st.session_state: st.session_state.planner = []
if "routines" not in st.session_state: st.session_state.routines = []

if "timer_running" not in st.session_state: st.session_state.timer_running = False
if "timer_stop" not in st.session_state: st.session_state.timer_stop = False

# ---------- 스타일 ----------
st.markdown("""
<style>
.stApp { background-color: #F0F8FF; }

.card {
    background: white; padding: 1.5rem; border-radius: 20px;
    margin-bottom: 1.5rem; border: 1px solid #E6F3FF;
    box-shadow: 0 4px 15px rgba(135,206,250,0.12);
}

.main-title {
    font-size: 2.1rem; font-weight: 800; color: #5DADE2;
    text-align: center; margin-bottom: 1rem;
}

/* 버튼 */
div.stButton > button {
    background-color: #87CEFA; color: white;
    border-radius: 14px; border: none; font-weight: bold;
}
div.stButton > button:hover { background-color: #5DADE2; }

/* 슬라이더 빨간색 제거 */
div[data-testid="stSlider"] span {
    color: #5DADE2 !important;
    font-weight: 700;
}

/* 라디오 버튼 빨간색 제거 */
div[data-baseweb="radio"] input:checked + div {
    background-color: #87CEFA !important;
    border-color: #5DADE2 !important;
}

/* 달력 */
.race-container {
    display: grid; grid-template-columns: repeat(7, 1fr);
    gap: 8px; margin-top: 10px;
}
.race-box {
    aspect-ratio: 1/1; background-color: #F8F9FA;
    border: 2px solid #E6F3FF; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-weight: bold; color: #BDC3C7; font-size: 0.8rem;
}
.race-box.today {
    border-color: #5DADE2;
    background-color: #E1F5FE;
    color: #5DADE2;
}
.race-box.completed {
    background-color: #87CEFA;
    border-color: #5DADE2;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- 유틸 ----------
def now_kst():
    return datetime.now(ZoneInfo("Asia/Seoul"))

# ---------- HOME ----------
def home():
    st.markdown("<h1 class='main-title'>☁️ STUDY DASHBOARD</h1>", unsafe_allow_html=True)

    # ⏱️ 뽀모도로
    st.markdown("<div class='card'><b style='color:#5DADE2'>⏱️ 집중 타이머</b>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    focus = c1.number_input("집중(분)", 1, 120, 25)
    rest = c2.number_input("휴식(분)", 1, 60, 5)

    b1, b2 = st.columns(2)
    if b1.button("🚀 시작", use_container_width=True):
        st.session_state.timer_running = True
        st.session_state.timer_stop = False
    if b2.button("⏹️ 정지", use_container_width=True):
        st.session_state.timer_stop = True
        st.session_state.timer_running = False

    placeholder = st.empty()

    if st.session_state.timer_running:
        for i in range(focus * 60, -1, -1):
            if st.session_state.timer_stop:
                placeholder.warning("⏸️ 타이머 정지됨")
                break
            m, s = divmod(i, 60)
            placeholder.markdown(
                f"<div style='font-size:3rem;text-align:center;font-weight:800;color:#5DADE2'>{m:02d}:{s:02d}</div>",
                unsafe_allow_html=True
            )
            time.sleep(1)
    st.markdown("</div>", unsafe_allow_html=True)

    # ✨ 루틴
    st.markdown("<div class='card'><b style='color:#5DADE2'>✨ 루틴 체크</b>", unsafe_allow_html=True)
    r = st.text_input("루틴 추가")
    if st.button("추가"):
        if r: st.session_state.routines.append({"task": r, "done": False}); st.rerun()
    for i, rt in enumerate(st.session_state.routines):
        rt["done"] = st.checkbox(rt["task"], rt["done"], key=f"r_{i}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- PLANNER ----------
def planner():
    st.markdown("<h1 class='main-title'>✍️ DAILY PLANNER</h1>", unsafe_allow_html=True)

    # 계획 입력
    st.markdown("<div class='card'><b>📌 공부 계획</b>", unsafe_allow_html=True)
    with st.form("plan"):
        sub = st.text_input("과목")
        cont = st.text_input("공부 내용")
        goal = st.slider("목표 시간 (h)", 0.5, 12.0, 1.0, 0.5)
        if st.form_submit_button("계획 저장"):
            st.session_state.planner.append({
                "id": time.time(),
                "날짜": date.today(),
                "과목": sub,
                "내용": cont,
                "목표": goal,
                "실제": 0.0,
                "상태": "",
                "완료": False
            })
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 결과 입력
    st.markdown("### ⏳ 결과 입력")
    for item in st.session_state.planner:
        if not item["완료"]:
            with st.expander(f"{item['과목']} | {item['내용']}"):
                with st.form(f"finish_{item['id']}"):
                    actual = st.slider("실제 공부 시간", 0.0, 12.0, item["목표"], 0.5)
                    state = st.radio("상태", ["O", "△", "X"], horizontal=True)
                    if st.form_submit_button("기록 완료"):
                        item["실제"] = actual
                        item["상태"] = state
                        item["완료"] = True
                        st.rerun()

    # 완료 기록 + 진행률
    completed = [i for i in st.session_state.planner if i["완료"]]
    if completed:
        df = pd.DataFrame(completed)
        st.markdown("### ✅ 완료된 공부")
        for _, r in df.iterrows():
            progress = min(int((r["실제"] / r["목표"]) * 100), 100)
            st.markdown(f"""
            <div class='card'>
            <b>{r['과목']} – {r['내용']}</b><br>
            ⏱ {r['실제']}h / {r['목표']}h ({progress}%)
            </div>
            """, unsafe_allow_html=True)
            st.progress(progress / 100)

# ---------- STATS ----------
def stats():
    st.markdown("<h1 class='main-title'>📊 STATISTICS</h1>", unsafe_allow_html=True)

    today = now_kst().date()
    year, month = today.year, today.month
    _, last_day = calendar.monthrange(year, month)

    st.markdown(f"<p style='text-align:center;color:#5DADE2;font-weight:700'>오늘 날짜: {today}</p>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    race = "<div class='race-container'>"
    done_days = [i["날짜"] for i in st.session_state.planner if i["완료"]]
    for d in range(1, last_day + 1):
        cdate = date(year, month, d)
        cls = "completed" if cdate in done_days else "today" if cdate == today else ""
        race += f"<div class='race-box {cls}'>{d}</div>"
    race += "</div>"
    st.markdown(race, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 📈 통계 카드
    completed = [i for i in st.session_state.planner if i["완료"]]
    if completed:
        df = pd.DataFrame(completed)
        total_goal = df["목표"].sum()
        total_actual = df["실제"].sum()
        weekly = df[df["날짜"] >= today - timedelta(days=6)]

        c1, c2, c3 = st.columns(3)
        c1.metric("오늘 공부", f"{df[df['날짜']==today]['실제'].sum()}h")
        c2.metric("총 공부", f"{total_actual}h")
        c3.metric("주간 달성률", f"{int((total_actual/total_goal)*100)}%")

# ---------- MAIN ----------
if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats()

st.markdown("<br><br><br>")
c1, c2, c3 = st.columns(3)
if c1.button("🏠 Home", use_container_width=True): st.session_state.page = "home"; st.rerun()
if c2.button("✍️ Planner", use_container_width=True): st.session_state.page = "planner"; st.rerun()
if c3.button("📊 Stats", use_container_width=True): st.session_state.page = "stats"; st.rerun()
