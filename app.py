import streamlit as st
import speech_recognition as sr
import requests
import uuid
import tempfile
import os

st.set_page_config(page_title="🎤 Speech Translator", layout="centered")
st.title("🎤 Speech → Text → Translator (Azure API)")

# ---------------------------
# Sidebar: Azure Credentials
# ---------------------------
st.sidebar.header("🔐 Azure Translator Settings")

AZURE_KEY = st.sidebar.text_input("Azure Key", type="password")
AZURE_ENDPOINT = st.sidebar.text_input("Azure Endpoint", "https://api.cognitive.microsofttranslator.com")
AZURE_REGION = st.sidebar.text_input("Azure Region", "eastasia")

# ---------------------------
# Translation Function
# ---------------------------
def translate_text(text, to_lang):
    url = f"{AZURE_ENDPOINT}/translate?api-version=3.0&to={to_lang}"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_REGION,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4())
    }

    body = [{"text": text}]
    response = requests.post(url, headers=headers, json=body)
    result = response.json()

    try:
        return result[0]["translations"][0]["text"]
    except:
        return f"Error: {result}"

# ---------------------------
# Speech to Text using UPLOADED AUDIO
# ---------------------------
def speech_to_text(audio_file):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio)
    except:
        return "Could not understand audio"


# ---------------------------
# Audio Recorder
# ---------------------------
st.subheader("🎙️ Record Your Voice")

audio_bytes = st.audio_input("Click to record your voice")

to_lang = st.selectbox("Translate Into:", ["ur", "en", "ar", "fr", "de", "zh", "hi"])

if st.button("🎤 Convert & Translate"):
    if not audio_bytes:
        st.error("Please record your voice first!")
    elif not AZURE_KEY:
        st.error("Enter Azure Key!")
    else:
        # Save temp audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        # Speech to Text
        text = speech_to_text(temp_audio_path)

        st.write("### 📝 Recognized Text:")
        st.info(text)

        # Translate
        translated = translate_text(text, to_lang)
        st.write("### 🌐 Translated Text:")
        st.success(translated)

        # Cleanup
        os.remove(temp_audio_path)
