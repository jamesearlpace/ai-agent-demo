from azure.ai.agents import AgentsClient
from azure.ai.agents.models import OpenAIKeyCredential, FunctionTool, ToolSet, MessageRole
import os
from dotenv import load_dotenv
import streamlit as st
from user_functions import user_functions

load_dotenv()

st.set_page_config(page_title="AI Support Agent")
st.title("AI Support Agent")

project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_API_KEY")

if "client" not in st.session_state:
    st.session_state.client = AgentsClient(
        endpoint=project_endpoint,
        credential=OpenAIKeyCredential(api_key)  # correct credential type
    )
    toolset = ToolSet()
    toolset.add(FunctionTool(user_functions))
    st.session_state.client.enable_auto_function_calls(toolset)
    st.session_state.agent = st.session_state.client.create_agent(
        model=model_deployment,
        name="support-agent",
        instructions="You are a helpful support assistant.",
        toolset=toolset
    )
    st.session_state.thread = st.session_state.client.threads.create()
    st.session_state.history = []

prompt = st.chat_input("Ask something...")
if prompt:
    st.session_state.history.append(("user", prompt))
    st.session_state.client.messages.create(
        thread_id=st.session_state.thread.id,
        role="user",
        content=prompt
    )
    run = st.session_state.client.runs.create_and_process(
        thread_id=st.session_state.thread.id,
        agent_id=st.session_state.agent.id
    )
    msg = st.session_state.client.messages.get_last_message_text_by_role(
        thread_id=st.session_state.thread.id,
        role=MessageRole.AGENT
    )
    answer = msg.text.value if msg else "No response."
    st.session_state.history.append(("agent", answer))

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)
