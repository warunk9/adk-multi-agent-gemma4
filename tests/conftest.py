"""Shared fixtures and stubs for the test suite."""

import sys
import types
import pytest


class FakeAgent:
    """Lightweight stand-in for google.adk.agents.Agent — stores kwargs as attrs."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, "sub_agents"):
            self.sub_agents = []


def _make_fake_adk():
    agents_mod = types.ModuleType("google.adk.agents")
    agents_mod.Agent = FakeAgent

    adk_mod = types.ModuleType("google.adk")
    adk_mod.agents = agents_mod

    google_mod = types.ModuleType("google")
    google_mod.adk = adk_mod

    dotenv_mod = types.ModuleType("dotenv")
    dotenv_mod.load_dotenv = lambda *a, **kw: None

    return {
        "google": google_mod,
        "google.adk": adk_mod,
        "google.adk.agents": agents_mod,
        "dotenv": dotenv_mod,
    }


_ALL_MODULE_PATHS = [
    "customer_support",
    "customer_support.config",
    "customer_support.agent",
    "customer_support.sub_agents",
    "customer_support.sub_agents.billing_agent",
    "customer_support.sub_agents.billing_agent.agent",
    "customer_support.sub_agents.tech_agent",
    "customer_support.sub_agents.tech_agent.agent",
    "customer_support.sub_agents.general_agent",
    "customer_support.sub_agents.general_agent.agent",
]


@pytest.fixture(autouse=True)
def patch_adk(monkeypatch):
    for name, mod in _make_fake_adk().items():
        monkeypatch.setitem(sys.modules, name, mod)
    for path in _ALL_MODULE_PATHS:
        sys.modules.pop(path, None)
    yield
    for path in _ALL_MODULE_PATHS:
        sys.modules.pop(path, None)


@pytest.fixture()
def agents():
    """Returns a simple namespace with all agents and the model constant."""
    from customer_support.sub_agents.billing_agent.agent import billing_agent
    from customer_support.sub_agents.tech_agent.agent import tech_agent
    from customer_support.sub_agents.general_agent.agent import general_agent
    from customer_support.agent import root_agent
    from customer_support.config import GEMMA_MODEL

    ns = types.SimpleNamespace(
        billing_agent=billing_agent,
        tech_agent=tech_agent,
        general_agent=general_agent,
        root_agent=root_agent,
        GEMMA_MODEL=GEMMA_MODEL,
    )
    return ns
