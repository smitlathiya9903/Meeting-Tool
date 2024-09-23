import streamlit as st
import requests
from moviepy.editor import VideoFileClip
import os
from pydub import AudioSegment
from pydub.utils import make_chunks
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hugging Face API token
HF_API_TOKEN = os.getenv("HF_API_KEY")

def check_api_token():
    # Check if the API token is set
    if not HF_API_TOKEN:
        st.error("HF_API_TOKEN is not set. Please check your .env file.")
        return False
    return True

def transcribe_audio(audio_file, max_retries=5, retry_delay=10):
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    with open(audio_file, "rb") as f:
        data = f.read()
    
    retries = 0
    while retries < max_retries:
        response = requests.post(API_URL, headers=headers, data=data)
        result = response.json()
        
        if 'text' in result:
            return result['text']
        elif isinstance(result, list) and len(result) > 0 and 'text' in result[0]:
            return result[0]['text']
        elif 'error' in result:
            error_message = result['error']
            if 'Authorization' in error_message:
                st.error(f"API Token error: {error_message}")
                st.info("Please check your HF_API_TOKEN in the .env file.")
                return None
            elif 'Model is currently loading' in error_message or 'Model too busy' in error_message:
                st.warning(f"Model is busy, retrying in {retry_delay} seconds... (Attempt {retries + 1} of {max_retries})")
                time.sleep(retry_delay)
                retries += 1
            else:
                st.error(f"Unexpected error: {error_message}")
                return None
        else:
            st.error(f"Unexpected API response format: {result}")
            return None
    
    st.error("Transcription failed after multiple retries.")
    return None

def summarize_text(text, max_retries=3, retry_delay=10):
    if not text:
        st.error("No text to summarize.")
        return None

    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    payload = {
        "inputs": text,
        "parameters": {"max_length": 150, "min_length": 50},
    }
    
    retries = 0
    while retries < max_retries:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        if isinstance(result, list) and 'summary_text' in result[0]:
            return result[0]['summary_text']
        elif 'error' in result:
            error_message = result['error']
            if 'Authorization' in error_message:
                st.error(f"API Token error: {error_message}")
                st.info("Please check your HF_API_TOKEN in the .env file.")
                return None
            else:
                st.warning(f"An error occurred: {error_message}. Retrying in {retry_delay} seconds... (Attempt {retries + 1} of {max_retries})")
                time.sleep(retry_delay)
                retries += 1
        else:
            st.error(f"Unexpected API response format: {result}")
            return None
    
    st.error("Summarization failed after multiple retries.")
    return None

def transcribe_audio_chunks(audio_file, chunk_length_ms=60000):
    # Load the audio file and split it into chunks
    audio = AudioSegment.from_mp3(audio_file)
    chunks = make_chunks(audio, chunk_length_ms)
    
    full_transcription = ""
    
    for i, chunk in enumerate(chunks):
        chunk_file = f"chunk_{i}.mp3"
        chunk.export(chunk_file, format="mp3")
        
        try:
            # Transcribe each chunk
            transcription = transcribe_audio(chunk_file)
            if transcription:
                full_transcription += transcription + " "
            else:
                st.error(f"Failed to transcribe chunk {i}")
                break
        except Exception as e:
            st.error(f"Error during transcription of chunk {i}: {str(e)}")
            break
        finally:
            # Clean up the chunk file
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
    
    return full_transcription.strip()

def process_video(video_file):
    if not check_api_token():
        return None, None

    temp_video_path = "temp_video.mp4"
    with open(temp_video_path, "wb") as f:
        f.write(video_file.getbuffer())

    try:
        # Extract audio from video
        video = VideoFileClip(temp_video_path)
        audio = video.audio
        audio.write_audiofile("temp_audio.wav")
        
        # Close the video file to release the file handle
        video.close()
        
        # Convert to mp3 (Whisper prefers mp3)
        audio_segment = AudioSegment.from_wav("temp_audio.wav")
        audio_segment.export("temp_audio.mp3", format="mp3")
        
        # Transcribe audio in chunks
        transcription = transcribe_audio_chunks("temp_audio.mp3")
        if not transcription:
            st.error("Transcription failed. Please check the error messages above.")
            return None, None
        
        # Summarize transcription
        summary = summarize_text(transcription)
        if not summary:
            st.error("Summarization failed. Please check the error messages above.")
            return transcription, None
        
        return transcription, summary
        
    except Exception as e:
        st.error(f"An error occurred during video processing: {str(e)}")
        return None, None
    finally:
        # Clean up temporary files
        for file in ["temp_audio.wav", "temp_audio.mp3", temp_video_path]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except PermissionError:
                    st.warning(f"The temporary file {file} could not be deleted automatically. You may need to remove it manually later.")
                    st.info(f"Temporary file location: {os.path.abspath(file)}")