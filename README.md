# NoteVidya 📽️✍️

**NoteVidya** is an intelligent YouTube video note-taking application that simplifies learning from video content. It enables users to generate clean, structured notes and interact with a personalized chatbot using Retrieval-Augmented Generation (RAG), all from just a YouTube video link.

---

## 🔍 Overview

Many learners struggle to extract meaningful information from long-form video content. NoteVidya addresses this by automating the process of:

1. **Transcribing** spoken content from YouTube videos.
2. **Structuring** transcripts into high-quality notes.
3. **Providing** a smart chatbot to answer user queries based on the video content.

Whether you are a student, researcher, or lifelong learner, NoteVidya saves time and enhances comprehension.

---

## 🧠 Features

- **YouTube Video Integration**: Paste a video URL and extract its core learning content.
- **Automatic Transcription**: Speech is transcribed using robust speech-to-text models.
- **Structured Note Generation**: Converts the transcript into well-organized and readable notes using summarization and formatting techniques.
- **RAG-based Chatbot**: Ask contextual questions about the video using a Retrieval-Augmented Generation pipeline.
- **User-Friendly Interface**: Simple and intuitive UI for seamless interaction.

---

## 🚀 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 
- **Transcription**: `Whisper` (OpenAI)
- **Summarization & Notes**: `LangChain`, `transformers`, `Gemini` APIs
- **Chatbot**: RAG pipeline with `FAISS` for semantic search
- **Storage**: Local or cloud-based vector store for embeddings

---

## 📦 Installation

```bash
git clone https://github.com/SarthakJain10/NoteVidya.git
cd NoteVidya
```

## ⚠️ Limitations & Future Improvements
- Currently supports only public YouTube videos.

- May take time for long videos depending on system resources.

- UI/UX enhancements planned.

- Adding support for multi-language videos and more accurate timestamped note sections.

## 🤝 Contributing
We welcome contributions from the community. Please fork the repository, create a new branch, and submit a pull request with appropriate documentation.

## 📄 License
This project is licensed under the Apache 2.O License. See the LICENSE file for details.


