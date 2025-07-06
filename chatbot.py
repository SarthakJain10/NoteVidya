import os
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from colorama import Fore, Style, init
import streamlit as st

# Environment configuration
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # Suppress TensorFlow warnings
init(autoreset=True)  # Colorama initialization

# Configuration constants
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
API_TOKEN = st.secrets["api"]["hugging_face_api"]


def create_retrieval_qa_pipeline(transcript):
    if not transcript or not isinstance(transcript, str):
        raise ValueError("Transcript must be a non-empty string.")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\\n\\n", "\\n", " "] 
    )
    # texts = text_splitter.split_text(transcript)
    texts = [t.replace("\n", " ") for t in text_splitter.split_text(transcript) if t is not None]


    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    vectorstore = FAISS.from_texts(texts, embeddings)
    retriever = vectorstore.as_retriever(search_type='similarity', search_kwargs={"k": 4})

    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ['GOOGLE_API_KEY'] = st.secrets["api"]["google_api_key"]

    model = init_chat_model(
        "gemini-2.0-flash",
        model_provider="google-genai",
        max_output_tokens=500,
        temperature=0.3
    )

    prompt_template = """Use the following context to answer:
{context}

Question: {question}
Answer in clear English:"""  # Simplified template

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=model,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={
        "prompt": prompt,
        "document_separator": "\n\n"  # Better context separation
        }
    )

    # Return the QA chain and retriever for chatbot use
    return qa_chain


