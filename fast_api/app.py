from fastapi import FastAPI
from langgraph_api.app import graph, State  # import compiled graph and State

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(user_input: str):
    state = {"messages": [("user", user_input)]}
    last_ai_message = None
    
    async for event in graph.stream(state, stream_mode="values"):
        latest_message = event["messages"][-1]
        if latest_message.type == "ai":
            last_ai_message = latest_message.content

    return {"response": last_ai_message}