
# from dotenv import load_dotenv
# load_dotenv()

# from langchain_google_genai import ChatGoogleGenerativeAI
# llm=ChatGoogleGenerativeAI(model="gemini-3.8-flash")

# while True:
#   query=input("User:")
#   if query.lower() in ["exit","quit","bye"]:
#     print("Good Bye, have a nice day!")
#     break
#   res=llm.invoke(query)
#   print("AI:",res.content[0]["text"])
from dotenv import load_dotenv
load_dotenv()

# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import streamlit as st

# llm = ChatGoogleGenerativeAI(model = "gemini-3.6-flash")
llm = ChatOpenAI(model = "gpt-5")

st.title("🤖 AskBuddy – AI QnA Bot")
st.markdown("My QnA Bot with LangChain and Google Gemini !")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)
    

query = st.chat_input("Ask anything ?")
if query:
    st.session_state.messages.append({"role":"user", "content":query})
    st.chat_message("user").markdown(query)
    res = llm.invoke(query)
    st.chat_message("ai").markdown(res.content)
    st.session_state.messages.append({"role":"ai", "content":res.content})