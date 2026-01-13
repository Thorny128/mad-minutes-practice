import pandas as pd
import streamlit as st
import trigdata
import random
import time
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

MAD_MINUTES_SPEEDRUN_QUESTIONS = 15

# Initialize session state
if 'started' not in st.session_state:
    st.session_state.started = False
    st.session_state.start_time = None
    st.session_state.num_questions = 0
    st.session_state.num_correct = 0
    st.session_state.wrong_answers = []
    st.session_state.current_question = None
    st.session_state.current_answer = None
    st.session_state.trig_list = []
    st.session_state.timer_length = 180
    st.session_state.speedrun_mode = False
    st.session_state.speedrun_running = False
    st.session_state.final_time = 0

conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read()

with st.sidebar:
    with st.container(horizontal=True):
        st.write("### Leaderboard")
        if st.button("Refresh Leaderboard"):
            st.session_state.df = conn.read(ttl=0)
            st.rerun()
    st.dataframe(st.session_state.df)


# Setup page
st.title("⏰ Mad Minutes Practice ⏰")
st.markdown("Infinite practice questions for Mad Minutes, a weekly quiz where you must solve 15 trigonometry questions in a few minutes!")
st.write("Unlike normal Mad Minutes, you will continue getting practice questions until time is up.")
st.markdown(":gray[Created by Alex Kuriakose, Class of '27 @ Sharon High School]")
st.divider()

APP_VERSION = "v1.3"

st.markdown(
    f"""
    <style>
    .version-text {{
        position: fixed;
        top: 60px;
        right: 20px;
        font-size: 0.9rem;
        color: #888;
        z-index: 9999;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 5px 10px;
        border-radius: 5px;
    }}
    </style>
    <div class="version-text">
        {APP_VERSION}
    </div>
    """,
    unsafe_allow_html=True
)

@st.fragment(run_every="1000ms")
def run_timer():
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, st.session_state.timer_length - elapsed)
    st.markdown(f"### Time Remaining: {int(remaining // 60)}:{int(remaining % 60):02d}")
    if remaining <= 0:
        st.session_state.started = False
        st.rerun()

@st.fragment(run_every="1000ms")
def run_stopwatch():
    elapsed = time.time() - st.session_state.start_time
    st.markdown(f"### Time Remaining: {int(elapsed // 60)}:{int(elapsed % 60):02d}")

# Timer display for practice mode
if st.session_state.started and st.session_state.start_time and not st.session_state.speedrun_mode:
    run_timer()
    if st.button("Stop Early"):
        st.session_state.started = False
        st.rerun()

# Stopwatch display for Mad Minutes Speedrun mode
if st.session_state.started and st.session_state.start_time and st.session_state.speedrun_mode:
    run_stopwatch()
    if st.button("End Speedrun"):
        st.session_state.started = False
        st.session_state.speedrun_running = False
        st.rerun()


@st.dialog("Enter Username")
def submit_score(user_time):
    st.write("If a username already exists in the database, it will be overridden with your current time")
    name = st.text_input("Enter Username Here")
    if st.button("Submit"):
        # Check if username already exists
        existing_df = st.session_state.df.copy()
        if name in existing_df['Username'].values:
            # Update existing entry
            existing_df.loc[existing_df['Username'] == name, 'Time to finish Mad Minutes'] = user_time
            existing_df.loc[existing_df['Username'] == name, 'Date'] = datetime.now().strftime("%m/%d/%Y")
            updated_df = existing_df
        else:
            # Add new entry
            new_row = pd.DataFrame({
                "Username": [name],
                "Time to finish Mad Minutes": [user_time],
                "Date": [datetime.now().strftime("%m/%d/%Y")]
            })
            updated_df = pd.concat([st.session_state.df, new_row], ignore_index=True)

        conn.update(worksheet="Leaderboard", data=updated_df)
        st.session_state.df = updated_df
        st.success("Score submitted!")
        st.session_state.speedrun_mode = False
        st.session_state.started = False
        st.session_state.start_time = None
        st.rerun()

# Results Section
if not st.session_state.started and st.session_state.start_time is not None:
    if st.session_state.speedrun_mode:
        # Speedrun results
        if st.session_state.num_questions < MAD_MINUTES_SPEEDRUN_QUESTIONS:
            st.write("#### The speedrun has ended. You either got a question wrong or ended the speedrun prematurely.")
            st.session_state.speedrun_mode = False
            st.session_state.started = False
            st.session_state.start_time = None
        else:
            if st.session_state.final_time == 0:
                st.session_state.final_time = round(time.time() - st.session_state.start_time, 3)
            st.write("## Congratulations for finishing the speedrun!")
            st.write(f"You finished Mad Minutes in {st.session_state.final_time} seconds!")
            if st.button("Save Score to Leaderboard"):
                submit_score(st.session_state.final_time)
    else:
        # Practice mode results
        st.success("Time's up!")
        st.write("### Results")
        st.write(f"You got {st.session_state.num_correct} out of {st.session_state.num_questions} problems correct")
        avg_time = 0
        if st.session_state.num_questions > 0:
            avg_time = (time.time() - st.session_state.start_time) / st.session_state.num_questions
            st.write(f"You averaged {round(avg_time, 3)} seconds per problem")
        if avg_time <= 12:
            st.write("You could fully finish a 3-minute Mad Minutes!")
        else:
            st.write("You would not be able to fully finish a 3-minute Mad Minutes.")
        if avg_time <= 8:
            st.write("You could fully finish a 2-minute Mad Minutes!")
        else:
            st.write("You would not be able to fully finish a 2-minute Mad Minutes.")

        if st.session_state.wrong_answers:
            st.write("### Incorrect Answers:")
            for question, user_ans, correct_ans in st.session_state.wrong_answers:
                st.write(f"{question} = {correct_ans}, but you answered '{user_ans}'")

    st.divider()

# Mode Selection
if not st.session_state.started:
    st.write("## New Game")
    st.subheader("Formatting Tips")
    st.markdown("""
     * Use the letter 'v' to indicate square roots (e.g. v3/2)
     * Use 'undefined' for undefined values
     * Put negative signs at the very front of a number (e.g. -1/2, NOT 1/-2)
     """)

    st.subheader("Options")
    with st.container(horizontal=True):
        mode = st.radio("Select mode:", ["Basic (sin/cos/tan)", "Advanced (includes sec/csc/cot)"])
        timer_length = st.radio("Select time:", ["3 minutes", "2 minutes"])

    basic_trig_list = [trigdata.sin_degrees, trigdata.sin_radians, trigdata.cos_degrees,
                       trigdata.cos_radians, trigdata.tan_degrees, trigdata.tan_radians]
    advanced_trig_list = [trigdata.csc_degrees, trigdata.csc_radians, trigdata.sec_degrees,
                          trigdata.sec_radians, trigdata.cot_degrees, trigdata.cot_radians]
    if st.button("Start Practice"):
        if mode == "Basic (sin/cos/tan)":
            st.session_state.trig_list = basic_trig_list
        else:
            st.session_state.trig_list = basic_trig_list + advanced_trig_list

        if timer_length == "3 minutes":
            st.session_state.timer_length = 180
        else:
            st.session_state.timer_length = 3

        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.num_questions = 0
        st.session_state.num_correct = 0
        st.session_state.wrong_answers = []

        # Generate first question
        current_trig_dict = random.choice(st.session_state.trig_list)
        st.session_state.current_question, st.session_state.current_answer = random.choice(list(current_trig_dict.items()))
        st.rerun()
    with st.container(horizontal=True):
        if st.button("Mad Minutes Speedrun"):
            st.session_state.trig_list = basic_trig_list + advanced_trig_list
            st.session_state.speedrun_mode = True
            st.session_state.started = True
            st.session_state.start_time = time.time()
            st.session_state.num_questions = 0
            st.session_state.num_correct = 0
            st.session_state.wrong_answers = []
            st.session_state.final_time = 0
            current_trig_dict = random.choice(st.session_state.trig_list)
            st.session_state.current_question, st.session_state.current_answer = random.choice(
                list(current_trig_dict.items()))
            st.rerun()
        if st.button("What is Speedrun Mode?"):
            st.markdown("In Mad Minutes Speedrun mode, you must correctly answer 15 Mad Minutes questions (covering sin/cos/tan/sec/csc/cot from 0-360º) as quickly as possible—if you get even one question wrong, the speedrun immediately ends. If you achieve a perfect score, you can save your completion time and username to the leaderboard, which either adds a new entry or replaces your existing time if your username is already registered.")

# Main loop for Mad Minutes Speedrun mode
if st.session_state.speedrun_mode and st.session_state.started:
    if st.session_state.num_questions < MAD_MINUTES_SPEEDRUN_QUESTIONS:
        st.write(f"### {st.session_state.num_questions}/15 Questions Answered")
        st.write(f"### What is {st.session_state.current_question}?")
        st.markdown("""
        * Use the letter 'v' to indicate square roots (e.g. v3/2)
        * Use 'undefined' for undefined values
        """)
        with st.form(key='answer_form', clear_on_submit=True):
            user_answer = st.text_input("Your answer:", key=f"input_{st.session_state.num_questions}")
            submit = st.form_submit_button("Submit")

            if submit and user_answer:
                processed_answer = (user_answer.lower()
                                    .replace(" ", "")
                                    .replace("0.5", "1/2")
                                    .replace("v", "√"))

                st.session_state.num_questions += 1

                if processed_answer == st.session_state.current_answer:
                    st.session_state.num_correct += 1
                else:
                    st.session_state.started = False
                    st.session_state.speedrun_running = False

                if st.session_state.num_questions < MAD_MINUTES_SPEEDRUN_QUESTIONS:  # Only generate next question if not done
                    current_trig_dict = random.choice(st.session_state.trig_list)
                    st.session_state.current_question, st.session_state.current_answer = random.choice(
                        list(current_trig_dict.items()))
                else:
                    st.session_state.started = False
                st.rerun()

# Main loop for Practice Mode
if st.session_state.started and st.session_state.start_time and not st.session_state.speedrun_mode:
    if time.time() - st.session_state.start_time < st.session_state.timer_length:
        if st.session_state.num_questions == 1:
            st.write(f"### {st.session_state.num_questions} Question Answered")
        else:
            st.write(f"### {st.session_state.num_questions} Questions Answered")
        st.write(f"### What is {st.session_state.current_question}?")
        st.markdown("""
        * Use the letter 'v' to indicate square roots (e.g. v3/2)
        * Use 'undefined' for undefined values
        """)

        with st.form(key='answer_form', clear_on_submit=True):
            user_answer = st.text_input("Your answer:", key=f"input_{st.session_state.num_questions}")
            submit = st.form_submit_button("Submit")

            if submit and user_answer:
                # Process answer
                processed_answer = (user_answer.lower()
                                  .replace(" ", "")
                                  .replace("0.5", "1/2")
                                  .replace("v", "√"))

                st.session_state.num_questions += 1

                if processed_answer == st.session_state.current_answer:
                    st.session_state.num_correct += 1
                else:
                    st.session_state.wrong_answers.append([
                        st.session_state.current_question,
                        processed_answer,
                        st.session_state.current_answer
                    ])

                # Generate next question
                current_trig_dict = random.choice(st.session_state.trig_list)
                st.session_state.current_question, st.session_state.current_answer = random.choice(list(current_trig_dict.items()))
                st.rerun()
