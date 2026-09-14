from pydantic import BaseModel

class BlogState(BaseModel):
    # user  input 
    topic:str=""
    audience:str=""
    # research op
    research:str=""
    research_feedback:str=""
    # writer 
    research_draft:str=""
    research_feedback_draft:str=""
    # editor
    final_blog:str=""
    # metadata
    rivision_count:int=0


