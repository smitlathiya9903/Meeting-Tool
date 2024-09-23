import requests
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
from PIL import Image
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"

# Set up headers for the API request
headers = {"Authorization": f"Bearer {API_KEY}"}

def read_file(uploaded_file):
    # Determine the file type and read the content accordingly
    if uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() for page in pdf_reader.pages])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(uploaded_file)
        text = df.to_string()
    elif uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
        text = df.to_string()
    elif uploaded_file.type.startswith("image/"):
        image = Image.open(uploaded_file)
        text = "Image uploaded successfully. (Further processing can be added here)"
    else:
        text = uploaded_file.getvalue().decode("utf-8")  # For text and unsupported files
    return text

def truncate_text(text, max_tokens=900):
    # Truncate the text to a specified number of tokens (words)
    words = text.split()
    return ' '.join(words[:max_tokens])

def query_hf_api(text, points):
    # Define the instruction for the API
    instruction = (
        "Analyze the following document and create a structured meeting agenda. "
        "The agenda should include the following sections: Introduction, Discussion Points, Conclusions, and Action Items. "
        "Make sure to incorporate these key points: {points}. "
        "Each section should be clearly separated with bullet points.\n\n"
        "Use this structure:\n"
        "### Meeting Agenda:\n"
        "1. **Introduction:**\n"
        "   - Brief overview of the meeting's purpose.\n\n"
        "2. **Discussion Points:**\n"
        "   - Problem: Explain the issues or challenges.\n"
        "   - Solution: Propose a solution and its benefits.\n"
        "   - Technology: Discuss technology and its implementation.\n"
        "   - What Needs: Resources and support required.\n\n"
        "3. **Conclusions:**\n"
        "   - Key insights and decisions made.\n\n"
        "4. **Action Items:**\n"
        "   - Assign tasks and responsibilities.\n"
        "   - Schedule follow-up actions.\n\n"
        "Finally, provide a list of important keywords from the agenda."
    )
    
    # Combine the instruction with the text and truncate if necessary
    full_input = truncate_text(f"{instruction}\n\n{text}", max_tokens=900)

    # Set up parameters for the API request
    params = {
        "inputs": full_input,
        "parameters": {
            "max_length": 900,
            "do_sample": False
        }
    }

    # Make the API request
    response = requests.post(API_URL, headers=headers, json=params)

    if response.status_code == 200:
        # Process the response and format the output
        outline = response.json()[0]['summary_text']
        
        point_wise_outline = outline.split('. ')
        structured_outline = "\n".join([f"• {point.strip()}" for point in point_wise_outline if point])
        
        formatted_output = "### Generated Meeting Outline:\n\n" + structured_outline.replace("• ", "\n• ") + "\n\n### Meeting Points:\n"
        formatted_output += "\n".join([f"• {point.strip()}" for point in points.split(",")])
        
        return formatted_output
    else:
        return f"Failed to process the document. Status Code: {response.status_code}, Response: {response.text}"

def generate_meeting_agenda(uploaded_files, meeting_points):
    combined_text = ""

    # Read and combine text from all uploaded files
    for uploaded_file in uploaded_files:
        file_text = read_file(uploaded_file)
        combined_text += f"\n{file_text}"

    # Generate the meeting agenda using the combined text and meeting points
    agenda = query_hf_api(combined_text, meeting_points)
    return agenda