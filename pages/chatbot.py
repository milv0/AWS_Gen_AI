import os
import streamlit as st
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_aws import ChatBedrock
from langchain.callbacks.base import BaseCallbackHandler

# 세션 상태 초기화 Default 값
if "TEMPERATURE" not in st.session_state:
    st.session_state.TEMPERATURE = 0.9
if "TOP_P" not in st.session_state:
    st.session_state.TOP_P = 1.0
if "TOP_K" not in st.session_state:
    st.session_state.TOP_K = 500
if "MAX_TOKENS" not in st.session_state:
    st.session_state.MAX_TOKENS = 4096
if "MEMORY_WINDOW" not in st.session_state:
    st.session_state.MEMORY_WINDOW = 10


# AWS 리전 설정
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"  

# 모델 ID 설정
MODEL_ID = "CLAUDE_3_SONNET_MODEL_ID"

# 프롬프트 템플릿 생성
CLAUDE_PROMPT = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),  # 대화 기록을 저장할 플레이스홀더
    HumanMessagePromptTemplate.from_template("{input}"),  # 사용자 입력을 받을 플레이스홀더
])

# 초기 메시지 설정
INIT_MESSAGE = {"role": "assistant",
                "content": "안녕하세요! 저는 Claude 챗봇이에요! 뭐든 물어봐주세요! 😄"}

# 시스템 프롬프트 설정
SYSTEM_PROMPT = "You're a cool assistant, love to response with emoji."

# 스트리밍 콜백 핸들러 클래스 정의
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

# 대화 체인 초기화 함수
def init_conversationchain() -> (ConversationChain, ChatBedrock): # type: ignore
    model_kwargs = {'temperature': st.session_state.TEMPERATURE,
                    'top_p': st.session_state.TOP_P,
                    'top_k': st.session_state.TOP_K,
                    'max_tokens': st.session_state.MAX_TOKENS,
                    'system': SYSTEM_PROMPT}  # 모델 파라미터 설정

    llm = ChatBedrock(
        model_id=MODEL_ID,
        model_kwargs=model_kwargs,
        streaming=True  # 스트리밍 활성화
    )

    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=ConversationBufferWindowMemory(
            k=st.session_state.MEMORY_WINDOW, ai_prefix="Assistant", chat_memory=StreamlitChatMessageHistory(), return_messages=True),  # 메모리 설정
        prompt=CLAUDE_PROMPT
    )

    # 세션 상태에 초기 메시지 저장
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [INIT_MESSAGE]

    return conversation, llm

# 응답 생성 함수
def generate_response(conversation: ConversationChain, input_text: str) -> str:
    return conversation.run(input=input_text, callbacks=[StreamHandler(st.empty())])

# 새로운 대화 시작 함수
def new_chat() -> None:
    st.session_state["messages"] = [INIT_MESSAGE]
    st.session_state["langchain_messages"] = []

# 대화 체인 초기화
conv_chain, llm = init_conversationchain()


# Streamlit 
if __name__ == "__main__":


    st.set_page_config(page_title='🧑🏻‍💻 AI 챗봇', layout='wide')
    st.title("🧑🏻‍💻 AI 챗봇")

    # 대화 체인 초기화, llm 객체를 session_state에 저장
    conv_chain, llm = init_conversationchain()
    st.session_state.llm = llm    

    # 사이드바에 파라미터 설정 추가
    with st.sidebar:
        st.markdown("## 추론 파라미터")
        TEMPERATURE = st.slider("Temperature", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
        TOP_P = st.slider("Top-P", min_value=0.0, max_value=1.0, value=1.00, step=0.01)
        TOP_K = st.slider("Top-K", min_value=1, max_value=500, value=500, step=5)
        MAX_TOKENS = st.slider("Max Token", min_value=0, max_value=4096, value=4096, step=8)
        MEMORY_WINDOW = st.slider("Memory Window", min_value=0, max_value=10, value=10, step=1)

    # 스트리밍 콜백 핸들러 클래스 정의
    class StreamHandler(BaseCallbackHandler):
        def __init__(self, container):
            self.container = container
            self.text = ""

        def on_llm_new_token(self, token: str, **kwargs) -> None:
            self.text += token
            self.container.markdown(self.text)

    # 사이드바에 새로운 대화 시작 버튼 추가
    st.sidebar.button("New Chat", on_click=new_chat, type='primary')

    # 기존 대화 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 받기
    prompt = st.chat_input()

    # 사용자 입력이 있을 경우 처리
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # 마지막 메시지가 어시스턴트가 아닌 경우 새로운 응답 생성
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = generate_response(conv_chain, prompt)
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)

