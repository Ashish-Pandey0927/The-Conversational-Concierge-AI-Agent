import os
import operator
from typing import TypedDict, Annotated, List

from dotenv import load_dotenv
import gradio as gr

load_dotenv()
required_keys = ["GOOGLE_API_KEY", "TAVILY_API_KEY", "OPENWEATHERMAP_API_KEY"]
if not all(os.getenv(key) for key in required_keys):
    raise ValueError(
        "Missing one or more required API keys. "
        "Please check your .env file for: "
        "GOOGLE_API_KEY, TAVILY_API_KEY, OPENWEATHERMAP_API_KEY"
    )


from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_tavily import TavilySearch
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_community.embeddings import HuggingFaceEmbeddings


from tools.weather import get_weather


print("Setting up RAG pipeline...")
loader = TextLoader("data/wine_business_info.md")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
print("RAG pipeline ready.")


print("Defining tools...")
retriever_tool = create_retriever_tool(
    retriever,
    "search_wine_business_info",
    "Searches and returns information about the Celestial Vines Estate winery. Use for questions about their history, wines, tours, hours, or location.",
)
tavily_tool = TavilySearch(max_results=3)
weather_tool = get_weather
tools = [retriever_tool, tavily_tool, weather_tool]
print("Tools defined.")


print("Defining LangGraph agent...")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

def call_model(state: AgentState):
    """Invokes the LLM with the current message history."""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)  # <-- Fix variable name here
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Determines whether to call a tool or end the graph."""
    last_message = state['messages'][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "action"
    return END


workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
tool_node = ToolNode(tools)
workflow.add_node("action", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent", should_continue, {"action": "action", END: END}
)
workflow.add_edge("action", "agent")
app = workflow.compile()
print("LangGraph agent compiled and ready.")



# This function contains the corrected logic for displaying the agent's response.
def run_agent(message, history):
    """Processes user input and streams the agent's response."""
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        if ai:
            history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))

    try:
        stream = app.stream({"messages": history_langchain_format})
        
        # This simplified loop correctly finds and yields the final answer
        final_answer = ""
        for chunk in stream:
            if "agent" in chunk:
                response_message = chunk["agent"]["messages"][-1]
                if isinstance(response_message, AIMessage) and response_message.content:
                    final_answer = response_message.content
        
        yield final_answer

    except Exception as e:
        print(f"An error occurred: {e}")
        yield "Sorry, an error occurred. Please check the server logs or try again."


print("Launching Gradio UI...")
gr.ChatInterface(
    run_agent,
    title="🍷 Conversational Concierge for Celestial Vines Estate (Powered by Gemini)",
    description="Ask me about the winery, search the web, or get the current weather.",
    examples=[
        "Tell me about your Cabernet Sauvignon.",
        "What are your tasting room hours?",
        "What is the weather like in Napa today?",
        "Who was the 16th president of the United States?"
    ],
    theme="soft",
    type="messages",
).launch()
system_prompt = (
    "You are a helpful, friendly assistant for Celestial Vines Estate. "
    "You can answer questions about the winery, search the web, provide weather updates, "
    "and also engage in general conversation. If the user greets you or asks a general question, "
    "respond warmly and conversationally."
)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
llm_with_tools = llm.bind_tools(tools, system_prompt=system_prompt)