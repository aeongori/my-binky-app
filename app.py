import streamlit as st
import openai
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
from io import BytesIO

# 1. 페이지 설정 및 디자인 (첼시 스타일)
st.set_page_config(page_title="Binky's Chelsea Mansion", page_icon="💅", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #fdfaf6; }
    .stChatMessage.user { background-color: #e3f2fd; border-radius: 15px; }
    .stChatMessage.assistant { background-color: #fce4ec; border-radius: 15px; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #4b0082; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. 세션 상태 관리 (대화 기록)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 사이드바 설정
with st.sidebar:
    st.title("🇬🇧 Binky's Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    voice_option = st.selectbox("Binky's Voice Tone:", ["nova", "shimmer"])
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("5년 뒤 런던에서의 삶을 응원합니다!")

st.title("🎙️ Live with Binky Felstead")
st.write("Binky가 당신의 영어를 실시간으로 교정하며, 옥스포드 스타일의 지성미를 더해줍니다.")

if not api_key:
    st.warning("먼저 사이드바에 API Key를 입력해주세요, darling!")
    st.stop()

openai.api_key = api_key

# --- 핵심 로직 함수 ---

def get_binky_response(user_input):
    """Binky 페르소나: 한국어 번역, 영어 교정, 지적인 톤 유지"""
    system_prompt = """
    당신은 'Made in Chelsea'의 Binky Felstead입니다. 
    1. 말투: Posh, Chic, 위트 있으며 'literally', 'darling', 'mate'를 즐겨 씁니다.
    2. 지성: 예술과 문화에 깊은 식견이 있는 옥스포드 스타일의 지성미를 갖췄습니다.
    3. 미션: 
       - 사용자가 한국어로 말하면 -> 완벽하고 세련된 'Sloane Ranger' 영어로 번역하세요.
       - 사용자가 영어로 말하면 -> 대화를 이어가되, 더 Posh하고 자연스러운 영국식 표현으로 즉시 교정해주세요.
       - 교정 시 "Darling, it's actually more natural to say..." 처럼 다정하게 팁을 주세요.
    """
    messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
    messages.append({"role": "user", "content": user_input})
    
    response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content

def speak_binky(text):
    """Binky의 목소리로 텍스트 읽기 (TTS)"""
    response = openai.audio.speech.create(model="tts-1", voice=voice_option, input=text)
    return response.content

def extract_text_from_pdf(file):
    """PDF에서 텍스트 추출"""
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# --- 메인 화면 구성 (탭) ---

tab1, tab2 = st.tabs(["💬 Live Chat & Correction", "📖 Script/URL/PDF Reader"])

# Tab 1: 실시간 대화 및 음성 인식 연습
with tab1:
    st.info("💡 폰 키보드의 '마이크' 버튼을 눌러 음성으로 대화해보세요!")
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
            audio_content = speak_binky(binky_text)
            st.audio(audio_content, format="audio/mpeg", autoplay=True)
            st.session_state.messages.append({"role": "assistant", "content": binky_text})

# Tab 2: 외부 컨텐츠 낭독 (교재 그대로 읽기 포함)
with tab2:
    st.subheader("Binky's Reading Room")
    src_type = st.radio("소스 선택:", ["Direct Script", "URL (Web Article)", "PDF Document 📄"])
    
    raw_content = ""
    if src_type == "Direct Script":
        raw_content = st.text_area("Binky가 읽어줄 내용을 입력하세요.")
    elif src_type == "URL (Web Article)":
        url = st.text_input("웹사이트 주소를 입력하세요.")
        if url:
            try:
                res = requests.get(url)
                soup = BeautifulSoup(res.text, 'html.parser')
                raw_content = ' '.join([p.text for p in soup.find_all('p')[:5]])
                st.success("내용을 가져왔습니다!")
            except: st.error("URL 로드 실패.")
    elif src_type == "PDF Document 📄":
        file = st.file_uploader("PDF 업로드", type="pdf")
        if file:
            raw_content = extract_text_from_pdf(file)
            st.success("PDF 텍스트 추출 완료!")

    if st.button("Read in Binky's Voice"):
        if raw_content:
            with st.spinner("Binky가 낭독을 준비합니다..."):
                # 교재 내용을 그대로 읽어주는 프롬프트
                read_prompt = f"Darling, I'll read this for you. Listen to my accent carefully:\n\n{raw_content[:1000]}"
                audio_script = speak_binky(read_content if len(raw_content) < 1000 else raw_content[:1000])
                st.audio(audio_script, format="audio/mpeg")
        else: st.warning("내용을 먼저 입력해주세요.")
