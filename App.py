import streamlit as st
import pandas as pd
import random
import time
import calendar
from datetime import date, datetime
from zoneinfo import ZoneInfo
import plotly.express as px

# ---------- 1. 기본 설정 ----------
st.set_page_config(page_title="Minimal Study Log", page_icon="📝", layout="centered")

# 세션 상태 초기화 (데이터 구조 유지)
if "page" not in st.session_state: st.session_state.page = "home"
if "planner" not in st.session_state: st.session_state.planner = []
if "wake_sleep" not in st.session_state: st.session_state.wake_sleep = {} 
if "timer_running" not in st.session_state: st.session_state.timer_running = False

# 오늘의 인용구
quotes = ["성공은 매일 반복되는 작은 노력의 합산이다.", "끝날 때까지는 항상 불가능해 보인다.", "어제보다 나은 오늘을 만드는 것은 당신의 선택이다."]

# ---------- 2. 강력한 커스텀 스타일 (빨간색 제거 & 네비게이션 고정) ----------
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .card {
        background: #FFFFFF; padding: 1.5rem; border-radius: 12px;
        margin-bottom: 1rem; border: 1px solid #EEEEEE;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .title-text { font-size: 1.8rem; font-weight: 700; color: #222222; text-align: center; }

    /* 슬라이더 빨간 숫자 및 색상 강제 변경 */
    div[data-testid="stSliderTickBar"] span, 
    div[data-testid="stSlider"] div[data-baseweb="typography"] {
        color: #5DADE2 !important; /* 하늘색으로 변경 */
    }
    div[data-baseweb="slider"] > div > div { background: #E1F5FE !important; }
    div[role="slider"] { background-color: #FFFFFF !important; border: 2px solid #5DADE2 !important; }

    /* 라디오 버튼 빨간색 제거 */
    div[data-baseweb="radio"] label div[role="presentation"] { border-color: #5DADE2 !important; }
    div[data-baseweb="radio"] label div[dir] { background-color: #5DADE2 !important; }

    /* 달력 그리드 */
    .race-container { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
    .race-box {
        aspect-ratio: 1 / 1; background-color: #FAFAFA; border: 1px solid #EEEEEE;
        border-radius: 8px; display: flex; align-items: center; justify-content: center;
        font-weight: 500; color: #AAAAAA; font-size: 0.75rem;
    }
    .race-box.today { border: 2px solid #5DADE2; color: #5DADE2; }
    .race-box.completed { background-color: #5DADE2; color: #FFFFFF; border: none; }

    /* 하단 네비게이션 바 스타일 */
    .nav-container {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: white; border-top: 1px solid #EEEEEE;
        padding: 10px 0; z-index: 100;
    }
</style>
""", unsafe_allow_html=True)

def now_kst(): return datetime.now(ZoneInfo("Asia/Seoul"))

# ---------- 3. 페이지 함수 ----------

def home():
    st.markdown("<h1 class='title-text'>STUDY LOG</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='card' style='text-align:center;'>\"{random.choice(quotes)}\"</div>", unsafe_allow_html=True)

    # ⏱️ 뽀모도로 타이머
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        st.subheader("⏱️ Pomodoro")
        c1, c2 = st.columns(2)
        f_min = c1.number_input("집중(분)", 1, 120, 25)
        b_min = c2.number_input("휴식(분)", 1, 60, 5)
        
        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("시작", use_container_width=True):
            st.session_state.timer_running = True
            placeholder = st.empty()
            # 집중 시간
            for i in range(f_min * 60, -1, -1):
                if not st.session_state.timer_running: break
                m, s = divmod(i, 60)
                placeholder.markdown(f"<h2 style='text-align:center;'>Focus: {m:02d}:{s:02d}</h2>", unsafe_allow_html=True)
                time.sleep(1)
            # 휴식 전환
            if st.session_state.timer_running:
                for i in range(b_min * 60, -1, -1):
                    if not st.session_state.timer_running: break
                    m, s = divmod(i, 60)
                    placeholder.markdown(f"<h2 style='text-align:center; color:#48C9B0;'>Break: {m:02d}:{s:02d}</h2>", unsafe_allow_html=True)
                    time.sleep(1)
        if btn_col2.button("정지", use_container_width=True):
            st.session_state.timer_running = False
            st.rerun()

    # 🌅 기상/취침 루틴
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        st.subheader("🌅 Routine")
        today_str = str(date.today())
        if today_str not in st.session_state.wake_sleep:
            st.session_state.wake_sleep[today_str] = {"wake": "-", "sleep": "-"}
        r1, r2 = st.columns(2)
        if r1.button("☀️ 지금 기상", use_container_width=True):
            st.session_state.wake_sleep[today_str]["wake"] = now_kst().strftime("%H:%M")
            st.rerun()
        if r2.button("🌙 지금 취침", use_container_width=True):
            st.session_state.wake_sleep[today_str]["sleep"] = now_kst().strftime("%H:%M")
            st.rerun()

def planner():
    st.markdown("<h1 class='title-text'>DAILY PLANNER</h1>", unsafe_allow_html=True)
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        with st.form("plan_form", clear_on_submit=True):
            sub = st.text_input("과목")
            con = st.text_input("공부 내용")
            goal = st.slider("목표 시간 (h)", 0.5, 12.0, 1.0, step=0.5)
            if st.form_submit_button("계획 추가 📌"):
                st.session_state.planner.append({
                    "id": time.time(), "날짜": date.today(), "과목": sub, "내용": con, 
                    "목표": goal, "실제": 0.0, "성취도": "미완료", "완료": False
                })
                st.rerun()

    st.markdown("### ⏳ 진행 중인 공부")
    for i in st.session_state.planner:
        if not i.get("완료", False):
            with st.expander(f"{i['과목']} (목표: {i['목표']}h)"):
                with st.form(key=f"exec_{i['id']}"):
                    act = st.slider("실제 공부 시간 (h)", 0.0, 12.0, i['목표'], step=0.5)
                    sta = st.radio("성취도", ["완벽(O)", "보통(△)", "미흡(X)"], horizontal=True)
                    if st.form_submit_button("완료 기록 ✅"):
                        i["실제"] = act
                        i["완료"] = True
                        i["성취도"] = "O" if "완벽" in sta else ("△" if "보통" in sta else "X")
                        st.rerun()

def stats():
    st.markdown("<h1 class='title-text'>STATISTICS</h1>", unsafe_allow_html=True)
    today = date.today()
    _, last_day = calendar.monthrange(today.year, today.month)
    
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        st.subheader(f"{today.month}월 리포트")
        race_html = "<div class='race-container'>"
        # KeyError 방지를 위해 get() 사용
        done_dates = [str(p.get("날짜")) for p in st.session_state.planner if p.get("완료")]
        for d in range(1, last_day + 1):
            curr_date = date(today.year, today.month, d)
            cls = "race-box"
            if str(curr_date) in done_dates: cls += " completed"
            elif curr_date == today: cls += " today"
            race_html += f"<div class='{cls}'>{d}</div>"
        race_html += "</div>"
        st.markdown(race_html, unsafe_allow_html=True)

    # 상세 조회 (기상/취침 및 공부 내용)
    with st.expander("📅 날짜별 상세 기록"):
        s_date = st.date_input("조회할 날짜", today)
        ws = st.session_state.wake_sleep.get(str(s_date), {"wake": "-", "sleep": "-"})
        st.write(f"**기상:** {ws['wake']} | **취침:** {ws['sleep']}")
        day_plans = [p for p in st.session_state.planner if p.get("날짜") == s_date and p.get("완료")]
        if day_plans: st.table(pd.DataFrame(day_plans)[['과목', '내용', '실제', '성취도']])

    if st.session_state.planner:
        df = pd.DataFrame(st.session_state.planner)
        df_done = df[df.get("완료", False) == True]
        if not df_done.empty:
            st.markdown("### 📊 과목별 공부 비중")
            fig = px.pie(df_done, values='실제', names='과목', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

# ---------- 4. 메인 렌더링 및 네비게이션 ----------

if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats()

# 하단 네비게이션 바 (공간 확보 후 렌더링)
st.markdown("<br><br><br>", unsafe_allow_html=True)
nav1, nav2, nav3 = st.columns(3)
if nav1.button("🏠 Home", use_container_width=True):
    st.session_state.page = "home"
    st.rerun()
if nav2.button("✍️ Planner", use_container_width=True):
    st.session_state.page = "planner"
    st.rerun()
if nav3.button("📊 Stats", use_container_width=True):
    st.session_state.page = "stats"
    st.rerun()
