#----------------------------------------------------------------------------------------------------------------------------------------------

#This file contains functions for generating different types of quiz questions using a language model (LLM). 
# The functions include:
# generate_mcq: Creates multiple-choice questions based on provided context.
# generate_true_false: Generates true/false questions based on context.
# generate_qna: Produces short answer questions from the context.
# quiz_generation: Chooses the appropriate question generation function based on user input and retrieves the context from a vector store.
# process_quiz: Parses the generated quiz text to extract and format questions and answers for display.
#----------------------------------------------------------------------------------------------------------------------------------------------

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def generate_mcq(llm, context):
    mcq_prompt = """
    Based on the following context, generate at least 5 multiple-choice question (MCQ):
    Context: {context}
    Provide the question, four options, and the correct answer in the following format:
    Question: ...
    Options: A) ..., 
    B) ..., 
    C) ..., 
    D) ...
    Correct Answer: ...
    """
    prompt = PromptTemplate(input_variables=["context"], template=mcq_prompt)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    return llm_chain.run({"context": context})

def generate_true_false(llm, context):
    tf_prompt = """

    Based on the following context, generate at least 5 true/false questions:
    Context: {context}
    Provide the questions and the correct answers (True or False) in the following format:
    Question 1: ...
    Correct Answer 1: ...
    Question 2: ...
    Correct Answer 2: ...
    ........
    """
    prompt = PromptTemplate(input_variables=["context"], template=tf_prompt)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    return llm_chain.run({"context": context})

def generate_qna(llm, context):
    qna_prompt = """
    Based on the following context, generate at least 5 short answer questions:
    Context: {context}
    Provide the questions and the correct answers in the following format:
    Question 1: ...
    Correct Answer 1: ...
    """
    prompt = PromptTemplate(input_variables=["context"], template=qna_prompt)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    return llm_chain.run({"context": context})

def quiz_generation(llm, vector_store, user_choice):
    # Fetch context from vector store (assume the query is related to the quiz topic)
    context = vector_store.similarity_search("Quiz topic", k=5)[0].page_content
    print("context:\n\n",context)
    
    # Generate quiz based on user choice and return both the question and answer
    if user_choice == "mcq":
        return generate_mcq(llm, context)
    elif user_choice == "true_false":
        return generate_true_false(llm, context)
    elif user_choice == "objective":
        return generate_qna(llm, context)

# Function to process quiz and hide answers until submission
def process_quiz(quiz,quiz_type):
    print("\nquiz::::",end='\n')
    print(quiz)
    questions = []
    answers = []
    
    # Split the response into blocks by double newlines
    blocks = quiz.strip().split("\n\n")
    
    for block in blocks:
        lines = block.strip().split("\n")
        
        # Process each line to extract questions and answers
        question_line = None
        answer_line = None
        
        if quiz_type=="mcq":
            for line in lines:
                line = line.strip()
                if line.startswith("Question") or line.startswith("**Question"):
                    question_line = line
                elif line.endswith("?"):
                    question_line= question_line+" "+ line
                    questions.append(question_line)
                elif line.startswith("**Options"):
                    pass
                
                    
                elif line.startswith("Correct Answer") or line.startswith("**Correct Answer"):
                    answer_line = line
                else:
                    question_line = line
                    questions.append(question_line)

                

                if answer_line:
                    answer_text = answer_line.split(":")[1].strip() if ":" in answer_line else answer_line

                    if answer_text.endswith(")**"):
                        answer_text = answer_text.replace(")**", "").strip()
                    answers.append(answer_text)
        else:
            for line in lines:
                line = line.strip()
                if line.startswith("Question") or line.startswith("**Question"):
                    question_line = line
                    questions.append(question_line)
                        
                elif line.startswith("Correct Answer") or line.startswith("**Correct Answer"):
                    answer_line = line
                else:
                    question_line = line
                    questions.append(question_line)

                if answer_line:
                    answer_text = answer_line.split(":")[1].strip() if ":" in answer_line else answer_line

                    if answer_text.endswith(")**"):
                        answer_text = answer_text.replace(")**", "").strip()
                    answers.append(answer_text)
  
    return questions, answers