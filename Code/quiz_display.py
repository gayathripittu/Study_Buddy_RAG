# ---------------------------------------------------------------------------------------------------------------
# Displays MCQ Quiz: Defines mcq_display function to present multiple-choice questions using Streamlit, collect user responses, and calculate the score based on correct answers.
# Displays True/False Quiz: Defines true_false_display function to present true/false questions, collect user responses, and calculate the score.
# Processes MCQ Questions: Defines mcq_processing function to structure a list of questions and options into a dictionary and then displays the MCQ quiz using mcq_display
# ---------------------------------------------------------------------------------------------------------------
import streamlit as st
import re

def mcq_display(mcq_dict,correct_answers):
    print("correct_answers:",correct_answers)

    st.title("Movie Quiz")
    # Loop through the dictionary and display questions with options

    responses = {}  # To store the user's answers

    user_answers = []  # To store answers in a list for evaluation

    for i, (question, options) in enumerate(mcq_dict.items()):

        st.write(question)

        # Extract options from the list and display them using radio buttons
        answer = st.radio(f"Select an answer for:", options)
        responses[question] = answer

        # Extract the user's choice 
        user_answers.append(answer) 

    # Submit button
    if st.button('Submit'):
        score = 0  # Initialize score
        st.markdown("*You selected the following answers:*.")
        # Loop through user's answers and compare them with the correct answers
        for i, (question, user_answer) in enumerate(zip(mcq_dict.keys(), user_answers)):
            correct_answer = correct_answers[i]
            # Check if the user's answer matches the correct answer
            if user_answer == correct_answer:
                score += 1
                st.write(f"Your answer for question {i} Correct answer")
            else:
                st.write(f"Your answer for question {i} is incorrect | Correct answer: {correct_answer}")

        # Display the score
        st.write(f"Your total score is: {score}/{len(mcq_dict)}")
        return

def true_false_display(tf_questions,correct_answers_tf):

    # Create a title for the quiz
    st.title("True/False Quiz")

    # Loop through the list of questions and display them
    user_tf_answers = []  # To store the user's answers

    for question in tf_questions:
        print(question)
        st.write(question)
        # Use radio buttons to let the user select True or False
        answer = st.radio(f"Select True or False:", ['True', 'False'])
        user_tf_answers.append(answer)

    # Submit button
    if st.button('Submit'):
        st.balloons()
        score = 0  # Initialize score
        st.write("You selected the following answers:")
        
        # Loop through the user's answers and compare them with the correct answers
        for i, (question, user_answer) in enumerate(zip(tf_questions, user_tf_answers)):
            correct_answer = correct_answers_tf[i]
            
            # Check if the user's answer matches the correct answer
            if user_answer == correct_answer:
                score += 1
                st.write(f"Your answer for question {i} Correct answer")
            else:
                st.write(f"Your answer for question {i} is incorrect | Correct answer: {correct_answer}")

        # Display the score
        st.write(f"Your total score is: {score}/{len(tf_questions)}")
    return

def mcq_processing(questions_list,correct_answers):
    questions_dict = {}
    current_question = 1
    options = []
    question=''

    # Iterate over the list and structure it into a dictionary
    for item in questions_list:
        if item.startswith("**Question"):
            key = f"question {current_question}:"
            if question:
                questions_dict[question] = options
            question = key+re.sub(r"\*\*Question\s\d+:\*\*", "", item)
            options = []
            current_question=current_question+1
        else:
            if "Options: " in item:
                item=item.replace("Options: ", "")
                
            options.append(item)

    if question:
        questions_dict[question] = options
    mcq_display(questions_dict,correct_answers)
    return


