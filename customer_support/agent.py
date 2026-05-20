from dotenv import load_dotenv
from google.adk.agents import Agent
from customer_support.config import GEMMA_MODEL
from customer_support.sub_agents.billing_agent.agent import billing_agent
from customer_support.sub_agents.tech_agent.agent import tech_agent
from customer_support.sub_agents.general_agent.agent import general_agent

load_dotenv()

root_agent = Agent(
    name="triage_agent",
    model=GEMMA_MODEL,
    description="Front-line triage agent that greets customers and routes them to the right specialist.",
    instruction="""You are the first point of contact for TechCorp customer support.

Your responsibilities:
1. Greet the customer warmly and ask how you can help.
2. Listen to their issue and identify the correct specialist:
   - billing_agent  → payment, invoices, subscriptions, refunds, pricing
   - tech_agent     → bugs, errors, installation, API, troubleshooting
   - general_agent  → account access, policies, feedback, everything else
3. Transfer to the appropriate agent — do NOT try to resolve issues yourself.

Always be polite and make the handoff feel seamless for the customer.""",
    sub_agents=[billing_agent, tech_agent, general_agent],
)
