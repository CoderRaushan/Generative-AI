from dotenv import load_dotenv
load_dotenv()

from langchain_community.utilities import GoogleSerperAPIWrapper 
from langchain_groq import ChatGroq 
from langchain.agents import create_agent 
from langgraph.checkpoint.memory import InMemorySaver  

llm=ChatGroq(model="openai/gpt-oss-20b")

search=GoogleSerperAPIWrapper()

agent = create_agent(
    model=llm,
    tools=[search.run],
    system_prompt="you are an agent and can search for any question on google",
    checkpointer=InMemorySaver(),
)

while True:
    query=input("User:")
    if query.lower()=="quit":
      print("Bye")
      break
    res=agent.invoke(
        {"messages":[{"role":"user","content":query}]},
        {"configurable": {"thread_id": "1"}}
       ) 
    print("AI:",res["messages"][-1].content)
