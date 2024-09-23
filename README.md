# Meeting Assistant Tool

This project is a Streamlit-based web application that provides two main features:
1. Meeting Agenda Generator
2. Video Summarizer

## Features

### 1. Meeting Agenda Generator
- Upload multiple documents (PDF, TXT, PNG, JPG, DOCX, XLSX, CSV)
- Input meeting points
- Generate a structured meeting agenda based on the uploaded documents and meeting points

### 2. Video Summarizer
- Upload a video file (MP4, AVI, MOV)
- Transcribe the audio from the video
- Generate a summary of the transcribed content

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/meeting-assistant-tool.git
   cd meeting-assistant-tool
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Hugging Face API token:
   - Create a `.env` file in the project root directory
   - Add your Hugging Face API token to the `.env` file:
     ```
     HF_API_TOKEN=your_huggingface_api_token_here
     ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`)

3. Use the sidebar to select the desired feature:
   - Meeting Agenda Generator
   - Video Summarizer

4. Follow the on-screen instructions for each feature:
   - For the Meeting Agenda Generator:
     - Upload one or more documents
     - Enter meeting points
     - Click "Generate Agenda"
   - For the Video Summarizer:
     - Upload a video file
     - Click "Process Video"

## Project Structure

- `app.py`: Main Streamlit application file
- `feature1_backend.py`: Backend logic for the Meeting Agenda Generator
- `feature2_backend.py`: Backend logic for the Video Summarizer
- `requirements.txt`: List of Python package dependencies
- `.env`: Environment file for storing API tokens (not tracked in git)

## Troubleshooting

- If you encounter API token errors:
  1. Check that your `.env` file is in the project root directory
  2. Verify that the `HF_API_TOKEN` in the `.env` file is correct
  3. Try regenerating your Hugging Face API token and updating it in the `.env` file

- For other issues, check the error messages in the Streamlit interface or console output

## Contributing

Contributions to improve the Meeting Assistant Tool are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit them (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project uses the Hugging Face API for natural language processing tasks
- Streamlit is used for creating the web interface
- Various open-source libraries are used for document processing and video handling
