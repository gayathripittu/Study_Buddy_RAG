# ---------------------------------------------------------------------------------
# Extracts Text from PDFs: Reads and extracts text from PDF files.
# Splits Text into Chunks: Divides extracted text into manageable chunks for further processing.
# Checks for Duplicate Files: Computes and checks file hashes to identify if a PDF has been previously processed.
# Creates or Loads Embeddings: Creates embeddings from text chunks if the file is new, or loads existing embeddings if the file is a duplicate.
# Manages Pickle and Index Files: Saves or loads processed embeddings and index files to/from disk.
# Handles File Processing: Processes PDFs, including updating metadata and avoiding reprocessing of duplicates.
#----------------------------------------------------------------------------------
import os
import faiss
import hashlib
import pickle
import json
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
print(api_key)  # For debugging purposes

# Initialize embeddings model
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def extract_text_from_pdf(pdf_file_object):
    """
    Extract text from a PDF file object.

    Args:
        pdf_file_object (file-like object): The PDF file from which to extract text.

    Returns:
        str: The extracted text from the PDF.
    """
    pdf = PdfReader(pdf_file_object)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    return text

def text_split(document_text):
    """
    Split the document text into chunks for processing.

    Args:
        document_text (str): The text of the document to be split.

    Returns:
        list: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ".", ","],
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(document_text)
    return chunks

def load_hash_files(json_file):
    """
    Load existing file hashes from a JSON file.

    Args:
        json_file (str): The path to the JSON file containing file hashes.

    Returns:
        list: A list of existing file hashes.
    """
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                existing_file_hashes = json.load(f)
        except json.JSONDecodeError:
            existing_file_hashes = []
            print("The JSON file seems to be empty.")
    else:
        existing_file_hashes = []
    return existing_file_hashes

def create_embeddings(chunks, file_name, pdf_file_object):
    """
    Create or load embeddings for the provided chunks of text.

    Args:
        chunks (list): List of text chunks to embed.
        file_name (str): Name of the PDF file.
        pdf_file_object (file-like object): The PDF file used to check for duplicates.

    Returns:
        FAISS: The vector store containing the embeddings.
    """
    pickle_file_path = "pickle/" + str(file_name[:-4]) + ".pkl"
    index_file_path = "pickle_index/" + str(file_name[:-4]) + ".index"
    
    pdf = PdfReader(pdf_file_object)
    pkl_file_name = str(file_name[:-4]) + ".pkl"

    if os.path.exists(pickle_file_path):
        print("File already exists! Processing skipped.")
        index = faiss.read_index(index_file_path)
        
        with open(pickle_file_path, 'rb') as f:
            metadata = pickle.load(f)
        vectorstore = FAISS(embedding_function=embeddings, index=index, docstore=metadata, index_to_docstore_id={})
    else:
        vectorstore = upload_and_process_file(pdf, chunks, pkl_file_name, pickle_file_path, index_file_path)
    
    return vectorstore

def check_for_duplicates(existing_file_hashes, pdf, json_file, pkl_file_name):
    """
    Check if a file is a duplicate based on its hash.

    Args:
        existing_file_hashes (list): List of existing file hashes.
        pdf (PdfReader): The PDF file to check.
        json_file (str): The path to the JSON file containing file hashes.
        pkl_file_name (str): The name of the pickle file.

    Returns:
        tuple or bool: A tuple with paths to existing files if a duplicate is found; otherwise, False.
    """
    file_hash = calculate_file_hash(pdf)

    for existing_file in existing_file_hashes:
        if existing_file['hash'] == file_hash:
            return "pickle/" + existing_file['filename'], existing_file['index_file_path']
    
    # Update the dictionary with the new filename and hash
    index_file_path = "pickle_index/" + str(pkl_file_name[:-4]) + ".index"
    file_details = {
        "filename": pkl_file_name,
        "hash": file_hash,
        "index_file_path": index_file_path
    }
    print("file_details:", file_details)

    # Append the new dictionary to the list
    existing_file_hashes.append(file_details)

    # Save the updated dictionary back to the JSON file
    with open(json_file, 'w') as f:
        json.dump(existing_file_hashes, f, indent=4)
    return False

def calculate_file_hash(pdf):
    """
    Calculate the SHA-256 hash of the PDF content.

    Args:
        pdf (PdfReader): The PDF file to hash.

    Returns:
        str: The SHA-256 hash of the PDF content.
    """
    pdf_content = b""
    for page in pdf.pages:
        pdf_content += page.extract_text().encode()
    file_hash = hashlib.sha256(pdf_content).hexdigest()
    return file_hash

def upload_and_process_file(pdf, chunks, pkl_file_name, pickle_file_path, index_file_path):
    """
    Upload and process the PDF file to create embeddings if not already processed.

    Args:
        pdf (PdfReader): The PDF file to process.
        chunks (list): List of text chunks from the PDF.
        pkl_file_name (str): Name of the pickle file.
        pickle_file_path (str): Path to the pickle file.
        index_file_path (str): Path to the index file.

    Returns:
        FAISS: The vector store containing the embeddings.
    """
    directory_path = os.path.join(os.getcwd(), 'pickle')
    print("directory_path:", directory_path)

    json_file = os.path.join(directory_path, "file_hashes.json")
    existing_file_hashes = load_hash_files(json_file)

    print("existing_files in upload and process func:", existing_file_hashes)

    is_duplicate = check_for_duplicates(existing_file_hashes, pdf, json_file, pkl_file_name)

    if is_duplicate:
        is_duplicate = list(is_duplicate)
        print("Duplicate file found! Processing skipped.")
        pickle_file_path = is_duplicate[0]
        index_file_path = is_duplicate[1]
        index = faiss.read_index(index_file_path)
        
        with open(pickle_file_path, 'rb') as f:
            metadata = pickle.load(f)
        vectorstore = FAISS(embedding_function=embeddings, index=index, docstore=metadata, index_to_docstore_id={})
    else:
        vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
        faiss.write_index(vectorstore.index, index_file_path)

        with open(pickle_file_path, 'wb') as f:
            pickle.dump(vectorstore.docstore, f)
        print("Embeddings were created for given chunks.")
    return vectorstore
