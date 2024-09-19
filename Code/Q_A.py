#---------------------------------------------------------------------------------------------------------------
# This file defines a function qa_process that answers queries based on context retrieved from a vector store. 
# It uses a language model to generate answers by applying a predefined prompt template that handles various types of input, including casual conversation and specific information requests. 
# The function returns a comprehensive answer based on the provided context and query.
#---------------------------------------------------------------------------------------------------------------

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

def qa_process(vectorstore, query):
    """
    Process a query to generate an answer based on the context from the vector store.

    Args:
        vectorstore (VectorStore): The vector store to retrieve context for answering the query.
        query (str): The question or query to be answered.

    Returns:
        str: The generated answer based on the provided context and query.
    """
    if query:
        # Retrieve relevant documents from the vector store based on the query
        docs = vectorstore.similarity_search(query)

        # Define the prompt template for the language model
        prompt_template = """
        You are a helpful assistant. Depending on the type of input, respond appropriately:
        1. If the input is a general greeting or casual conversation (e.g., "Hi", "Hello", "How are you?"), respond in a friendly and conversational manner.
        2. If the input is a specific question or request for information based on the provided context, answer comprehensively using the given context.
        3. If the answer cannot be determined with certainty from the context, indicate uncertainty or suggest potential sources of information.
        
        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        
        # Initialize the language model and prompt template
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        # Load the question-answering chain with the model and prompt
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

        # Generate the response using the context and the query
        response = chain({"input_documents": docs, "question": query}, return_only_outputs=True)

        # Print the documents for debugging purposes
        print(docs)

        return response["output_text"]
