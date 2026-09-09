from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import InMemoryVectorStore
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
import streamlit as st

def process_document(path):
    
    loader=PyPDFDirectoryLoader(path)
    pdfData=loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    splittedData=splitter.split_documents(pdfData)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    vector_store=InMemoryVectorStore.from_documents(
    documents=splittedData,
    embedding=embeddings,
    )

    llm=ChatGroq(model="openai/gpt-oss-20b")
        
    @tool
    def retriever_tool(query:str):
        """
            This tool can help you to retrieve the revelant data of the Pdf documents
        """
        docs = vector_store.similarity_search(query=query,k=4)

        context=""
        for doc in docs:
            context = context + doc.page_content + "\n\n"

        return context

    system_prompt="""
    you are a helpful assistent that answers questions using retrieved context.
    ALWAYS use the 'retriever_tool' tool for questions requiring exterenal knowledge.
    """

    agent=create_agent(
        model=llm,
        tools=[retriever_tool],
        checkpointer=InMemorySaver(),
        system_prompt=system_prompt
    )
    st.session_state.agent=agent
    st.session_state.document_uploaded=True


if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
    
if "document_uploaded" not in st.session_state:
   st.session_state.document_uploaded=False

if "agent" not in st.session_state:
    st.session_state.agent=None 


if "vector_store" not in st.session_state:
    st.session_state.vector_store=None

if "messages" not in st.session_state:
    st.session_state.messages=[] 
    

if not st.session_state.document_uploaded:
    uploaded=st.file_uploader(label="Select only Pdf Document",type=["pdf"],accept_multiple_files=True)
    if uploaded:
        with st.spinner("Processing..."):
            path="./docs_files/"
            for file in uploaded:
                with open(path+file.name, "wb") as f:
                    f.write(file.getvalue())
            process_document(path)
            st.rerun()


if st.session_state.document_uploaded and st.session_state.agent:
    for msg in st.session_state.messages:
        role=msg.get("role")
        content=msg.get("content")
        st.chat_message(role).markdown(content)
        
    query=st.chat_input("Ask Anything related to uploaded document")
    if query:
        st.chat_message("user").markdown(query)
        st.session_state.messages.append({"role":"user","content":query})
        response=st.session_state.agent.invoke({"messages":[{"role":"user","content":query}]},
                                               {"configurable":{"thread_id":1}})

        ans=response["messages"][-1].content
        st.session_state.messages.append({"role":"ai","content":ans})
        st.chat_message("ai").markdown(ans)

