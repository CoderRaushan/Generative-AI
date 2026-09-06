from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import  streamlit as st

llm=ChatGroq(model="openai/gpt-oss-20b",streaming=True)

search=GoogleSerperAPIWrapper()
tools=[search.run]

if "memory" not in st.session_state:
  st.session_state.memory=InMemorySaver()
  st.session_state.history=[]



agent=create_agent(
    model=llm,
    tools=tools,
    checkpointer=st.session_state.memory,
    system_prompt="you are an agent and can search for any question on google"
)




# Building web interface 

st.subheader("Google + Groq : ChatBot, Faster than any agent...")

for message in st.session_state.history:
   role=message["role"]
   content=message["content"]
   st.chat_message(role).markdown(content)

question=st.chat_input("Ask anythig...")

if question:
    st.chat_message("user").markdown(question)
    st.session_state.history.append({"role":"user","content":question})
    response=agent.stream(
    {"messages":[{"role":"user","content":question}]},
    {"configurable":{"thread_id":"1"}},
    stream_mode="messages"
    )

    ai_container=st.chat_message("ai")

    with ai_container:
       space=st.empty()
 
       message=""
       for chunk in response:
          message=message+chunk[0].content
          space.write(message)

       st.session_state.history.append({"role":"ai","content":message})
