import streamlit as st
import pandas as pd
import random
import time
import calendar
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px

# ---------- 1. 기본 설정 및 데이터 구조 ----------
st.set_page_config(page_title="Minimal Study Log", page_icon="📝", layout="centered")

# 세션 상태 초기화
if "page" not in st.session_state: st.session_state.page = "home"
if "planner" not in st.session_state: st.session_state.planner = []
if "wake_sleep" not in st.session_state: st.session_state.wake_sleep = {} # {date: {"wake": time, "sleep": time}}
if "timer_running" not in st.session_state: st.session_state.timer_running = False

# 오늘의 인용구 (매번 새로고침 시 변경)
quotes = [
    "성공은 매일 반복되는 작은 노력의 합산이다.",
    "끝날 때까지는 항상 불가능해 보인다.",
    "어제보다 나은 오늘을 만드는 것은 당신의 선택이다.",
    "공부할 때의 고통은 잠깐이지만, 못 배운 고통은 평생이다.",
    "할 수 있다고 믿는 사람은 결국 그렇게 된다."
]

# ---------- 2. 화이트 미니멀 커스텀 스타일 ----------
st.markdown("""
<style>
    /* 전체 배경 및 폰트 */
    .stApp { background-color: #FFFFFF; color: #333333; }
    
    /* 카드 디자인 (화이트 & 얇은 테두리) */
    .card {
        background: #FFFFFF; padding: 1.5rem; border-radius: 12px;
        margin-bottom: 1rem; border: 1px solid #EEEEEE;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    
    .title-text { font-size: 1.8rem; font-weight: 700; color: #222222; text-align: center; }

    /* [해결] 슬라이더 숫자 & 라디오 버튼 빨간색 제거 및 화이트/그레이톤 적용 */
    div[data-testid="stSliderTickBar"] span, 
    div[data-testid="stSlider"] div[data-baseweb="typography"] {
        color: #666666 !important; font-weight: 600 !important;
    }
    div[data-baseweb="slider"] > div > div { background: #F0F0F0 !important; }
    div[role="slider"] { background-color: #FFFFFF !important; border: 2px solid #DDDDDD !important; }

    /* 라디오 버튼 */
    div[data-baseweb="radio"] label div[role="presentation"] { border-color: #CCCCCC !important; }
    div[data-baseweb="radio"] label div[dir] { background-color: #444444 !important; }

    /* 달력 그리드 */
    .race-container { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
    .race-box {
        aspect-ratio: 1 / 1; background-color: #FAFAFA; border: 1px solid #EEEEEE;
        border-radius: 8px; display: flex; align-items: center; justify-content: center;
        font-weight: 500; color: #AAAAAA; font-size: 0.75rem; transition: 0.3s;
    }
    .race-box.today { border: 1.5px solid #222222; color: #222222; background-color: #FFFFFF; }
    .race-box.completed { background-color: #444444; color: #FFFFFF; border: none; }

    /* 버튼 스타일 */
    div.stButton > button {
        background-color: #FFFFFF; color: #333333; border: 1px solid #DDDDDD;
        border-radius: 8px; font-weight: 500; height: 3rem;
    }
    div.stButton > button:hover { border-color: #222222; color: #222222; background-color: #FAFAFA; }
</style>
""", unsafe_allow_html=True)

# ---------- 3. 유틸리티 함수 ----------
def now_kst(): return datetime.now(ZoneInfo("Asia/Seoul"))

# ---------- 4. 페이지 기능 ----------

def home():
    st.markdown("<h1 class='title-text'>STUDY LOG</h1>", unsafe_allow_html=True)
    
    # 인용구 카드
    st.markdown(f"<div class='card' style='text-align:center; font-style:italic;'>\"{random.choice(quotes)}\"</div>", unsafe_allow_html=True)

    # ⏱️ 뽀모도로 타이머 (자동 전환 + 정지 버튼)
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
                placeholder.markdown(f"<h2 style='text-align:center; color:#222222;'>Focus: {m:02d}:{s:02d}</h2>", unsafe_allow_html=True)
                time.sleep(1)
            
            # 자동 휴식 전환
            if st.session_state.timer_running:
                st.toast("집중 완료! 휴식을 시작합니다.")
                for i in range(b_min * 60, -1, -1):
                    if not st.session_state.timer_running: break
                    m, s = divmod(i, 60)
                    placeholder.markdown(f"<h2 style='text-align:center; color:#888888;'>Break: {m:02d}:{s:02d}</h2>", unsafe_allow_html=True)
                    time.sleep(1)
                st.balloons()
        
        if btn_col2.button("정지", use_container_width=True):
            st.session_state.timer_running = False
            st.rerun()

    # 🌅 기상/취침 버튼
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        st.subheader("🌅 Routine Log")
        today_str = str(date.today())
        if today_str not in st.session_state.wake_sleep:
            st.session_state.wake_sleep[today_str] = {"wake": None, "sleep": None}
            
        r1, r2 = st.columns(2)
        if r1.button("☀️ 지금 기상", use_container_width=True):
            st.session_state.wake_sleep[today_str]["wake"] = now_kst().strftime("%H:%M")
            st.toast("기상 시간이 등록되었습니다.")
        if r2.button("🌙 지금 취침", use_container_width=True):
            st.session_state.wake_sleep[today_str]["sleep"] = now_kst().strftime("%H:%M")
            st.toast("취침 시간이 등록되었습니다.")

def planner():
    st.markdown("<h1 class='title-text'>DAILY PLAN</h1>", unsafe_allow_html=True)
    
    # 계획 등록 (화이트 미니멀)
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        with st.form("plan_form", clear_on_submit=True):
            sub = st.text_input("과목")
            con = st.text_input("상세 내용")
            goal = st.slider("목표 시간 (h)", 0.5, 12.0, 1.0, step=0.5)
            if st.form_submit_button("계획 추가"):
                st.session_state.planner.append({
                    "id": time.time(), "날짜": date.today(), "과목": sub, "내용": con, 
                    "목표": goal, "실제": 0.0, "성취도": "미완료", "완료": False
                })
                st.rerun()

    # 결과 입력 섹션
    st.markdown("### ⏳ In Progress")
    for i in st.session_state.planner:
        if not i["완료"]:
            with st.expander(f"{i['과목']} : {i['내용']}"):
                with st.form(key=f"exec_{i['id']}"):
                    act = st.slider("실제 공부 시간 (h)", 0.0, 12.0, i['목표'], step=0.5)
                    sta = st.radio("성취도", ["완벽(O)", "보통(△)", "미흡(X)"], horizontal=True)
                    if st.form_submit_button("기록 완료"):
                        i["실제"], i["완료"] = act, True
                        i["성취도"] = "O" if "완벽" in sta else ("△" if "보통" in sta else "X")
                        st.rerun()

def stats():
    st.markdown("<h1 class='title-text'>STATISTICS</h1>", unsafe_allow_html=True)
    
    # 1. 월별 레이스 달력
    today = date.today()
    _, last_day = calendar.monthrange(today.year, today.month)
    
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        st.subheader(f"{today.month}월 리포트")
        race_html = "<div class='race-container'>"
        done_dates = [str(p["날짜"]) for p in st.session_state.planner if p["완료"]]
        
        for d in range(1, last_day + 1):
            curr_date = date(today.year, today.month, d)
            cls = "race-box"
            if str(curr_date) in done_dates: cls += " completed"
            elif curr_date == today: cls += " today"
            race_html += f"<div class='{cls}'>{d}</div>"
        race_html += "</div>"
        st.markdown(race_html, unsafe_allow_html=True)
    
    # 2. 날짜별 상세 기록 조회 (달력 클릭 대용)
    with st.expander("📅 특정 날짜 기록 확인하기"):
        search_date = st.date_input("날짜 선택", today)
        s_date_str = str(search_date)
        
        # 기상/취침
        ws = st.session_state.wake_sleep.get(s_date_str, {"wake": "-", "sleep": "-"})
        st.write(f"☀️ 기상: {ws['wake']} | 🌙 취침: {ws['sleep']}")
        
        # 스터디 플래너
        day_plans = [p for p in st.session_state.planner if p["날짜"] == search_date]
        if day_plans:
            st.table(pd.DataFrame(day_plans)[['과목', '내용', '실제', '성취도']])
        else:
            st.info("해당 날짜의 기록이 없습니다.")

    # 3. 과목별 & 기간별 통계 (평균 데이터)
    if st.session_state.planner:
        df = pd.DataFrame(st.session_state.planner)
        df_done = df[df["완료"]]
        
        st.markdown("### 📊 분석 정보")
        tab1, tab2 = st.tabs(["과목별 공부량", "기간별 평균"])
        
        with tab1:
            fig = px.pie(df_done, values='실제', names='과목', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.write(f"⏱️ 과목별 일평균 공부시간: **{round(df_done['실제'].mean(), 1)}h**")
            # 기상/취침 평균 계산 로직 (데이터가 있을 때)
            w_times = [datetime.strptime(v["wake"], "%H:%M") for v in st.session_state.wake_sleep.values() if v["wake"]]
            if w_times:
                avg_w = sum((t.hour * 60 + t.minute) for t in w_times) / len(w_times)
                st.write(f"🌅 평균 기상 시간: **{int(avg_w//60):02d}:{int(avg_w%60):02d}**")

# ---------- 5. 네비게이션 ----------
if st.session_state.page == "home": home()
elif st.session_state.page == "planner": planner()
elif st.session_state.page == "stats": stats()

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns(3)
if nav_col1.button("🏠 Home", use_container_width=True): st.session_state.page = "home"; st.rerun()
if nav_col2.button("✍️ Planner", use_container_width=True): st.session_state.page = "planner"; st.rerun()
if nav_col3.button("📊 Stats", use_container_width=True): st.session_state.page = "stats"; st.rerun()
