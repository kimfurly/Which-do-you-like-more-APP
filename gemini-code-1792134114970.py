import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="Which Do You Like More? - Speaking Practice",
    page_icon="💬",
    layout="centered"
)

# 커스텀 CSS 스타일링
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        color: #4A90E2;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-box {
        background-color: #F0F4F8;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 2. 학생 응답 데이터 저장 파일
DATA_FILE = "student_responses.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Name", "Q1", "Q2", "Q3", "Q4"])

def save_data(name, answers):
    df = load_data()
    # 기존에 이름이 있으면 업데이트, 없으면 추가
    if name in df["Name"].values:
        df.loc[df["Name"] == name, ["Q1", "Q2", "Q3", "Q4"]] = answers
    else:
        new_row = pd.DataFrame([{"Name": name, "Q1": answers[0], "Q2": answers[1], "Q3": answers[2], "Q4": answers[3]}])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# 3. 질문 데이터 세트
QUESTIONS = [
    {
        "id": 0,
        "option_a": "face painting",
        "option_b": "playing VR games",
        "text": "Which do you like more, face painting or playing VR games?"
    },
    {
        "id": 1,
        "option_a": "tteokbokki",
        "option_b": "gimbap",
        "text": "Which do you like more, tteokbokki or gimbap?"
    },
    {
        "id": 2,
        "option_a": "T-shirt",
        "option_b": "cap",
        "text": "Which do you like more, a T-shirt or a cap?"
    },
    {
        "id": 3,
        "option_a": "red flowers",
        "option_b": "yellow flowers",
        "text": "Which do you like more, red flowers or yellow flowers?"
    }
]

# 4. 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = "start"
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "student_answers" not in st.session_state:
    st.session_state.student_answers = []
if "feedback_msg" not in st.session_state:
    st.session_state.feedback_msg = ""

# 헤더
st.markdown("<div class='main-title'>💬 Which Do You Like More?</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>English Speaking Practice & Soulmate Matcher!</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# STEP 1: 이름 입력 및 접속
# -------------------------------------------------------------
if st.session_state.step == "start":
    st.info("👋 Hello! Welcome to English Speaking Practice. What's your name?")
    name_input = st.text_input("이름을 입력하세요 (Name):", value=st.session_state.student_name)
    
    if st.button("Start Practice! 🚀", use_container_width=True):
        if name_input.strip() == "":
            st.warning("이름을 꼭 입력해주세요!")
        else:
            st.session_state.student_name = name_input.strip()
            st.session_state.step = "practice"
            st.session_state.current_q = 0
            st.session_state.student_answers = []
            st.session_state.feedback_msg = f"Hi {st.session_state.student_name}! I'm Alex. Let's practice together!"
            st.rerun()

# -------------------------------------------------------------
# STEP 2: 스피킹 연습 및 답변 검증
# -------------------------------------------------------------
elif st.session_state.step == "practice":
    q_idx = st.session_state.current_q
    q_data = QUESTIONS[q_idx]
    
    # 진행률 표시
    st.progress((q_idx + 1) / len(QUESTIONS))
    st.caption(f"Question {q_idx + 1} of {len(QUESTIONS)}")
    
    # AI 친구 메시지 및 질문
    st.markdown(f"""
    <div class='chat-box'>
        <b>🤖 Alex:</b> {st.session_state.feedback_msg}<br><br>
        <b>📢 Question {q_idx + 1}:</b> {q_data['text']}
    </div>
    """, unsafe_allow_html=True)
    
    st.write("💡 **Target Answer Form:** `I like [Option] more.`")
    
    # 학생 답안 입력 (마이크 입력 또는 텍스트 입력)
    user_speech = st.text_input("답변을 입력하거나 음성 입력을 사용하세요:", key=f"input_q_{q_idx}")
    
    if st.button("Submit Answer 🎯", use_container_width=True):
        clean_speech = user_speech.strip().lower()
        
        # 정답 검증 로직 ("I like A/B more." 완성문장 검사)
        opt_a = q_data["option_a"].lower()
        opt_b = q_data["option_b"].lower()
        
        target_a = f"i like {opt_a} more"
        target_b = f"i like {opt_b} more"
        
        # 구두점 제거 후 비교
        norm_speech = re.sub(r'[^a-z0-9\s]', '', clean_speech)
        norm_a = re.sub(r'[^a-z0-9\s]', '', target_a)
        norm_b = re.sub(r'[^a-z0-9\s]', '', target_b)
        
        if norm_speech == norm_a:
            selected_option = q_data["option_a"]
            is_correct = True
        elif norm_speech == norm_b:
            selected_option = q_data["option_b"]
            is_correct = True
        else:
            is_correct = False
            
        if is_correct:
            st.session_state.student_answers.append(selected_option)
            if q_idx + 1 < len(QUESTIONS):
                st.session_state.current_q += 1
                st.session_state.feedback_msg = "Great job! Perfect sentence! 🎉 Let me ask the next question."
                st.rerun()
            else:
                # 4문제 완료
                st.session_state.step = "finished"
                save_data(st.session_state.student_name, st.session_state.student_answers)
                st.rerun()
        else:
            # 틀렸을 때 시범 문장 출력 및 재기회
            st.error(f"❌ Almost! Remember to say the FULL sentence: 'I like [option] more.' Please try again!")

# -------------------------------------------------------------
# STEP 3: 취향 일치(Soulmate) 결과 및 참가 현황
# -------------------------------------------------------------
elif st.session_state.step == "finished":
    st.balloons()
    st.success(f"🎉 Congratulations, {st.session_state.student_name}! You completed all 4 questions!")
    
    st.subheader("📋 Your Choice Summary")
    for i, ans in enumerate(st.session_state.student_answers):
        st.write(f"- **Q{i+1}:** I like **{ans}** more.")
        
    st.markdown("---")
    st.subheader("👯 Finding Your 100% Preference Soulmate...")
    
    df = load_data()
    other_students = df[df["Name"] != st.session_state.student_name]
    
    if other_students.empty:
        st.info("You are the first student to finish! Ask your classmates to complete the test!")
    else:
        # 100% 취향 일치 학생 매칭
        my_ans = st.session_state.student_answers
        matches = []
        
        for idx, row in other_students.iterrows():
            row_ans = [row["Q1"], row["Q2"], row["Q3"], row["Q4"]]
            if row_ans == my_ans:
                matches.append(row["Name"])
                
        if matches:
            st.markdown(f"""
            <div style="background-color: #E8F5E9; padding: 20px; border-radius: 12px; border: 2px solid #4CAF50; text-align: center;">
                <h2 style="color: #2E7D32;">💖 100% Preference Soulmate Found!</h2>
                <h3 style="color: #1B5E20;">{", ".join(matches)}</h3>
                <p>You and <b>{", ".join(matches)}</b> picked the exact same answers for all 4 questions!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No 100% match found yet! Check back after more classmates finish!")

    st.markdown("---")
    st.subheader("📊 Classmates Participation List")
    st.dataframe(df[["Name"]], use_container_width=True)
    
    if st.button("Practice Again 🔄", use_container_width=True):
        st.session_state.step = "start"
        st.rerun()