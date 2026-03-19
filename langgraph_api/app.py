from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Load environment variables
load_dotenv()

# ==============================
# 1. STATE (Memory)
# ==============================
class State(TypedDict):
    messages: Annotated[list, add_messages]

# ==============================
# 2. TOOLS
# ==============================
@tool
def add(a: float, b: float) -> float:
    """Adds two numbers together."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divides number 'a' by number 'b'. Returns an error if b is 0."""
    if b == 0:
        return "Error: Division by zero is not allowed."
    return a / b

tools = [add, multiply, divide]

# ==============================
# 3. LLM
# ==============================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

llm_with_tools = llm.bind_tools(tools)

# ==============================
# 4. ROUTER (START)
# ==============================
def router(state: State):
    latest_message = state["messages"][-1].content.lower()

    if "hi" in latest_message or "hello" in latest_message:
        return "hi"

    return "chatbot"

# ==============================
# 5. NODES
# ==============================
def chatbot_node(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools=tools)

def hi_node(state: State):
    return {
        "messages": [
            ("ai", "Hello! How can I assist you today? \n This is the HI_NODE")
        ]
    }

# ==============================
# 6. BUILD GRAPH
# ==============================
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("Hi_Node", hi_node)

# 🚀 START → Router
graph_builder.add_conditional_edges(
    START,
    router,
    {
        "hi": "Hi_Node",
        "chatbot": "chatbot"
    }
)

# 🤖 chatbot → tools OR end
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)

# 🔁 Back connections
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("Hi_Node", END)

graph = graph_builder.compile()

# ==============================
# 7. TERMINAL APP
# ==============================
if __name__ == "__main__":
    print("🤖 AI Agent Started (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        events = graph.stream(
            {"messages": [("user", user_input)]},
            stream_mode="values"
        )

        for event in events:
            latest_message = event["messages"][-1]

            if latest_message.type == "ai" and not latest_message.tool_calls:
                print("Bot:", latest_message.content)