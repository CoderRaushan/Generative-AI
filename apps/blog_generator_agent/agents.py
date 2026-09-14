import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def get_llm(model:str="openai/gpt-oss-20b", temperature:float=0.5):
    return ChatGroq(model=model, temperature=temperature)


RESEARCH_PROMPT=ChatPromptTemplate.from_messages([
    {"role":"system","content":"""
        you are a Research agent. Given a blog topic and target audience, produce a clear,
        structured research outline. Include 
        1. 5 - 7 key points the blog should cover
        2. Important facts, stats, or exmples for each point
        3. Suggested angle or hook
        4. Be concise. Use bullet points. Do Not write the full blog yet. 
    """},
    {"role":"user","content":"Topic:{topic}, Audience:{audience}"}
])