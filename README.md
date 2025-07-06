# 🎓 NoteVidya – Your AI-Powered YouTube Note Companion  
🌐 [Live App](https://notevidya.streamlit.app)

---

## ✨ Overview  
**NoteVidya** is your one-stop AI tool that **automatically generates transcripts, detailed notes**, and offers an intelligent **chatbot** to discuss content from **any YouTube video** — powered by **RAG (Retrieval-Augmented Generation)** and **Gemini AI**.

> 🚀 Just paste a YouTube URL, and we’ll handle the rest.

---

## 🧠 Features

- 🔗 **Smart YouTube URL Parsing**  
  - Instantly validates any YouTube video link.

- 📝 **Transcript Generation**  
  - Uses available YouTube transcript  
  - OR downloads audio and uses speech-to-text (when transcript not available)

- 📓 **AI-Generated Notes**  
  - Summarizes video using **Gemini AI** for structured and clear notes.

- 💬 **RAG-Based Chatbot**  
  - Interact with a chatbot trained on video content using:
    - Hugging Face Embedding Model
    - Gemini LLM

- 🌐 **Web App Interface**  
  - Built and deployed with Streamlit: [notevidya.streamlit.app](https://notevidya.streamlit.app)

---

## 🧭 How It Works

1. **User enters a YouTube video URL**
2. ✅ The app checks if it's a valid link
3. 🎧 If transcript is available → it’s used directly  
   📥 If not → the video is downloaded and audio is transcribed
4. 📝 Gemini AI generates **detailed notes** from transcript
5. 🧠 Embeddings are created using **Hugging Face model**
6. 🤖 Chatbot with **RAG + Gemini** lets you ask questions about the video

---

## 🛠️ Tech Stack

| Component        | Tech Used                        |
|------------------|----------------------------------|
| Frontend         | Streamlit                        |
| Transcript       | YouTube Transcript API / Speech-to-Text |
| Notes Generation | Gemini Model (Google AI)         |
| Chatbot          | RAG with Hugging Face + Gemini   |
| Embeddings       | Hugging Face Sentence Transformers |
| Hosting          | Streamlit Cloud                  |

---

## 🔐 Secrets and API Keys

All secrets are securely stored using Streamlit’s secrets management system in `.streamlit/secrets.toml`.

Example format:
```toml
GOOGLE_API_KEY = "your_google_gemini_api_key"
