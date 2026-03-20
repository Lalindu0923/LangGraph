# run_terminal.py

import asyncio
from langgraph_api.graph_setup import graph

async def main():
    print("🤖 AI Agent Started ❤️ (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        events = graph.astream(
            {"messages": [("user", user_input)]},
            stream_mode="values"
        )

        async for event in events:
            latest = event["messages"][-1]

            if latest.type == "ai" and not latest.tool_calls:
                print("Bot:", latest.content)


if __name__ == "__main__":
    asyncio.run(main())