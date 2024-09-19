#----------------------------------------------------
# Author: Gayathri Pittu
#
# This script sets up a Streamlit web application that allows users to:
# 1. Upload PDF documents and process them for further querying or quiz generation.
# 2. Ask questions about the content of the uploaded PDFs.
# 3. Take quizzes based on the content of the PDFs, with options for different quiz types.
#-----------------------------------------------------

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from utils import extract_text_from_pdf, text_split, create_embeddings
from Q_A import qa_process
from quiz1 import quiz_generation, process_quiz
from quiz_display import true_false_display, mcq_processing

# Title and Sidebar
st.sidebar.title("About Us 💡")
st.sidebar.write("""
**Welcome to Study Buddy!** 🎓  
Your smart study partner for all things PDF.  

- 📑 **Create quizzes from any PDF**  
- 💬 **Ask questions & get instant answers**  
- 🚀 **Master your documents with ease!**

Let's dive into your documents and start mastering them!
""")

# Apply custom styling to the Streamlit app
st.markdown(
    """
    <style>
    /* Main container styling */
    .stApp {
        font-family: 'Arial', sans-serif;
        color: #333;
    }

    /* Style for heading */
    .title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #2e3a59;
    }

    /* Style for subheading */
    .subtitle {
        font-size: 16px;
        text-align: center;
        color: #5a6270;
        margin-bottom: 30px;
    }
    .description {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main heading
st.markdown("<div class='title'>Welcome to Studybuddy!</div>", unsafe_allow_html=True)

# Subheading
st.markdown("<div class='subtitle'>Your personal learning assistant</div>", unsafe_allow_html=True)

# Sidebar menu options for user interaction
option = st.sidebar.selectbox(
    "What would you like to do?",
    ["Upload Your Document", "Summarize & Ask Questions", "Take a Quiz"]
)

def document_process(uploaded_file):
    """
    Process the uploaded PDF document by extracting text, splitting it into chunks, 
    and creating embeddings for further querying or quiz generation.

    Args:
        uploaded_file (UploadedFile): The uploaded PDF file.

    Returns:
        vectorstore: The vectorstore created from the document chunks.
    """
    if uploaded_file is not None:
        # Extract text from the PDF
        document_text = extract_text_from_pdf(uploaded_file)
        # Split the text into manageable chunks
        chunks = text_split(document_text)

        st.write(f"Your {uploaded_file.name} is processing! Please wait some time")

        # Create embeddings for the chunks
        vectorstore = create_embeddings(chunks, uploaded_file.name, uploaded_file)

        st.write("➡️ Head over to the Q&A tab to start asking questions")
        return vectorstore

# Initialize session state variables if they do not exist
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hello, how can I help you?"}]

# Handle the "Upload Your Document" option
if option == "Upload Your Document":
    st.subheader("Upload PDF 📄")
    st.write("Upload it here, and we’ll quiz you in seconds or answer your questions! 🤔📚")
    uploaded_file = st.file_uploader("", type="pdf")
    if uploaded_file:
        # Process the uploaded document
        st.session_state.uploaded_file = uploaded_file
        st.session_state.vectorstore = document_process(uploaded_file)
    else:
        st.write("No file uploaded yet.")

# Handle the "Summarize & Ask Questions" option
elif option == "Summarize & Ask Questions":
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Ensure a document is uploaded and processed
    if st.session_state.uploaded_file and st.session_state.vectorstore:
        query = st.chat_input("Please enter your query here.....")

        if query:
            # Add the user query to chat history
            st.session_state.chat_history.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)

            # Get the answer to the query
            response = qa_process(st.session_state.vectorstore, query)

            # Add the assistant's response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})

            with st.chat_message("assistant"):
                st.write(response)

    else:
        st.write("Please upload your document for querying.")

# Handle the "Take a Quiz" option
elif option == "Take a Quiz":
    st.markdown(
        """
        <div class='description'>
        Ready to test your knowledge? 🤔 
        Just pick a quiz, and let's get started! 🚀
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            border-radius: 5px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stSelectbox, .stRadio, .stTextInput {
            background-color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    if st.session_state.uploaded_file:
        if st.session_state.vectorstore:
            quiz_type = st.selectbox("Select the type of quiz:", ["objective", "mcq", "true_false"])
            if quiz_type:
                vectorstore = st.session_state.vectorstore
                llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)

                if "submitted" not in st.session_state:
                    st.session_state.submitted = False

                if "user_answers" not in st.session_state:
                    st.session_state.user_answers = []

                if "questions" not in st.session_state:
                    st.session_state.questions = []
                    st.session_state.correct_answers = []

                if st.button("Generate Quiz"):
                    # Generate quiz based on selected type
                    quiz = quiz_generation(llm, vectorstore, quiz_type)
                    if quiz:
                        questions, correct_answers = process_quiz(quiz, quiz_type)
                        print("questions:", end='\n\n')
                        print(questions)

                        # Store the questions and answers in session state
                        st.session_state.questions = questions
                        st.session_state.correct_answers = correct_answers
                        st.session_state.submitted = False  # Reset submission state
                        st.session_state.user_answers = [""] * len(questions)  # Reset user answers

                if not st.session_state.submitted:
                    # Display questions and collect user answers
                    if st.session_state.questions:
                        print(" Display questions and take user input")
                        
                        if quiz_type == 'mcq':
                            mcq_processing(st.session_state.questions, st.session_state.correct_answers)

                        elif quiz_type == 'true_false':
                            true_false_display(st.session_state.questions, st.session_state.correct_answers)

            else:
                st.write("Please select a quiz type.")
        else:
            st.write("Error processing the document.")
    else:
        st.write("Please upload your document to create a quiz.")
