import streamlit as st
from openai import OpenAI  # 최신 방식으로 변경

# 페이지 설정
st.set_page_config(page_title="Binky's Chelsea Mansion", page_icon="💅")

# 사이드바 설정
with st.sidebar:
    st.title("🇬🇧 Binky's Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    voice_option = st.selectbox("Binky's Voice:", ["nova", "shimmer"])

# API Key가 없으면 중단
if not api_key:
    st.warning("API Key를 입력해주세요, darling!")
    st.stop()

# --- 최신 OpenAI 클라이언트 설정 ---
client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 1. 대화 함수 (에러 해결 포인트!) ---
def get_binky_response(user_input):
    system_prompt = "당신은 Made in Chelsea의 Binky입니다. 아주 Posh하고 지적인 영국식 영어를 구사하며 사용자의 영어를 교정해줍니다."
    
    # 세션 메시지 구성
    current_messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        current_messages.append({"role": msg["role"], "content": msg["content"]})
    current_messages.append({"role": "user", "content": user_input})
    
    # 최신 문법으로 변경
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=current_messages
    )
    return response.choices[0].message.content

# --- 2. 목소리 함수 (에러 해결 포인트!) ---
def speak_binky(text):
    # 최신 문법으로 변경
    response = client.audio.speech.create(
        model="tts-1", 
        voice=voice_option, 
        input=text
    )
    return response.content

# --- 3. 메인 채팅 UI ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Binky에게 말을 거세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Binky의 텍스트 답변 생성
        binky_text = get_binky_response(prompt)
        st.markdown(binky_text)
        
        # Binky의 목소리 생성 및 재생
        try:
            audio_content = speak_binky(binky_text)
            st.audio(audio_content, format="audio/mpeg", autoplay=True)
        except Exception as e:
            st.error(f"오디오 생성 중 에러가 발생했어요: {e}")
            
        st.session_state.messages.append({"role": "assistant", "content": binky_text})
