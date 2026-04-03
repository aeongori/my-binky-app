import streamlit as st
from openai import OpenAI
import requests

# 1. 페이지 설정 (사이드바가 항상 열려 있도록 설정!)
st.set_page_config(
    page_title="Binky's Chelsea Mansion", 
    page_icon="💅",
    initial_sidebar_state="expanded" # 이 부분이 핵심입니다!
)

# 2. 사이드바 설정
with st.sidebar:
    st.title("🇬🇧 Binky's VIP Settings")
    st.markdown("---")
    # 여기에 복사해둔 키들을 넣으시면 됩니다!
    openai_key = st.text_input("OpenAI API Key", type="password")
    eleven_key = st.text_input("ElevenLabs API Key", type="password")
    voice_id = st.text_input("Voice ID")

# 필수 정보 체크
if not openai_key or not eleven_key or not voice_id:
    st.warning("사이드바에 모든 Key와 Voice ID를 입력해주세요, darling! 🔑")
    st.stop()

# (이하 기존 코드와 동일...)
client = OpenAI(api_key=openai_key)
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_binky_response(user_input):
    system_prompt = "Your name is Binky Felstead. Speak in a very posh Chelsea accent. Correct the user's English."
    current_messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        current_messages.append({"role": msg["role"], "content": msg["content"]})
    current_messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(model="gpt-4o", messages=current_messages)
    return response.choices[0].message.content

def speak_binky_eleven(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": eleven_key}
    data = {"text": text, "model_id": "eleven_multilingual_v2"}
    response = requests.post(url, json=data, headers=headers)
    return response.content

st.title("💅 Binky's Real Voice Practice")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Binky에게 말을 걸어보세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        binky_text = get_binky_response(prompt)
        st.markdown(binky_text)
        audio_content = speak_binky_eleven(binky_text)
        st.audio(audio_content, format="audio/mpeg", autoplay=True)
        st.session_state.messages.append({"role": "assistant", "content": binky_text})
