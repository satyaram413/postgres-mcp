import asyncio
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient

async def main():
    load_dotenv()
    
    config_file = "./config.json"
    
    print("Initializing PostgreSQL MCP client...")
    
    client = MCPClient.from_config_file(config_file)
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(model="llama3-70b-8192")
    
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=5,
        memory_enabled=True,
    )
    
    print("Fetching database schema...")
    try:
        schema_result = await agent.run("Get the database schema")
        print("Database schema loaded successfully.")
    except Exception as e:
        print(f"Error fetching schema: {e}")
    
    print("\n===== PostgreSQL Query Assistant =====")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("======================================\n")
    
    try:
        while True:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation...")
                break
                
            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue
            
            print("\nAssistant: ", end="", flush=True)
            
            try:
               
                response = await agent.run(
                    f"Convert this question to a SQL SELECT query and execute it: {user_input}"
                )
                print(response)
            except Exception as e:
                print(f"\nError: {e}")
    
    finally:
        if client and client.sessions:
            await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main())