from fastapi import FastAPI
from langgraph_api import graph, State  # import compiled graph and State

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(user_input: str):
    """Chat endpoint that processes user input through the LangGraph."""
    state = {"messages": [("user", user_input)]}
    last_ai_message = None

    # Use async graph streaming so async nodes (like MCP_Node) can execute.
    async for event in graph.astream(state, stream_mode="values"):
        latest_message = event["messages"][-1]
        if latest_message.type == "ai" and not latest_message.tool_calls:
            last_ai_message = latest_message.content

    return {"response": last_ai_message}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "FastAPI Chat Server Running. Use POST /chat to send messages."}