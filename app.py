import streamlit as st
import requests
import uuid
import tempfile
import os

st.set_page_config(page_title="🎤 Azure Speech Translator", layout="centered")
st.title("🎤 Speech → Text → Translator (Azure API)")


# ---------------------------
# Sidebar Settings
# ---------------------------
st.sidebar.header("🔐 Azure Settings")

AZURE_SPEECH_KEY = st.sidebar.text_input("Azure Speech Key", type="password")
AZURE_SPEECH_REGION = st.sidebar.text_input("Azure Speech Region", "eastasia")

AZURE_TRANS_KEY = st.sidebar.text_input("Azure Translator Key", type="password")
AZURE_TRANS_REGION = st.sidebar.text_input("Azure Translator Region", "eastasia")
AZURE_TRANS_ENDPOINT = "https://api.cognitive.microsofttranslator.com"


# ---------------------------
# Azure Speech-to-Text
# ---------------------------
def speech_to_text(audio_file):
    st.info("🎧 Converting speech to text...")

    url = f"https://{AZURE_SPEECH_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-US"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "audio/wav"
    }

    with open(audio_file, "rb") as f:
        audio_data = f.read()

    response = requests.post(url, headers=headers, data=audio_data)
    result = response.json()

    try:
        return result["DisplayText"]
    except:
        return f"Error: {result}"


# ---------------------------
# Azure Translator
# ---------------------------
def translate_text(text, to_lang):
    url = f"{AZURE_TRANS_ENDPOINT}/translate?api-version=3.0&to={to_lang}"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANS_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANS_REGION,
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
# Record Audio
# ---------------------------
st.subheader("🎙 Record your voice")

audio_bytes = st.audio_input("Click to record audio")

to_lang = st.selectbox("Translate Into:", ["ur", "en", "ar", "fr", "de", "zh", "hi"])

if st.button("🎤 Convert & Translate"):
    if not audio_bytes:
        st.error("Please record audio first.")
    elif not AZURE_SPEECH_KEY or not AZURE_TRANS_KEY:
        st.error("Enter Azure keys in the sidebar.")
    else:
        # Save temp audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        # Speech → Text
        text = speech_to_text(temp_audio_path)
        st.write("### 📝 Recognized Text:")
        st.info(text)

        # Text → Translation
        translated = translate_text(text, to_lang)
        st.write("### 🌐 Translated Text:")
        st.success(translated)

        os.remove(temp_audio_path)  # Clean up
