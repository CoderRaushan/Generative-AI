from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated


class ChatState(BaseModel):
    messages:Annotated[list,add_messages]


llm=ChatGroq(model="openai/gpt-oss-20b")

def chatBotNode(state:ChatState):
    res=llm.invoke(state.messages)
    state.messages=[res]
    return state

memory=InMemorySaver()

graph=StateGraph(ChatState)
graph.add_node("ChatBot",chatBotNode)

graph.add_edge(START,"ChatBot")
graph.add_edge("ChatBot", END)

graph=graph.compile(checkpointer=memory)

while True:
   query=input("user: ")
   if query.lower() in ["exit","quit"]:
       print("Good bye")
       break
   res=graph.invoke({"messages":[{"role":"user","content":query}]},
                 {"configurable":{"thread_id":"1"}})

   print(res["messages"][-1].content)

