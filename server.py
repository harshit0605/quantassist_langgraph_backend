import os
from fastapi import FastAPI
import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint 
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent 
import certifi

from dotenv import load_dotenv
load_dotenv()

# Set the SSL certificate path before any API clients are initialized
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from stock_market_agent.stock_agent  import workflow 
app = FastAPI()


sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="stock_agent", # the name of your agent defined in langgraph.json
            description="Agent helps perform in-depth research and analysis on the stock  using techincal and fundamental analysis",
            graph=workflow, # the graph object from your langgraph import
        )
    ],
)
 
# Use CopilotKit's FastAPI integration to add a new endpoint for your LangGraph agents
add_fastapi_endpoint(app, sdk, "/copilotkit", use_thread_pool=False)
 
# add new route for health check
@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}
 
def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )

if __name__ == '__main__':
    main()