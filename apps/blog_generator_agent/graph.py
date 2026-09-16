from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from state import BlogState
from agents import get_llm, researcher_agent,writer_agent,final_agent
from typing import Literal


MAX_REVISION=3

# defining nodes
def researcher_node(state:BlogState):
    """Research agent generates (or revises) the research outline"""
    llm=get_llm()
    researchData=researcher_agent(
        llm=llm,
        topic=state.topic,
        audience=state.audience,
        feedback=state.research_feedback
    )
    state.research=researchData
    state.research_feedback=""
    return state

def human_review_research_node(state:BlogState):
    """Pause and Ask human to approve the research send the feedback"""
    decision=interrupt({
        "stage":"researcher_review",
        "research":state.research,
        "instructions":(
            "Reply with 'approve' to continue to writing, " "or describe what to change to send it back to the researcher."
        )
    })
 
    if isinstance(decision, dict): # check if decision is a dictionary or not
        action = decision.get("action", "approve") #if action keyword is not in dect then is will considered as 'approve'
        feedback = decision.get("feedback", "") #if feedback is not present in dect then it will considered as empty feedback
    else:
        text = str(decision) #is decision is not a dict means it is a string or text 
        action = "approve" if text.lower() in ["approve", "approved", "ok", "yes", "process", ""] else "revise"
        feedback ="" if  action=="approve" else text 

    state.research_feedback=feedback
    return state

    # writer node
def writer_node(state:BlogState):
    """Writer agent produce the full draft blog (or revises it)"""
    llm=get_llm()
    researchDraftData=writer_agent(
        llm=llm,
        topic=state.topic,
        audience=state.audience,
        research=state.research,
        feedback=state.research_feedback_draft
    )
    if state.research_feedback_draft:      # <-- add this block
        state.rivision_count += 1

    state.research_draft=researchDraftData
    state.research_feedback_draft =""
    return state

# 

def human_review_draft_node(state:BlogState):
    """Pause and Ask human to approve the draft send the feedback"""
    decision=interrupt({
        "stage":"draft_review",
        "research_draft":state.research_draft,
        "instructions":(
            "Reply with 'approve' to continue to send the editor","or describe what to change to send it back to the writer." 
        )
    })
 
    if isinstance(decision, dict): # check if decision is a dictionary or not
        action = decision.get("action", "approve") #if action keyword is not in dect then is will considered as 'approve'
        feedback = decision.get("feedback", "") #if feedback is not present in dect then it will considered as empty feedback
    else:
        text = str(decision) #is decision is not a dict means it is a string or text 
        action = "approve" if text.lower() in ["approve", "approved", "ok", "yes", "process", ""] else "revise"
        feedback ="" if  action=="approve" else text 

    state.research_feedback_draft=feedback
    return state


def final_blog_node(state:BlogState):
    llm=get_llm()
    final=final_agent(
        llm=llm,
        topic=state.topic,
        research_draft=state.research_draft
    )
    state.final_blog=final
    return state

# conditional edges 
def route_after_research_agent(state:BlogState)->Literal["researcher_agent","writer_agent"]:
    if state.research_feedback:
        return "researcher_agent"
    else :
        return "writer_agent"

def route_after_writer_agent(state:BlogState)->Literal["writer_agent","final_agent"]:
   if state.research_feedback_draft and state.rivision_count < MAX_REVISION:
       return "writer_agent"
   else:
       return "final_agent"

#    Build and compile the graph 
def build_blog_graph():
    graph=StateGraph(BlogState)
    # add nodes
    graph.add_node("researcher_agent",researcher_node)
    graph.add_node("human_review_research", human_review_research_node)
    graph.add_node("writer_agent", writer_node)
    graph.add_node("human_review_draft", human_review_draft_node)
    graph.add_node("final_agent",final_blog_node)
# add edges 

    graph.add_edge(START,"researcher_agent")
    graph.add_edge("researcher_agent","human_review_research")
    graph.add_conditional_edges(
        "human_review_research",
        route_after_research_agent,
        {
            "researcher_agent": "researcher_agent",
            "writer_agent": "writer_agent",
        },
    )
    graph.add_edge("writer_agent","human_review_draft")

    graph.add_conditional_edges(
        "human_review_draft",
        route_after_writer_agent,
        {
            "writer_agent": "writer_agent",
            "final_agent": "final_agent",
        },
    )

    graph.add_edge("final_agent",END)
    checkpointer = InMemorySaver() 
    return graph.compile(checkpointer=checkpointer) 
    
