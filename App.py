import streamlit as st
import pandas as pd
import random
import time
import calendar
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px
import streamlit.components.v1 as components
import pickle  # [추가] 데이터 저장을 위해 필요
import os      # [추가] 파일 존재 확인을 위해 필요

# ---------- [추가] 데이터 저장/로드 유틸리티 ----------
DB_FILE = "study_data.pkl"

def save_data():
    data = {
        "planner": st.session_state.planner,
        "routines": st.session_state.routines,
        "sleep_log": st.session_state.sleep_log
    }
    with open(DB_FILE, "wb") as f:
        pickle.dump(data, f)

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            data = pickle.load(f)
            st.session_state.planner = data.get("planner", [])
            st.session_state.routines = data.get("routines", [])
            st.session_state.sleep_log = data.get("sleep_log", {})

# ---------- 1. 기본 설정 ----------
st.set_page_config(
    page_title="Study Dashboard",
    page_icon="🏠", 
    layout="centered",
)

# 상태 관리 초기화
if "page" not in st.session_state: st.session_state.page = "home"
if "planner" not in st.session_state: 
    st.session_state.planner = []
    load_data() # [추가] 앱 시작 시 데이터 불러오기

if "routines" not in st.session_state: st.session_state.routines = []
if "sleep_log" not in st.session_state: st.session_state.sleep_log = {}
if "timer_running" not in st.session_state: st.session_state.timer_running = False

# 인용구 리스트 및 로직 (동일)
quotes = [
    "오늘의 노력이 내일의 나를 만든다.",
    "끝날 때까지 끝난 게 아니다.",
    "공부할 때의 고통은 잠깐이지만, 못 배운 고통은 평생이다.",
    "성공은 매일 반복되는 작은 노력의 합계이다.",
    "할 수 있다고 믿는 사람은 결국 그렇게 된다."
]
if "quote_date" not in st.session_state or st.session_state.quote_date != date.today():
    st.session_state.quote_date = date.today()
    st.session_state.daily_quote = random.choice(quotes)

# ---------- 2. 커스텀 스타일 (동일) ----------
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .card {
        background: #FFFFFF; padding: 1.5rem; border-radius: 15px;
        margin-bottom: 1.5rem; border: 1px solid #F0F0F0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .main-title {
        font-size: 2rem; font-weight: 800; color: #333333;
        text-align: center; margin-bottom: 0.5rem;
    }
    .quote-box {
        text-align: center; font-style: italic; color: #888888; margin-bottom: 2rem;
    }
    .race-container {
        display: grid; grid-template-columns: repeat(7, 1fr);
        gap: 8px; margin-top: 10px;
    }
    .race-box {
        aspect-ratio: 1 / 1; background-color: #FFFFFF;
        border: 1px solid #EEEEEE; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 500; color: #BBBBBB; font-size: 0.8rem;
    }
    .race-box.today { border: 2px solid #333333; color: #333333; }
    .race-box.completed { background-color: #333333; border-color: #333333; color: white; }
    div[data-testid="stSliderTickBar"] span, span[data-baseweb="typography"] { color: #333333 !important; }
    div[role="slider"] { background-color: #333333 !important; border: 2px solid #333333 !important; }
    .st-ae { color: #333333 !important; }
    div.stButton > button {
        background-color: #333333; color: white;
        border-radius: 8px; border: none; font-weight: 600;
    }
    div.stButton > button:hover { background-color: #000000; border: none; color: white; }
</style>
""", unsafe_allow_html=True)

def now_kst(): return datetime.now(ZoneInfo("Asia/Seoul"))

# ---------- 4. 페이지 함수 ----------

def home():
    st.markdown("<h1 class='main-title'>STUDY DASHBOARD</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='quote-box'>\"{st.session_state.daily_quote}\"</div>", unsafe_allow_html=True)
    
    # 타이머 섹션
    st.markdown("<div class='card'><div style='font-weight:700; margin-bottom:10px;'>⏱️ FOCUS TIMER</div>", unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    f_time = tc1.number_input("집중(분)", 1, 120, 25)
    b_time = tc2.number_input("휴식(분)", 1, 60, 5)
    col_start, col_stop = st.columns(2)
    if col_start.button("🚀 START", use_container_width=True):
        st.session_state.timer_running = True
        st.rerun()
    if col_stop.button("⏹️ STOP", use_container_width=True):
        st.session_state.timer_running = False
        st.rerun()

    if st.session_state.timer_running:
        placeholder = st.empty()
        completed_focus = False
        for i in range(f_time * 60, -1, -1):
            if not st.session_state.timer_running: break
            m, s = divmod(i, 60)
            placeholder.markdown(f"<div style='font-size:3rem; text-align:center; padding:20px; color:#333333; font-weight:800;'>FOCUS<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            if i == 0: completed_focus = True
        if completed_focus and st.session_state.timer_running:
            st.balloons() 
            components.html("<audio autoplay><source src='https://actions.google.com/sounds/v1/alarms/beep_short.ogg' type='audio/ogg'></audio>", height=0)
            time.sleep(1)
            for i in range(b_time * 60, -1, -1):
                if not st.session_state.timer_running: break
                m, s = divmod(i, 60)
                placeholder.markdown(f"<div style='font-size:3rem; text-align:center; padding:20px; color:#2ECC71; font-weight:800;'>BREAK<br>{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
                time.sleep(1)
            st.session_state.timer_running = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 수면 로그
    st.markdown("<div class='card'><div style='font-weight:700; margin-bottom:10px;'>🛌 WAKE UP / SLEEP LOG</div>", unsafe_allow_html=True)
    t_col1, t_col2 = st.columns(2)
    today_str = str(date.today())
    if today_str not in st.session_state.sleep_log:
        st.session_state.sleep_log[today_str] = {"wake": None, "sleep": None}
    if t_col1.button("☀️ 지금 기상", use_container_width=True):
        st.session_state.sleep_log[today_str]["wake"] = now_kst().strftime("%H:%M")
        save_data() # 저장
        st.rerun()
    if t_col2.button("🌙 지금 취침", use_container_width=True):
        st.session_state.sleep_log[today_str]["sleep"] = now_kst().strftime("%H:%M")
        save_data() # 저장
        st.rerun()
    wake_t = st.session_state.sleep_log[today_str]["wake"] or "--:--"
    sleep_t = st.session_state.sleep_log[today_str]["sleep"] or "--:--"
    st.markdown(f"<p style='text-align:center; margin-top:10px; font-size:1.1rem;'>기상: <b>{wake_t}</b> | 취침: <b>{sleep_t}</b></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 루틴
    st.markdown("<div class='card'><div style='font-weight:700; margin-bottom:10px;'>✨ ROUTINE</div>", unsafe_allow_html=True)
    r_input = st.text_input("루틴 추가", label_visibility="collapsed", placeholder="새로운 루틴 입력...")
    if st.button("추가"):
        if r_input: 
            st.session_state.routines.append({"task": r_input, "done": False})
            save_data() # 저장
            st.rerun()
    for idx, item in enumerate(st.session_state.routines):
        prev_done = item['done']
        item['done'] = st.checkbox(item['task'], value=item['done'], key=f"r_{idx}")
        if prev_done != item['done']: # 상태 변경 시 저장
            save_data()
    st.markdown("</div>", unsafe_allow_html=True)

def planner():
    st.markdown("<h1 class='main-title'>DAILY PLANNER</h1>")
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        with st.form("plan_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            sub = c1.text_input("과목명")
            con = c2.text_input("공부 내용")
            goal = st.slider("목표 시간 (h)", 0.5, 12.0, 1.0, step=0.5)
            if st.form_submit_button("계획 확정 📌"):
                st.session_state.planner.append({
                    "id": time.time(), "날짜": date.today(), "등록시간": now_kst().strftime("%H:%M"),
                    "과목": sub, "내용": con, "목표": goal, "실제": 0.0, "성취도": "미완료", "완료여부": False
                })
                save_data() # 저장
                st.rerun()
    
    for idx, item in enumerate(st.session_state.planner):
        if not item["완료여부"]:
            with st.expander(f"📍 {item['과목']} : {item['내용']}"):
                with st.form(key=f"finish_{item['id']}"):
                    actual = st.slider("실제 시간", 0.0, 12.0, item['목표'], step=0.5)
                    status = st.radio("성취도", ["완벽(O)", "보통(△)", "미흡(X)"], horizontal=True)
                    f1, f2 = st.columns(2)
                    if f1.form_submit_button("완료 ✅"):
                        item["실제"] = actual
                        item["성취도"] = "O" if "완벽" in status else ("△" if "보통" in status else "X")
                        item["완료여부"] = True
                        save_data(); st.rerun()
                    if f2.form_submit_button("삭제 🗑️"):
                        st.session_state.planner.pop(idx)
                        save_data(); st.rerun()
    # (완료 목록 생략 - 동일)
    if any(i["완료여부"] for i in st.session_state.planner):
        df_comp = pd.DataFrame([i for i in st.session_state.planner if i["완료여부"]])
        st.dataframe(df_comp[['과목', '내용', '목표', '실제', '성취도']], use_container_width=True, hide_index=True)

def stats():
    # 통계 코드는 데이터 변경이 없으므로 원본 유지
    st.markdown("<h1 class='main-title'>STATISTICS</h1>")
    today = now_kst().date()
    year, month = today.year, today.month
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    done_dates = [i["날짜"] for i in st.session_state.planner if i["완료여부"]]
    selected_day = st.number_input("날짜 선택", 1, calendar.monthrange(year, month)[1], today.day)
    selected_date = date(year, month, selected_day)
    race_html = "<div class='race-container'>"
    for d in range(1, calendar.monthrange(year, month)[1] + 1):
        curr = date(year, month, d)
        cls = "completed" if curr in done_dates else ("today" if curr == today else "")
        race_html += f"<div class='race-box {cls}'>{d}</div>"
    st.markdown(race_html + "</div>", unsafe_allow_html=True)
    # (나머지 시각화 코드 동일...)
    completed = [i for i in st.session_state.planner if i["완료여부"]]
    if completed:
        df = pd.DataFrame(completed)
        fig = px.pie(df, values='실제', names='과목', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

# ---------- 5. 메인 실행 및 하단 네비게이션 ----------
if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats()

st.markdown("<br><br><br><br>---", unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns(3)
if nav_col1.button("🏠 Home", use_container_width=True): st.session_state.page = "home"; st.rerun()
if nav_col2.button("✍️ Planner", use_container_width=True): st.session_state.page = "planner"; st.rerun()
if nav_col3.button("📊 Stats", use_container_width=True): st.session_state.page = "stats"; st.rerun()
