# fashion_agent/agent.py
# This file will contain the main logic for the AI agent.

import google.generativeai as genai
from google.generativeai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

# Replace with your actual Gemini API key
GEMINI_API_KEY = "AIzaSyC2pgSkdovwkpQgBLuWTpb-JMruxXXJIeM"
APP_NAME="google_search_agent"
USER_ID="user1234"
SESSION_ID="1234"
# Session and Runner


genai.configure(api_key=GEMINI_API_KEY)

# def create_item_description(item_description: str) -> dict:
#  """Evaluates a fashion store item using Gemini."""
#  response = genai.generate_text(
#      model="models/text-bison-001",
#      prompt=f"Evaluate the style and trendiness of the following item description: {item_description}",
#      temperature=0.5
#  )
#  return response

root_agent = Agent(
    model="gemini-2.0-flash",
    name="fashion_agent",
    
    
    description="Evaluates fashion store items using Gemini.",
    instruction="""You are a fashion agent that helps the user to find suiting items.
When a user provides an item description, you should:
1. Use the google search tool to find similar items.
2. output the style and trendiness of the items.
3. output images of the items.
4. output market prices of the items.
5. if the user asks for reviews, output reviews of the items.
6. if the user asks for recommendations, output recommendations of similar items.
7. if the user decides to buy the item, output give market trends of the items.
""",
    tools=[google_search],
    generate_content_config=types.GenerationConfig(
        temperature=0.5,
        max_output_tokens=250,
    )
)
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
# Agent Interaction (Async)
async def call_agent_async(query):
    content = types.ContentType(role='user', parts=[types.Part(text=query)])
    print(f"\n--- Running Query: {query} ---")
    final_response_text = "No final text response captured."
    try:
        # Use run_async
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            print(f"Event ID: {event.id}, Author: {event.author}")

            # --- Check for specific parts FIRST ---
            has_specific_part = False
            if event.content and event.content.parts:
                for part in event.content.parts: # Iterate through all parts
                    if part.executable_code:
                        # Access the actual code string via .code
                        print(f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```")
                        has_specific_part = True
                    elif part.code_execution_result:
                        # Access outcome and output correctly
                        print(f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}")
                        has_specific_part = True
                    # Also print any text parts found in any event for debugging
                    elif part.text and not part.text.isspace():
                        print(f"  Text: '{part.text.strip()}'")
                        # Do not set has_specific_part=True here, as we want the final response logic below

            # --- Check for final response AFTER specific parts ---
            # Only consider it final if it doesn't have the specific code parts we just handled
            if not has_specific_part and event.is_final_response():
                if event.content and event.content.parts and event.content.parts[0].text:
                    final_response_text = event.content.parts[0].text.strip()
                    print(f"==> Final Agent Response: {final_response_text}")
                else:
                    print("==> Final Agent Response: [No text content in final event]")


    except Exception as e:
        print(f"ERROR during agent run: {e}")
    print("-" * 30)

async def main():
    await call_agent_async("What is a t-shirt?")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    