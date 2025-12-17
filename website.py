import streamlit as st
import trigdata
import random
import time

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

# Setup page
st.title("⏰ Mad Minutes Practice ⏰")
st.markdown("Infinite practice questions for Mad Minutes, a weekly quiz where you must solve 15 trigonometry questions in a few minutes!")
st.markdown(":gray[Created by Alex Kuriakose, Class of '27 @ Sharon High School]")
st.divider()

@st.fragment(run_every="1000ms")
def run_timer():
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, st.session_state.timer_length - elapsed)
    st.markdown(f"### Time Remaining: {int(remaining // 60)}:{int(remaining % 60):02d}")
    if remaining <= 0:
        st.session_state.started = False
        st.rerun()

# Timer display
if st.session_state.started and st.session_state.start_time:
    run_timer()
    if st.button("Stop Early"):
        st.session_state.started = False
        st.rerun()

if not st.session_state.started and st.session_state.start_time is not None:
    st.success("Time's up!")
    st.write(f"You got {st.session_state.num_correct} out of {st.session_state.num_questions} correct")
    avg_time = 0
    if st.session_state.num_questions > 0:
        avg_time = st.session_state.timer_length / st.session_state.num_questions
        st.write(f"You averaged {round(avg_time, 3)} seconds per problem")
    if st.session_state.wrong_answers:
        st.write("### Incorrect Answers:")
        for question, user_ans, correct_ans in st.session_state.wrong_answers:
            st.write(f"{question} = {correct_ans}, but you answered {user_ans}")
    if avg_time < 12:
        st.write("You could fully finish a 3-minute Mad Minutes!")
    if avg_time < 8:
        st.write("You could fully finish a 2-minute Mad Minutes!")
    st.divider()

# Mode selection
if not st.session_state.started:
    st.write("Unlike normal Mad Minutes, you will continue getting practice questions until time is up (so that you can stress test yourself).")
    st.write()
    st.write("Use the square root symbol (√) or a 'v' to indicate square roots (e.g. v3/2)")
    st.write("Put negative signs at the very front of a number (e.g. -1/2, NOT 1/-2)")

    mode = st.radio("Select mode:", ["Basic (sin/cos/tan)", "Advanced (includes sec/csc/cot)"])
    timer_length = st.radio("Select time:", ["3 minutes", "2 minutes"])

    if st.button("Start Practice"):
        basic_trig_list = [trigdata.sin_degrees, trigdata.sin_radians, trigdata.cos_degrees,
                          trigdata.cos_radians, trigdata.tan_degrees, trigdata.tan_radians]
        advanced_trig_list = [trigdata.csc_degrees, trigdata.csc_radians, trigdata.sec_degrees,
                              trigdata.sec_radians, trigdata.cot_degrees, trigdata.cot_radians]
        if mode == "Basic (sin/cos/tan)":
            st.session_state.trig_list = basic_trig_list
        else:
            st.session_state.trig_list = basic_trig_list + advanced_trig_list

        if timer_length == "3 minutes":
            st.session_state.timer_length = 180
        else:
            st.session_state.timer_length = 120

        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.num_questions = 0
        st.session_state.num_correct = 0
        st.session_state.wrong_answers = []

        # Generate first question
        current_trig_dict = random.choice(st.session_state.trig_list)
        st.session_state.current_question, st.session_state.current_answer = random.choice(list(current_trig_dict.items()))
        st.rerun()

# Question and answer form
if st.session_state.started and st.session_state.start_time:
    if time.time() - st.session_state.start_time < st.session_state.timer_length:
        st.write(f"### What is {st.session_state.current_question}?")

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

