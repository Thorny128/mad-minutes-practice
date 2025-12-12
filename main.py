import time
import trigdata
import random

loop = True
TIMER_LENGTH = 180
basic_trig_list = [trigdata.sin_degrees, trigdata.sin_radians, trigdata.cos_degrees, trigdata.cos_radians,
                   trigdata.tan_degrees, trigdata.tan_radians]
basic_plus_trig_list = basic_trig_list + [trigdata.csc_degrees, trigdata.csc_radians, trigdata.sec_degrees,
                                          trigdata.sec_radians, trigdata.cot_degrees, trigdata.cot_radians]
current_list = []
wrong_ans_list = []

print("Welcome to Mad Minutes Practice!")
print("Use the square root symbol √ or a v to indicate square roots")
print("Put negative signs at the very front of a number (e.g. -1/2, NOT 1/-2)")
choice = input(
    "Press 'b' for basic trig functions (sin/cos/tan), and press 'a' for advanced trig functions (sec/csc/cot): ")
if choice == "b":
    current_list = basic_trig_list
else:
    current_list = basic_plus_trig_list

while loop:
    input(f"Press ENTER to start a new {round(TIMER_LENGTH / 60, 2)} minute round: ")
    start_time = time.time()
    num_questions = 0
    num_correct_ans = 0
    wrong_ans_list.clear()

    while time.time() - start_time < TIMER_LENGTH:
        current_trig_dict = random.choice(current_list)
        question, answer = random.choice(list(current_trig_dict.items()))
        user_input = (input(f"What is {question}? ")
                      .lower()
                      .replace(" ", "")
                      .replace("0.5", "1/2")
                      .replace("v", "√"))
        if user_input == answer:
            num_correct_ans += 1
        elif user_input == "stop":
            break
        else:
            wrong_ans_list.append([question, user_input, answer])
        num_questions += 1

    print("\nTime's up! Here's how you did:")
    print(f"You got {num_correct_ans} out of {num_questions} correct")
    print(f"You averaged {round(180 / num_questions, 3)} seconds per problem")
    if 180 / num_questions <= 180 / 15:
        print("You could fully finish a 3-minute Mad Minutes!")
    if 180 / num_questions <= 120 / 15:
        print("You could fully finish a 2-minute Mad Minutes!")
    if not (num_questions == num_correct_ans):
        print("\nHere are the questions you solved incorrectly, and their correct answers:")
        for [question, incorrect_ans, corr_ans] in wrong_ans_list:
            print(f"{question} = {corr_ans}, but you answered {incorrect_ans}")

    print()
