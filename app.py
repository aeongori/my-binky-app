import streamlit as st
from openai import OpenAI

# 1. 페이지 설정 (브라우저 탭에 표시될 이름과 아이콘)
st.set_page_config(page_title="Binky's Chelsea Mansion", page_icon="💅")

# 2. 사이드바 설정 (열쇠와 목소리 선택)
with st.sidebar:
    st.title("🇬🇧 Binky's Settings")
    st.markdown("---")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    voice_option = st.selectbox("Binky's Voice Tone:", ["nova", "shimmer"])
    st.info("Tip: 'Nova' is the most sophisticated Oxford-style voice! 🎙️")

# API Key가 없으면 실행 중단
if not api_key:
    st.warning("Please enter your OpenAI API Key, darling! 🔑")
    st.stop()

# 3. 최신 OpenAI 클라이언트 연결
client = OpenAI(api_key=api_key)

# 4. 대화 기록 저장소 (세션 상태)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Binky의 정체성 (System Prompt) - 뼛속까지 런던 첼시 스타일!
def get_binky_response(user_input):
    system_prompt = """
    Your name is Binky, and you are a highly sophisticated, intellectual, and posh woman from Chelsea, London. 
    You embody the 'Sloane Ranger' persona—refined, artistic, and deeply rooted in British high society.

    [STRICT RULES for your speech]:
    1. Always use British English spelling (e.g., 'colour', 'favourite', 'realise', 'programme').
    2. Use posh British vocabulary and idioms (e.g., 'darling', 'lovely', 'splendid', 'rather', 'quite', 'bloody brilliant', 'cheers').
    3. Your tone is elegant, warm, and highly intellectual. You are a mentor who guides the user to speak more 'Refined Oxford English'.
    4. If the user speaks Korean, translate it into very posh British English first, then respond in English.
    5. Always correct any Americanisms or informal slang into a more 'Refined British' style.
    6. Mention Chelsea, afternoon tea, or art occasionally to maintain your persona.
    """
    
    # 대화 맥락 구성
    current_messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        current_messages.append({"role": msg["role"], "content": msg["content"]})
    current_messages.append({"role": "user", "content": user_input})
    
    # 답변 생성
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=current_messages
    )
    return response.choices[0].message.content

# 6. Binky의 목소리 생성 함수 (TTS)
def speak_binky(text):
    response = client.audio.speech.create(
        model="tts-1", 
        voice=voice_option, 
        input=text
    )
    return response.content

# 7. 메인 채팅 인터페이스 UI
st.title("💅 Binky's English Practice")
st.subheader("Direct from Chelsea, London")

# 대화 내용 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력창
if prompt := st.chat_input("Speak to Binky..."):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Binky의 답변 생성 및 표시
    with st.chat_message("assistant"):
        with st.spinner("Binky is thinking..."):
            binky_text = get_binky_response(prompt)
            st.markdown(binky_text)
            
            # 목소리 재생
            try:
                audio_content = speak_binky(binky_text)
                st.audio(audio_content, format="audio/mpeg", autoplay=True)
            except Exception as e:
                st.error(f"Oh dear, the speaker is acting up: {e}")
            
            # 답변 저장
            st.session_state.messages.append({"role": "assistant", "content": binky_text})
