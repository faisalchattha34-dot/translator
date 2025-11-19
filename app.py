import streamlit as st
import speech_recognition as sr
import requests
import uuid

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
# Speech Recognition
# ---------------------------
st.subheader("🎙️ Speak Something")

recognizer = sr.Recognizer()

def speech_to_text():
    with sr.Microphone() as source:
        st.info("🎧 Listening... Speak now!")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        st.success("Processing voice...")
        return recognizer.recognize_google(audio)
    except:
        return "Could not understand audio"

# ---------------------------
# Language Selection
# ---------------------------
to_lang = st.selectbox("Translate Speech Into:", 
                       ["ur", "en", "ar", "fr", "de", "zh", "hi"])

# ---------------------------
# Run Speech to Translation
# ---------------------------
if st.button("🎤 Start Speaking"):
    if not AZURE_KEY:
        st.error("❌ Enter Azure Key in the sidebar")
    else:
        text = speech_to_text()
        st.write("### 📝 Recognized Text:")
        st.info(text)

        translated = translate_text(text, to_lang)
        st.write("### 🌐 Translated Text:")
        st.success(translated)
