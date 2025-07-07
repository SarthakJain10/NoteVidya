import os
import re
import json 
import yt_dlp
import whisper
import time
from urllib.parse import urlparse, parse_qs
import streamlit as st
import requests
import tempfile


def is_valid_youtube_url(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if "youtube.com" in domain:
            query_params = parse_qs(parsed.query)
            video_id = query_params.get("v")
            if video_id and len(video_id[0]) == 11:
                return True

        elif "youtu.be" in domain:
            video_id = parsed.path.strip("/")
            if len(video_id) == 11:
                return True

        return False
    except Exception:
        return False
    

#Function to extract video id from url
def extract_video_url(url: str):
    """
    Extracts the YouTube video ID from a given URL.
    
    Args:
        url (str): The URL string from which to extract the YouTube video ID.
    
    Returns:
        str or None: The extracted 11-character YouTube video ID if found, otherwise None.
    """


    # Parse the URL
    parsed_url = urlparse(url)

    # Check if it is a valid Youtube domain
    if parsed_url.netloc not in ['youtube.com', 'www.youtube.com', 'youtu.be']:
        return None
    
    # Extract query parameter
    query_params = parse_qs(parsed_url.query)
    
    # Try to extract video ID from 'v' parameter directly
    if 'v' in query_params and query_params['v']:
        return query_params['v'][0]
    
    # Patterns for video ID extraction
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
        r"(?:embed\/)([0-9A-Za-z_-]{11})"
    ]

    #Try to extract video Id
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
    return None



# Function to verify youtube video url
def verify_youtube_url(url: str):
    """
    Verify if the provided URL corresponds to a single YouTube video (including standard, shortened, or embedded formats) and return a clean, canonical video URL.

    Args:
        url (str): The input URL to check and normalize.

    Returns:
        str or None: The canonical YouTube video URL (format: 'https://youtu.be/<video_id>') if valid, otherwise None.
    """

    parsed = urlparse(url)
    
    # Check valid YouTube domains
    if parsed.netloc not in ['youtube.com', 'www.youtube.com', 'youtu.be']:
        return None

    # Block pure playlist URLs (no video ID)
    if parsed.path == '/playlist':
        return None

    query = parse_qs(parsed.query)
    video_id = None

    # Standard watch URL (v= parameter)
    if 'v' in query:
        video_id = query['v'][0]
    # Shortened youtu.be URL
    elif parsed.netloc == 'youtu.be':
        video_id = parsed.path[1:]
    # Embedded video URL
    elif '/embed/' in parsed.path:
        video_id = parsed.path.split('/')[-1]

    # Validate and return clean video URL if video_id found
    if video_id and re.match(r'^[A-Za-z0-9_-]{11}$', video_id):
        return f'https://youtu.be/{video_id}'
    
    # Block if only playlist parameters exist (no video ID)
    if 'list' in query and not video_id:
        return None

    return None



def get_youtube_transcript(video_id: str, api_key: str) -> str:
    """
    Fetches YouTube transcript in paragraph format using Supadata API
    
    Args:
        video_id: YouTube video ID (e.g., 'dQw4w9WgXcQ')
        api_key: Your Supadata API key
        
    Returns:
        str: Plain text transcript in paragraph format
    
    Raises:
        HTTPError: If API request fails
    """
    url = "https://api.supadata.ai/v1/youtube/transcript"
    params = {
        "videoId": video_id,
        "text": "true"
    }
    headers = {
        "x-api-key": api_key
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    
    return response.json()["content"]



def download_youtube_video(video_url: str) -> str:
    '''
    Downloads a YouTube video to a temporary directory for processing.
    
    Args:
        video_url (str): URL of the YouTube video
        
    Returns:
        str: Path to the downloaded video file
    '''
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            ydl_opts = {
                'outtmpl': f'{tempdir}/%(id)s.%(ext)s',
                'cookiesfile': 'cookies.txt',
                'noplaylist': True,
                'ignoreerrors': True,
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                if not info or 'requested_downloads' not in info:
                    raise ValueError("Failed to extract video info")
                
                downloaded_file = info['requested_downloads'][0]['filepath']
                return downloaded_file

    except Exception as e:
        st.error(f"Video download failed: {str(e)}")
        return None



# Wait for download
def wait_for_download(file_path, timeout=100):

    """
    Wait for a file to appear at the specified path, checking for both existence and completion of writing, with a timeout.

    Args:
        file_path (str): The path to the file to wait for.
        timeout (int or float, optional): Maximum time (in seconds) to wait for the file to be fully available. Defaults to 100.

    Returns:
        bool: True if the file exists and is fully written within the timeout period, otherwise False.
    """

    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            st.error('timeout: Download took too long')
            return False
        time.sleep(1)

    # Additional check to ensure the file is fully written
    file_size = -1
    while file_size != os.path.getsize(file_path):
        file_size = os.path.getsize(file_path)
        time.sleep(1)

    return True



def transcribe_video(video_path: str) -> str:
    """
    Transcribes a video file using Whisper and returns only the transcript text.
    
    Args:
        video_path (str): Path to the video/audio file
        
    Returns:
        str: Raw transcribed text or None if error occurs
    """
    try:
        model = whisper.load_model('base')
        result = model.transcribe(video_path)
        return result.get('text', '')
    
    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
        return None




def download_and_transcribe(video_url: str) -> str | None:
    """
    Downloads a YouTube video and transcribes its audio content with proper error handling.

    Args:
        video_url (str): Valid YouTube video URL

    Returns:
        str | None: Transcript text or None if failed
    """
    try:
        # Download video to temp location
        video_path = download_youtube_video(video_url)
        if not video_path:
            return None

        # Verify download completion
        if not wait_for_download(video_path):
            st.error("Video download verification failed")
            return None

        # Transcribe audio content
        transcript = transcribe_video(video_path)
        
        # Cleanup temporary files immediately
        try:
            os.remove(video_path)
        except Exception as cleanup_error:
            st.warning(f"Temp file cleanup failed: {cleanup_error}")

        return transcript if transcript else None

    except TimeoutError as e:
        st.error(f"Processing timeout: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Transcription pipeline failed: {str(e)}")
        return None


def display_transcript(tabs, video_id: str, video_url: str, api_key: str):
    """
    Displays transcript using API-first approach with local fallback
    
    Args:
        tabs: Streamlit tabs container
        video_id: YouTube video ID for API
        video_url: Full URL for local processing
        api_key: Supadata API key
    """
    with tabs[0]:
        st.header('📝 Transcript')
        transcript_placeholder = st.empty()
        transcript = None

        # Try API method first
        try:
            transcript = get_youtube_transcript(video_id, api_key)
            st.toast("API transcript fetched successfully", icon="⚡")
        except Exception as api_error:
            st.warning(f"API fallback: {str(api_error)}")
            
            # Fallback to local processing
            try:
                transcript = download_and_transcribe(video_url)
                if transcript:
                    st.toast("Local transcription completed", icon="🤖")
                    
                    # Cache transcript per your [storage preferences](programming.transcript_storage)
                    cache_path = f"transcripts/{video_id}.txt"
                    with open(cache_path, "w") as f:
                        f.write(transcript)
                    
            except Exception as local_error:
                transcript_placeholder.error(f"Both methods failed: {str(local_error)}")
                return

        if transcript:
            transcript_placeholder.markdown(
                f'<div class="custom-tab-content">{transcript}</div>',
                unsafe_allow_html=True
            )
            
        else:
            transcript_placeholder.warning("No transcript available for this video")
