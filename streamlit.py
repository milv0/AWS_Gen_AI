import streamlit as st

# 세션 상태 초기화 Default 값
if "TEMPERATURE" not in st.session_state:
    st.session_state.TEMPERATURE = 1.0
if "TOP_P" not in st.session_state:
    st.session_state.TOP_P = 1.0
if "TOP_K" not in st.session_state:
    st.session_state.TOP_K = 500
if "MAX_TOKENS" not in st.session_state:
    st.session_state.MAX_TOKENS = 4096
if "MEMORY_WINDOW" not in st.session_state:
    st.session_state.MEMORY_WINDOW = 10

from pages.chatbot import init_conversationchain

# Streamlit 페이지 설정
st.set_page_config(page_title='🔥 생성형 AI', layout='wide')
st.title("🔥 생성형 AI")

st.markdown("<br><br>", unsafe_allow_html=True)  # 줄 바꿈

st.page_link('pages/calendar.py', label='캘린더', icon='📅')
st.page_link('pages/chatbot.py', label='챗봇', icon='🧑🏻‍💻')
st.page_link('pages/summarizer.py', label='문서요약', icon='📝')
st.page_link('pages/portfolio.py', label='포트폴리오 정리', icon='🧾')

st.page_link('pages/img.py', label='이미지 생성', icon='🖼️')


# 대화 체인 초기화
conv_chain, llm = init_conversationchain()

# llm 객체를 session_state에 저장
st.session_state.llm = llm