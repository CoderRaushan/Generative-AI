from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from  langgraph.types import Interrupt, Command
from state import BlogState
from agents import get_llm, researcher_agent,writer_agent,final_agent


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
    decision=Interrupt({
        "stage":"researcher_review",
        "research":state.research,
        "instructions":(
            "Reply with 'approve' to continue to writing","or describe what to change to send it back to the researcher."
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
    state.research=researchDraftData
    state.research_feedback_draft=""
    return state