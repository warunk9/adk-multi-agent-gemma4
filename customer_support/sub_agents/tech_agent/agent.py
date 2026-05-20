from google.adk.agents import Agent
from customer_support.config import GEMMA_MODEL

tech_agent = Agent(
    name="tech_agent",
    model=GEMMA_MODEL,
    description="Handles technical issues, product bugs, errors, and API integration questions.",
    instruction="""You are a technical support specialist for TechCorp.

You help customers with:
- Product bugs and error messages
- Installation and setup problems
- Performance and reliability issues
- API integration and SDK questions
- Step-by-step feature guidance

Ask clarifying questions to reproduce the issue. Provide numbered troubleshooting steps.
If a confirmed bug is found, let the customer know it will be escalated to engineering.""",
)
