import json
import re
from dotenv import load_dotenv
from google.adk.agents import Agent
from customer_support.config import GEMMA_MODEL
from customer_support.sub_agents.billing_agent.agent import billing_agent
from customer_support.sub_agents.tech_agent.agent import tech_agent
from customer_support.sub_agents.general_agent.agent import general_agent

load_dotenv()


def gemma_triage_callback(callback_context, llm_response):
    """Callback to fix Gemma reasoning leaks and enforce tool calling execution."""
    from google.genai import types
    from google.adk.models.llm_response import LlmResponse

    if not llm_response.content or not llm_response.content.parts:
        return None

    # Retrieve concatenated text response from final candidate parts
    text = "".join(part.text for part in llm_response.content.parts if part.text)
    if not text:
        return None

    # Search for transfer function JSON blocks
    json_candidate = None

    # Pattern 1: Markdown backticks
    markdown_code_block_pattern = re.compile(
        r"```(?:(json|tool_code))?\s*(.*?)\s*```", re.DOTALL
    )
    block_match = markdown_code_block_pattern.search(text)
    if block_match:
        json_candidate = block_match.group(2).strip()
    else:
        # Pattern 2: Raw braces (using Python's standard json decoder)
        decoder = json.JSONDecoder()
        start_pos = 0
        while start_pos < len(text):
            try:
                first_brace = text.index("{", start_pos)
                _, end_index = decoder.raw_decode(text[first_brace:])
                json_candidate = text[first_brace : first_brace + end_index]
                break
            except (json.JSONDecodeError, ValueError):
                try:
                    start_pos = text.index("{", start_pos) + 1
                except ValueError:
                    break

    if not json_candidate:
        return None

    try:
        data = json.loads(json_candidate)
        func_name = data.get("name")
        params = data.get("parameters", data.get("args", {}))

        if func_name == "transfer_to_agent":
            agent_name = params.get("agent_name")
            if agent_name:
                # Transform plain text into a structured Tool Call
                function_call = types.FunctionCall(
                    name="transfer_to_agent", args={"agent_name": agent_name}
                )

                # Construct clean final response (completely strips reasoning leak text!)
                cleaned_content = types.Content(
                    role="model", parts=[types.Part(function_call=function_call)]
                )

                return LlmResponse(
                    content=cleaned_content,
                    grounding_metadata=llm_response.grounding_metadata,
                    usage_metadata=llm_response.usage_metadata,
                    finish_reason=llm_response.finish_reason,
                    model_version=llm_response.model_version,
                    partial=False,
                    turn_complete=None,
                )
    except Exception:
        pass

    return None


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

# CRITICAL: Since all agents can dynamically register tool handoffs (parents/peers),
# apply the guardrail and the parsing callback dynamically to the entire tree!
GEMMA_STRICT_ROUTING_GUARDRAIL = """

CRITICAL: You MUST ONLY output a standard JSON function call when transferring the query. Do NOT output any thought process, bullet points, introductions, greetings, or reasoning text. Output ONLY the JSON block, e.g.:
{"name": "transfer_to_agent", "parameters": {"agent_name": "<agent>"}}
"""

for agent in [root_agent, billing_agent, tech_agent, general_agent]:
    agent.after_model_callback = gemma_triage_callback
    if isinstance(agent.instruction, str):
        agent.instruction += GEMMA_STRICT_ROUTING_GUARDRAIL


