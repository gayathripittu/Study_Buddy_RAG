# Study_Buddy_RAG

**Study Buddy** is a smart study assistant application built with Streamlit. It allows users to upload PDF documents, generate quizzes, and get answers to questions based on the content of the PDFs. The application supports multiple-choice and true/false quizzes and integrates with Google Generative AI for enhanced question-answering capabilities.

## Project Overview
- **Upload PDFs:** Upload PDF documents to extract text and create quizzes.
- **Generate Quizzes:** Create multiple-choice and true/false quizzes based on the content of the uploaded PDF.
- **Ask Questions:** Ask questions about the content of the PDF and get instant answers.
- **Calculate Scores:** After taking a quiz, view the score and correct answers.

## Features
- **PDF Text Extraction:**  Extracts text from PDF documents.
- **Text Chunking:** Splits text into manageable chunks for processing.
- **Quiz Generation:** Generates multiple-choice and true/false questions from the extracted text.
- **Question Answering:** Provides answers to user queries based on the content of the uploaded PDF.

## Installation

**1. Clone the repository:**

```
git clone https://github.com/yourusername/study-buddy.git
cd study-buddy
```
**2. Create a virtual environment::**
```
python -m venv venv
```

**3. Activate the virtual environment:**

```
venv\Scripts\activate
```

**4. Install the dependencies:**

```
pip install -r requirements.txt
```
**5. Set up environment variables:**

```
GOOGLE_API_KEY=your_google_api_key
```
## Running the Project
To run the Streamlit application, use the following command:
```
streamlit run main.py
```

## Usage

1) Data Collection: Open the Streamlit app in your browser.
2) **Upload a PDF:** Go to the "Upload Your Document" section and upload your PDF file.
3) **Generate Quizzes:** Choose the quiz type (multiple-choice or true/false) and generate a quiz.
4) **Ask Questions:** Use the "Summarize & Ask Questions" section to ask questions about the content of the uploaded PDF.
5) **Take Quizzes:** Answer the questions and view your score upon submission.


## License
This project is licensed under the MIT License. See the LICENSE file for details.