# StudyBuddy Library

A simple mini library app for storing books and journals with uploaded files.

## Features

- Add book and journal records
- Upload files such as PDF, DOCX, JPG, or TXT
- View the collection in one dashboard
- Delete records and associated uploaded files
- Chatbot tutor powered by Gemini using library references as context
- Custom API key support from the app sidebar
- Ready to run as a Streamlit app for deployment

## Run locally with Streamlit

1. Create a virtual environment:
   python -m venv .venv
2. Activate it:
   .venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Start the app:
   streamlit run app.py
5. Open:
   http://localhost:8501

## Chatbot setup

- Open the sidebar in the app
- Fill in your own Gemini API key
- Use the model field to enter a valid Gemini model name, such as `gemini-1.5-flash`
- Ask questions about books and journals already stored in the library
- The bot responds as a tutor and librarian using the available references as context

## Streamlit deployment

This project is set for Streamlit deployment using the main app file:

- `app.py` - main Streamlit interface
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - default Streamlit server config
- `data/library.json` - saved library records
- `uploads/` - uploaded files

> Note: on Streamlit Cloud, uploaded files are temporary and may not persist across app restarts unless you store them in external cloud storage such as S3, GCS, or a database-backed file system.
