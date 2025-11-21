import streamlit as st
import requests
import tempfile
import os

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="🎤 Voice LLM Assistant", layout="centered", page_icon="🤖")
st.title("🎤 Voice LLM Assistant")

# ---------------------------
# Sidebar Settings
# ---------------------------
st.sidebar.header("🔐 API Settings")
AZURE_SPEECH_KEY = st.sidebar.text_input("Azure Speech Key", type="password")
AZURE_SPEECH_REGION = st.sidebar.text_input("Azure Speech Region", "eastasia")
OPENROUTER_KEY = st.sidebar.text_input("OpenRouter API Key", type="password")

# LLM model
LLM_MODEL = "google/gemma-3-27b-it:free"

# Settings
st.sidebar.header("🌐 Language Settings")
speech_lang = st.sidebar.selectbox("Speech Input Language", ["en-US", "ur-PK", "hi-IN"])
llm_lang = st.sidebar.selectbox("LLM Reply Language", ["en", "ur", "hi"])


# ---------------------------
# Azure Speech-to-Text
# ---------------------------
def speech_to_text(audio_file, language):
    url = (
        f"https://{AZURE_SPEECH_REGION}.stt.speech.microsoft.com/"
        f"speech/recognition/conversation/cognitiveservices/v1?language={language}"
    )

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "audio/wav"
    }

    with open(audio_file, "rb") as f:
        audio_data = f.read()

    response = requests.post(url, headers=headers, data=audio_data)

    if response.status_code != 200:
        return f"Azure STT Error: {response.text}"

    result = response.json()
    return result.get("DisplayText", "Speech not recognized!")


# ---------------------------
# LLM Call (OpenRouter)
# ---------------------------
def ask_llm(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": f"Reply in {llm_lang} language."},
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(url, headers=headers, json=body)

    if res.status_code != 200:
        return f"OpenRouter Error: {res.text}"

    data = res.json()
    return data["choices"][0]["message"]["content"]


# ---------------------------
# Azure Text-to-Speech
# ---------------------------
def text_to_speech(text, language):
    url = f"https://{AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3"
    }

    voices = {
        "en-US": "en-US-JennyNeural",
        "ur-PK": "ur-PK-UzmaNeural",
        "hi-IN": "hi-IN-SwaraNeural",
    }

    voice = voices.get(language, "en-US-JennyNeural")

    ssml = f"""
    <speak version='1.0' xml:lang='{language}'>
        <voice xml:lang='{language}' xml:gender='Female' name='{voice}'>
            {text}
        </voice>
    </speak>
    """

    response = requests.post(url, headers=headers, data=ssml)

    if response.status_code != 200:
        return None, f"Azure TTS Error: {response.text}"

    return response.content, None


# ---------------------------
# AUDIO INPUT
# ---------------------------
st.subheader("🎙 Record Your Question")
audio_bytes = st.audio_input("Press to Record")

if st.button("🎤 Process Voice"):
    if not audio_bytes:
        st.error("Please record audio first!")
    else:
        # Save temp audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes.read())
            temp_path = temp_audio.name

        # Convert Speech → Text
        user_text = speech_to_text(temp_path, speech_lang)
        st.write("### 📝 Recognized Speech:")
        st.info(user_text)

        # LLM Response
        llm_reply = ask_llm(user_text)
        st.write("### 🤖 LLM Reply:")
        st.success(llm_reply)

        # Convert Text → Speech
        audio_output, err = text_to_speech(llm_reply, speech_lang)

        if err:
            st.error(err)
        else:
            st.audio(audio_output, format="audio/mp3")

        os.remove(temp_path)
