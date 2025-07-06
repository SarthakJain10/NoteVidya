import streamlit as st
import transcript_generator
from notes_generator import chain
from chatbot import create_retrieval_qa_pipeline

Supadata_api = st.secrets["api"]["Supadata_api"] # transcript generation

st.set_page_config(
    page_title = "Note Vidya",
    page_icon = "📝",
    layout = "wide"
)


st.markdown("""
<h1 style="
    background: linear-gradient(90deg, #ff8a00, #e52e71);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 4rem;
    font-weight: bold;
    text-align: center;
    ">
    Welcome to <span style="color: #ff8a00;">NoteVidya</span> 
    <br><hr style="border: none; height: 2px; background: #e52e71; margin: 16px 0;">
    <span style="color: #e52e71;"> Your AI-Powered Note-Taking Assistant</span><br>
</h1>
""", unsafe_allow_html=True)


custom_css = """
<style>
.st-key-custom_input {
    max-width: 1300px;
    margin-bottom: 1.5em;
}

/* Enlarge and style the input box */
.st-key-custom_input input {
    background: #f8fafc;
    color: #222831;
    border: 2px solid #d1d5db;
    border-radius: 8px;
    padding: 18px 22px;
    font-size: 1.25em;
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
    box-shadow: 0 2px 6px rgba(60,72,88,0.08);
    outline: none;
    width: 100%;
    box-sizing: border-box;
}

/* Focus state */
.st-key-custom_input input:focus {
    border-color: #2563eb;
    background: #eef2fb;
    box-shadow: 0 0 0 3px #2563eb33;
}

/* Placeholder styling */
.st-key-custom_input input::placeholder {
    color: #94a3b8;
    opacity: 1;
    font-style: italic;
}

/* Hover effect */
.st-key-custom_input input:hover {
    border-color: #94a3b8;
    background: #f1f5f9;
}
</style>
"""


st.markdown(custom_css, unsafe_allow_html=True)

with st.container(border = True):
    col1, col2 = st.columns([3,1])
    with col1:
        video_url = st.text_input(
            "Enter Youtube URL:",
            placeholder = "https://www.youtube.com/watch?v=...",
            help= "Paste any Youtube video link here"
        ).strip()
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("Analyze Video", use_container_width=True)

# Tabs Activation Logic
if analyze_btn and video_url:
    try:
        # URL Validation & Processing
        try:
            video_id = transcript_generator.extract_video_url(video_url)
        except Exception:
            video_url = transcript_generator.verify_youtube_url(video_url)
            video_id = transcript_generator.extract_video_url(video_url)

        # Video Section
        st.header("🎥 Watch Video")
        st.video(video_url)
        st.caption("Enjoy the YouTube video here.")

        # Custom CSS Injection
        st.markdown("""
        <style>
        /* Base tab style */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.3rem;
            font-weight: 600;
            color: #3a3a3a;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            padding: 10px 24px;
            margin-bottom: 0px;
        }

        /* Active and inactive tabs */
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #F63366 !important;
            color: #fff !important;
            border-radius: 8px 8px 0 0 !important;
        }

        .stTabs [data-baseweb="tab-list"] button[aria-selected="false"] {
            background-color: #f0f2f6 !important;
            color: #3a3a3a !important;
            border-radius: 8px 8px 0 0 !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            margin-bottom: 16px;
        }

        /* Default (light mode) content text color */
        .custom-tab-content {
            font-size: 20px !important;
            line-height: 1.7;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            color: #232323;
        }

        /* Dark mode overrides */
        @media (prefers-color-scheme: dark) {
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                color: #ffffff;
            }

            .stTabs [data-baseweb="tab-list"] button[aria-selected="false"] {
                background-color: #2c2c2c !important;
                color: #ffffff !important;
            }

            .custom-tab-content {
                color: #e0e0e0;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        # Tabs Setup
        tabs = st.tabs(['Transcript', 'Notes', 'Chatbot'])

        # Transcript Tab
        with tabs[0]:
            st.header('📝 Transcript')
            transcript_placeholder = st.empty()
            transcript = None

            # API + Local Fallback
            try:
                transcript = transcript_generator.get_youtube_transcript(video_id, Supadata_api)
                st.toast("API transcript fetched successfully", icon="⚡")
            except Exception as api_error:
                st.warning(f"API fallback: {str(api_error)}")
                try:
                    transcript = transcript_generator.download_and_transcribe(video_url)
                    if transcript:
                        st.toast("Local transcription completed", icon="🤖")
                        with open(f"transcripts/{video_id}.txt", "w") as f:
                            f.write(transcript)
                except Exception as local_error:
                    transcript_placeholder.error(f"Both methods failed: {str(local_error)}")

            if 'tst' not in st.session_state:
                st.session_state.tst = transcript

            # Display Result
            if transcript:
                transcript_placeholder.markdown(
                    f'<div class="custom-tab-content">{transcript or "No transcript available"}</div>',
                    unsafe_allow_html=True)
            else:
                transcript_placeholder.warning("No transcript available")

        # Notes Tab
        with tabs[1]:
            st.header("📚 Detailed Notes")
            notes_placeholder = st.empty()

            try:    
                # Generation and display notes
                with st.spinner("Generating notes..."):
                    notes_result = chain.invoke({"transcript": transcript},
                                                config={'run_name': 'SummaryGeneration'})
                    # notes_placeholder.markdown(notes_result)
                    notes_placeholder.markdown(
                        f'<div class="custom-tab-content">{notes_result}</div>',
                        unsafe_allow_html=True
                    )
            
            except FileNotFoundError:
                notes_placeholder.write("Transcript file not found.")
            except Exception as e:
                notes_placeholder.write(f"An error occurred while reading the transcript: {str(e)}")


        # Chatbot Tab Implementation 
        with tabs[2]:
            st.header("🤖 Chatbot")

            transcript = st.session_state.get("tst")
    

            # Initialize session state only if not present
            if "messages" not in st.session_state:
                st.session_state.messages = []

            chat_container = st.container()

            # Display chat messages from history on app rerun
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Accept user input
            if prompt := st.chat_input("How may i help you?"):
                # Display user message in chat message container
                with st.chat_message("user"):
                    st.markdown(prompt)
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})

            qa_chain= create_retrieval_qa_pipeline(transcript)

            # Streamed response emulator
            def response_generator():
                response = qa_chain.invoke({"query": prompt})
                return response


            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                response_text = response_generator()
                st.markdown(response_text)
                # response = st.write_stream(response_generator())
                
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response_text})
          

    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    if not video_url and analyze_btn:
        st.warning("Please enter a valid Youtube URL!")

