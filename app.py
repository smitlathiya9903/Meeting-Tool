import streamlit as st
from process_doc import generate_meeting_agenda
from process_video import process_video, check_api_token
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    st.title("Meeting Assistant Tool")
    
    # Sidebar for feature selection
    feature = st.sidebar.selectbox("Select Feature", ["Meeting Agenda Generator", "Video Summarizer"])
    
    if feature == "Meeting Agenda Generator":
        st.header("Meeting Agenda Generator")
        
        # File uploader for multiple document types
        uploaded_files = st.file_uploader("Upload the meeting documents", type=["pdf", "txt", "png", "jpg", "docx", "xlsx", "csv"], accept_multiple_files=True)
        
        # Text input for meeting points
        meeting_points = st.text_area("Enter meeting points", placeholder="Discuss Q3 results, Budget allocation...")
        
        if st.button("Generate Agenda"):
            if uploaded_files and meeting_points:
                with st.spinner("Generating agenda..."):
                    # Call function from process_doc.py to generate agenda
                    agenda = generate_meeting_agenda(uploaded_files, meeting_points)
                st.write(agenda)
            else:
                st.write("Please upload at least one document and provide meeting points.")
    
    elif feature == "Video Summarizer":
        st.header("Meeting Video Summarizer")
        
        # Check if API token is valid
        if not check_api_token():
            st.error("API token is not set or invalid. Please check your .env file.")
            return

        # File uploader for video files
        uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])
        
        if uploaded_file is not None:
            # Display the uploaded video
            st.video(uploaded_file)
            
            if st.button("Process Video"):
                with st.spinner("Processing video..."):
                    # Call function from process_video.py to transcribe and summarize
                    transcription, summary = process_video(uploaded_file)
                
                if transcription:
                    st.subheader("Transcription")
                    st.text_area("Full transcription", transcription, height=200)
                    
                    if summary:
                        st.subheader("Summary")
                        st.write(summary)
                    else:
                        st.error("Summarization failed. Please check the error messages above.")
                else:
                    st.error("Video processing failed. Please check the error messages above.")

if __name__ == "__main__":
    main()