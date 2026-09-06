from dotenv import load_dotenv
load_dotenv()

### db,  llm, tools, create_agent, system_prompt
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import streamlit as st


db = SQLDatabase.from_uri("mysql+pymysql://root:1230@localhost:3306/my_tasks")


## llm, tools, memory, system_prompt
model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    reasoning_effort="low",
)
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

system_prompt = """
You are a task management assistant.

You have access to SQL database tools for managing tasks.

The tasks table has:
- id
- title
- description
- status
- created_at

Allowed operations:
- Create tasks
- Read tasks
- Update tasks
- Delete tasks

Rules:
- Always use the SQL tools when the user asks about tasks.
- For SELECT queries, return at most 10 rows.
- Order task lists by created_at DESC.
- After INSERT, UPDATE, or DELETE, verify the operation using a SELECT query.
- Never invent database results.
- When listing tasks, present them clearly as a Markdown table.
"""


@st.cache_resource
def get_agent():
    agent = create_agent(
        model=model,
        tools=tools,
        checkpointer=InMemorySaver(),
        system_prompt=system_prompt
    )
    return agent

agent = get_agent()


st.subheader("📜 TaskBot - Manage Your Tasks")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])


prompt = st.chat_input("Ask me to manage your tasks ?")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user", "content":prompt})

    with st.chat_message("ai"):
        with st.spinner("Processing..."):
            response = agent.invoke(
                    {"messages":[{"role":"user", "content":prompt}]},
                    {"configurable":{"thread_id":"1"}}
                )
            result = response["messages"][-1].content
            st.markdown(result)
            st.session_state.messages.append({"role":"ai", "content":result})





