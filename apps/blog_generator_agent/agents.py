import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def get_llm(model:str="openai/gpt-oss-20b", temperature:float=0.5):
    return ChatGroq(model=model, temperature=temperature)


RESEARCH_PROMPT=ChatPromptTemplate.from_messages([
    {"role":"system","content":"""
        you are a Research agent. Given a blog topic and target audience, produce a clear,
        "structured research outline. Includes\n"
        "1. 5 - 7 key points the blog should cover \n"
        "2. Important facts, stats, or exmples for each point\n"
        "3. Suggested angle or hook\n"
        "4. Be concise. Use bullet points. Do Not write the full blog yet. 
    """},
    {"role":"user","content":"Topic:{topic}, Audience:{audience}, {revision_hits}, Write the research outline now. "}
]) 

# Researcher Agent
def researcher_agent(llm:ChatGroq,topic:str,audience:str,feedback:str)-> str:
    revision_hits=f"The human provided this feedback on your previous research - please address it:{feedback}"

    if not feedback:
        revision_hits="This is your first attempt"
    chain=RESEARCH_PROMPT | llm
    result=chain.invoke({
        "topic":topic,
        "audience":audience,
        "revision_hits":revision_hits,
    })
    return result.content

# Writter Agent
WRITER_PROMPT=ChatPromptTemplate.from_messages([
    {"role":"system","content":"""
        you are a Blog Writer agent. Using the research notes provided, write a complete engaging blog post.
        "Rules:\n"
        "- Length:500-800 words \n"
        "- Structure: catchy title, intro hook, 3-5 sections with H2 headings, conclusion \n"
        "- Toned clear, friendly, suited to the target audience\n"
        "- Use markdown formatting\n"
        "- Do NOT add a 'word count' line at the end"
    """},
    {"role" : "user","content":"""
        Topic: {topic},
        Audience: {audience},
        Research Notes: {research}
        {revision_hits}
        write the full blog post now.
"""
}]) 

def writer_agent(llm:ChatGroq,topic:str,audience:str,research:str,feedback:str)-> str:
    revision_hits=f"The human provided this feedback on your previous draft and asked for these changes:{feedback} please apply these changes during writting the blog."

    if not feedback:
        revision_hits="This is your first attempt"
    chain=WRITER_PROMPT | llm
    print(revision_hits)
    result=chain.invoke({
        "topic":topic,
        "audience":audience,
        "research":research,
        "revision_hits":revision_hits,
    })
    return result.content
  
# Final blog Editior agent
FINAL_PROMPT=ChatPromptTemplate.from_messages([
    {"role":"system","content":"""
    "You are an Editor Agent — the final quality gate before publishing. \n"
    "Take the draft and produce the FINAL polished version. Specifically:\n"
    "- Fix grammar, spelling, and awkward phrasing\n"
    "- Tighten wordy sentences\n"
    "- Improve flow and transitions between sections\n"
    "- Make the titte and intro more compelling if needed \n"
    "- Keep the same structure and markdown formatting\n"
    "- Blog Wordings should look like human, not a AI, and don't use any speciat chars and complex / fancy words.\n"
    "Output only the final polished blog post - no commentary."
    """},
    {"role" : "user","content":"""
        Topic: {topic},
        research_draft:{research_draft}
  
        return the published blog post.
"""
}]) 


def final_agent(llm:ChatGroq,topic:str,research_draft:str)-> str:

    chain= FINAL_PROMPT | llm
    result=chain.invoke({
        "topic":topic,
        "research_draft":research_draft
    })
    return result.content