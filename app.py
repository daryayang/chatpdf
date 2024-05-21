import os
import tempfile
import streamlit as st
from streamlit_chat import message
from agent import Agent

st.set_page_config(page_title="ChatPDF")

def display_messages():
    st.subheader("聊天框")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()

def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner("Thinking"):
            agent_text = st.session_state["agent"].ask(user_text)
        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))
        st.session_state["user_input"] = ""  # Clear the input field after processing

def read_and_save_file():
    st.session_state["agent"].forget()  # to reset the knowledge base
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""
    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name
        with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {file.name}"):
            st.session_state["agent"].ingest(file_path)
        os.remove(file_path)

def main():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state["agent"] = Agent()

    st.header("PDF智能解析")
    st.subheader("请上传一个PDF文件")
    st.file_uploader("Upload document", type=["pdf"], key="file_uploader", on_change=read_and_save_file, label_visibility="collapsed", accept_multiple_files=True)

    st.session_state["ingestion_spinner"] = st.empty()
    st.divider()
    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)
    st.divider()


if __name__ == "__main__":
    main()
