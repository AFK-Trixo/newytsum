import streamlit as st
import whisper
from pytube import YouTube
import tempfile
import google.generativeai as genai
from reportlab.pdfgen import canvas
import os

# Initialize the Whisper model with a spinner
def load_whisper_model(model_size="small"):
    with st.spinner("Loading transcription model..."):
        return whisper.load_model(model_size)

# Configure Google Gemini Pro API
def configure_genai(api_key):
    genai.configure(api_key=api_key)

# Download audio from a YouTube video with detailed progress
def download_audio(youtube_link):
    download_message = st.empty()
    with st.spinner("Downloading video audio..."):
        download_message.text("Downloading video audio... This might take a few minutes.")
        yt = YouTube(youtube_link)
        audio_stream = yt.streams.get_audio_only()
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        audio_stream.download(filename=temp_file.name)
        download_message.text("Download completed!")
    return temp_file.name

# Transcribe audio file and detect its language with detailed progress
def transcribe_and_detect_language(model, file_path):
    progress_bar = st.progress(0)
    status_message = st.empty()
    
    status_message.text("Preparing to transcribe...")
    progress_bar.progress(10)
    status_message.text("Transcribing audio and detecting language...")
    progress_bar.progress(50)
    
    result = model.transcribe(file_path, task="transcribe_and_detect_language")
    
    progress_bar.progress(100)
    status_message.text("Transcription completed!")
    
    return result['text'], result['language']

# Generate a summary for a given text with detailed progress
def generate_summary(text, prompt):
    progress_bar = st.progress(0)
    status_message = st.empty()
    
    status_message.text("Generating custom summary...")
    progress_bar.progress(25)
    
    full_prompt = f"{prompt}\n\n{text}"
    gemini_model = genai.GenerativeModel("gemini-pro")
    response = gemini_model.generate_content(full_prompt)
    
    progress_bar.progress(100)
    status_message.text("Summary generation completed!")
    
    return response.text

def export_text(text, filename="export.txt"):
    with open(filename, "w") as file:
        file.write(text)
    return filename

def export_pdf(text, filename="export.pdf"):
    c = canvas.Canvas(filename)
    c.drawString(100, 800, text)  # Simple text addition, more complex formatting can be done
    c.save()
    return filename

def main():
    st.set_page_config(page_title="YouTube Video Summary", page_icon=":clapper:", layout="wide")

    col1, col2 = st.columns([1, 9])
    with col1:
        st.image("yt.png", width=100)  # Adjust path as necessary
    with col2:
        st.title("YouTube Video Summary[BETA]")

    youtube_link = st.text_input("Enter YouTube Video Link:", help="Paste the URL of the YouTube video you want to summarize.")

    if youtube_link:
        # Embed YouTube video
        st.video(youtube_link)

    if st.button("Get Transcript") and youtube_link:
        whisper_model = load_whisper_model("small")
        configure_genai(api_key='AIzaSyDrHF2WLdpSYW4fDdFHLWAkae1ipXvoY3g')  # Use your actual API key here

        audio_file_path = download_audio(youtube_link)
        transcript, detected_language = transcribe_and_detect_language(whisper_model, audio_file_path)

        st.session_state['transcript'] = transcript
        st.session_state['generate_summary_clicked'] = False
        st.session_state['summary_in_progress'] = False

    if 'transcript' in st.session_state:
        st.subheader("Transcript")
        transcript_output = st.text_area("Transcript Output", value=st.session_state['transcript'], height=300, help="You can scroll or edit the text if needed.", key='transcript_output')

        summary_prompt = st.text_input("Enter your summary prompt, e.g., 'Summarize this in less than 250 words', 'Provide a bullet point summary', or 'I want a very detailed summary of this transcript':", key='summary_prompt')
        
        if st.button("Generate Summary"):
            if summary_prompt:
                st.session_state['generate_summary_clicked'] = True
                custom_summary = generate_summary(st.session_state['transcript'], summary_prompt)
                st.session_state['custom_summary'] = custom_summary

    if st.session_state.get('generate_summary_clicked'):
        # Display the generated summary
        st.subheader("Custom Summary")
        custom_summary_output = st.text_area("Custom Summary Output", value=st.session_state.get('custom_summary', ''), height=200, help="Here's the summary based on your prompt.", key='custom_summary_output')

        # Export options
        export_col1, export_col2 = st.columns(2)
        with export_col1:
            if st.button("Export Transcript as TXT"):
                txt_path = export_text(st.session_state['transcript'], "transcript.txt")
                st.download_button(label="Download Transcript as TXT", data=open(txt_path, "rb"), file_name="transcript.txt", mime="text/plain")

        with export_col2:
            if st.button("Export Summary as PDF"):
                pdf_path = export_pdf(st.session_state.get('custom_summary', ''), "summary.pdf")
                st.download_button(label="Download Summary as PDF", data=open(pdf_path, "rb"), file_name="summary.pdf", mime="application/pdf")

    st.markdown("---")
    st.markdown("Built with :heart: using Streamlit, Whisper, and Google Gemini Pro")

if __name__ == "__main__":
    main()