import streamlit as st
from openai import OpenAI
import requests
import base64

# 1. 페이지 설정 및 초기화
st.set_page_config(
    page_title="Binky's Study Mansion", 
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화 (메시지, 저장된 문장들)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vault" not in st.session_state:
    st.session_state.vault = []

# 2. 사이드바: 설정 및 학습 저장소
with st.sidebar:
    st.title("🇬🇧 Binky's VIP Settings")
    openai_key = st.text_input("OpenAI API Key", type="password")
    eleven_key = st.text_input("ElevenLabs API Key", type="password")
    voice_id = st.text_input("Voice ID")
    
    st.markdown("---")
    st.header("📚 Binky's Study Vault")
    if not st.session_state.vault:
        st.write("저장된 문장이 없어요, darling! 대화를 시작해봐요. ✨")
    else:
        for i, item in enumerate(reversed(st.session_state.vault)):
            with st.expander(f"Entry #{len(st.session_state.vault) - i}: {item['text'][:30]}..."):
                st.write(f"**Binky:** {item['text']}")
                st.audio(item['audio'], format="audio/mpeg")
                if st.button(f"삭제하기", key=f"del_{i}"):
                    st.session_state.vault.pop(-(i+1))
                    st.rerun()

# 필수 키 확인
if not openai_key or not eleven_key or not voice_id:
    st.warning("사이드바에 모든 Key와 Voice ID를 입력해주세요, darling! 🔑")
    st.stop()

client = OpenAI(api_key=openai_key)

# 3. 함수 정의
def get_binky_response(user_input):
    system_prompt = "Your name is Binky Felstead. Speak in a very bright, bubbly, and posh Chelsea accent. Correct the user's English elegantly."
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

# 4. 메인 화면 UI
st.title("💅 Binky's Real Voice Practice")
st.caption("Perfect your British accent with Binky's real voice!")

# 채팅 기록 출력
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # 어시스턴트 답변에만 오디오 및 저장 버튼 표시
        if msg["role"] == "assistant":
            audio_key = f"audio_{i}"
            if "audio" in msg:
                st.audio(msg["audio"], format="audio/mpeg")
                if st.button("✨ 이 문장 저장하기 (Save to Vault)", key=f"save_{i}"):
                    # 보관함에 중복 확인 후 저장
                    if not any(v['text'] == msg['content'] for v in st.session_state.vault):
                        st.session_state.vault.append({"text": msg["content"], "audio": msg["audio"]})
                        st.success("보관함에 저장되었어요, darling! 🎁")

# 채팅 입력창
if prompt := st.chat_input("Binky에게 말을 걸어보세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Binky가 생각 중이에요..."):
            binky_text = get_binky_response(prompt)
            audio_content = speak_binky_eleven(binky_text)
            
            st.markdown(binky_text)
            st.audio(audio_content, format="audio/mpeg", autoplay=True)
            
            # 메시지 객체에 오디오 데이터 포함하여 저장
            st.session_state.messages.append({
                "role": "assistant", 
                "content": binky_text, 
                "audio": audio_content
            })
            st.rerun() # 버튼 렌더링을 위해 리런
