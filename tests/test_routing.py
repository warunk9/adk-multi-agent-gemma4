"""Tests for triage routing logic — keyword-based routing via agent descriptions."""

import pytest


def classify_query(query: str, agents) -> str:
    """
    Simulates triage routing: matches query words against each specialist's
    description and instruction. Falls back to general_agent when nothing matches.
    """
    query_lower = query.lower()
    for agent in agents.root_agent.sub_agents:
        corpus = (agent.description + " " + agent.instruction).lower()
        for word in query_lower.split():
            if len(word) >= 4 and word in corpus:
                return agent.name
    return agents.general_agent.name


class TestBillingRouting:
    @pytest.mark.parametrize("query", [
        "I have a billing issue",
        "My payment failed last night",
        "I want a refund for my subscription",
        "I have a payment dispute about my invoice",
    ])
    def test_billing_queries_route_to_billing_agent(self, query, agents):
        assert classify_query(query, agents) == "billing_agent", f"Failed for: '{query}'"


class TestTechRouting:
    @pytest.mark.parametrize("query", [
        "There are bugs in the dashboard",
        "I keep getting an error from your API",
        "I am experiencing technical errors on the application",
    ])
    def test_tech_queries_route_to_tech_agent(self, query, agents):
        assert classify_query(query, agents) == "tech_agent", f"Failed for: '{query}'"


class TestGeneralRouting:
    @pytest.mark.parametrize("query", [
        "How do I reset my password",
        "I want to submit some feedback",
    ])
    def test_general_queries_route_to_general_agent(self, query, agents):
        assert classify_query(query, agents) == "general_agent", f"Failed for: '{query}'"


class TestFallback:
    def test_unknown_query_defaults_to_general_agent(self, agents):
        assert classify_query("hello there", agents) == "general_agent"

    def test_empty_query_defaults_to_general_agent(self, agents):
        assert classify_query("", agents) == "general_agent"
