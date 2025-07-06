import os
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.globals import set_llm_cache
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
import streamlit as st


# Disables catching
set_llm_cache(None)

# Find Google API Key in os environment
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ['GOOGLE_API_KEY'] = st.secrets["api"]["google_api_key"]

# initialize gemini model
model = init_chat_model("gemini-2.0-flash", model_provider="google-genai")

# Initialize open source model
llm = HuggingFaceEndpoint(
    repo_id = "microsoft/Phi-3-mini-4k-instruct",
    task = "text-generation",
    max_new_tokens = 512,
    do_sample = False,
    repetition_penalty = 1.03
)

chat = ChatHuggingFace(llm=llm, verbose=True)

# Design the prompt to denerate notes
prompt_template = """
**Input:**  
A {transcript} of a YouTube lecture video.

**Task:**  
Analyze the transcript and generate comprehensive, structured notes for students. The notes should be detailed, easy to understand, and organized with clear headings and subheadings. Break down complex concepts, highlight key points, and include examples or explanations where necessary to aid student comprehension.

**Output Requirements:**

- Begin with a main title reflecting the lecture topic.
- Use clear headings and subheadings to organize content (e.g., Introduction, Key Concepts, Examples, Summary).
- For each section, provide detailed explanations, definitions, and important points.
- Highlight any important terms, formulas, or concepts.
- Where appropriate, use bullet points or numbered lists for clarity.
- End with a concise summary of the lecture’s main takeaways.

**Instructions for the Summarizer:**
- Focus on clarity and depth to help students understand the material.
- Avoid simply copying the transcript; rephrase and condense information as needed.
- Ensure the notes are suitable for study and revision purposes.
"""

prompt = PromptTemplate(
    template= prompt_template,
    input_variables=['transcript']
)

# Parse the output to remove metadata
parser = StrOutputParser()

# Form chain
chain = prompt | model | parser