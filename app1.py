import streamlit as st
import requests
import uuid
import tempfile
import os

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="🎤 Voice LLM Assistant", layout="centered", page_icon="🤖", initial_sidebar_state="expanded")
st.title("🎤 Voice LLM Assistant")

# ---------------------------
# Sidebar Settings
# ---------------------------
st.sidebar.header("🔐 API Settings")
AZURE_SPEECH_KEY = st.sidebar.text_input("Azure Speech Key", type="password")
AZURE_SPEECH_REGION = st.sidebar.text_input("Azure Speech Region", "eastasia")
OPENROUTER_KEY = st.sidebar.text_input("OpenRouter LLM API Key", type="password")
LLM_MODEL = "google/gemma-3-27b-it:free"

# Language selection
st.sidebar.header("🌐 Settings")
speech_lang = st.sidebar.selectbox("Speech Language (for STT & TTS)", ["en-US", "ur-PK", "hi-IN", "fr-FR", "de-DE", "zh-CN"])
llm_lang = st.sidebar.selectbox("LLM Response Language", ["en", "ur", "hi", "fr", "de", "zh"])

# ---------------------------
# Initialize session state for conversation
# ---------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# ---------------------------
# Azure Speech-to-Text
# ---------------------------
def speech_to_text(audio_file, language):
    url = f"https://{AZURE_SPEECH_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language={language}"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "audio/wav"
    }

    with open(audio_file, "rb") as f:
        audio_data = f.read()

    response = requests.post(url, headers=headers, data=audio_data)
    result = response.json()

    return result.get("DisplayText", "Could not recognize speech")

# ---------------------------
# OpenRouter LLM
# ---------------------------
def ask_llm(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    res = requests.post(url, headers=headers, json=body).json()
    try:
        return res["choices"][0]["message"]["content"]
    except:
        return "LLM could not generate response."

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
    ssml = f"""
    <speak version='1.0' xml:lang='{language}'>
        <voice xml:lang='{language}' xml:gender='Female' name='{language}-JennyNeural'>
            {text}
        </voice>
    </speak>
    """
    response = requests.post(url, headers=headers, data=ssml)
    return response.content

# ---------------------------
# Record Audio
# ---------------------------
st.subheader("🎙 Record Your Question")
audio_bytes = st.audio_input("Click to record audio")

if st.button("🎤 Process Voice"):
    if not audio_bytes:
        st.error("Please record audio first!")
    elif not (AZURE_SPEECH_KEY and OPENROUTER_KEY):
        st.error("Enter Azure & OpenRouter API keys in the sidebar.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        # Speech → Text
        user_text = speech_to_text(temp_audio_path, speech_lang)
        st.write("### 📝 Your Speech:")
        st.info(user_text)

        # Text → LLM
        llm_reply = ask_llm(user_text)
        st.write("### 🤖 LLM Reply:")
        st.success(llm_reply)

        # Add to conversation history
        st.session_state.conversation.append({"user": user_text, "llm": llm_reply})

        # Text → Speech
        audio_output = text_to_speech(llm_reply, speech_lang)
        st.audio(audio_output, format="audio/mp3")

        os.remove(temp_audio_path)

# ---------------------------
# Conversation History
# ---------------------------
if st.session_state.conversation:
    st.subheader("📜 Conversation History")
    for i, chat in enumerate(st.session_state.conversation):
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**LLM:** {chat['llm']}")
        st.markdown("---")
