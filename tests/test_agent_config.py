"""Tests for agent configuration — no API calls made."""


class TestModel:
    def test_all_agents_use_gemma4(self, agents):
        for agent_obj in [
            agents.billing_agent,
            agents.tech_agent,
            agents.general_agent,
            agents.root_agent,
        ]:
            assert agent_obj.model == "gemma-4-31b-it"

    def test_model_constant_matches_agents(self, agents):
        assert agents.GEMMA_MODEL == "gemma-4-31b-it"


class TestAgentNames:
    def test_billing_agent_name(self, agents):
        assert agents.billing_agent.name == "billing_agent"

    def test_tech_agent_name(self, agents):
        assert agents.tech_agent.name == "tech_agent"

    def test_general_agent_name(self, agents):
        assert agents.general_agent.name == "general_agent"

    def test_root_agent_name(self, agents):
        assert agents.root_agent.name == "triage_agent"


class TestDescriptions:
    def test_billing_agent_description_mentions_billing(self, agents):
        assert "billing" in agents.billing_agent.description.lower()

    def test_tech_agent_description_mentions_technical(self, agents):
        desc = agents.tech_agent.description.lower()
        assert "technical" in desc or "bug" in desc or "api" in desc

    def test_general_agent_description_mentions_general(self, agents):
        assert "general" in agents.general_agent.description.lower()

    def test_triage_agent_description_mentions_routing(self, agents):
        desc = agents.root_agent.description.lower()
        assert "route" in desc or "triage" in desc or "specialist" in desc


class TestInstructions:
    def test_billing_instruction_covers_refunds(self, agents):
        assert "refund" in agents.billing_agent.instruction.lower()

    def test_billing_instruction_covers_subscriptions(self, agents):
        assert "subscription" in agents.billing_agent.instruction.lower()

    def test_tech_instruction_covers_bugs(self, agents):
        assert "bug" in agents.tech_agent.instruction.lower()

    def test_tech_instruction_covers_api(self, agents):
        assert "api" in agents.tech_agent.instruction.lower()

    def test_general_instruction_covers_account(self, agents):
        assert "account" in agents.general_agent.instruction.lower()

    def test_triage_instruction_names_all_specialists(self, agents):
        instruction = agents.root_agent.instruction
        assert "billing_agent" in instruction
        assert "tech_agent" in instruction
        assert "general_agent" in instruction

    def test_triage_instruction_delegates_not_resolves(self, agents):
        instruction = agents.root_agent.instruction.lower()
        assert "transfer" in instruction or "delegate" in instruction or "route" in instruction


class TestSubAgents:
    def test_root_agent_has_three_sub_agents(self, agents):
        assert len(agents.root_agent.sub_agents) == 3

    def test_root_agent_sub_agents_are_correct(self, agents):
        sub_names = {a.name for a in agents.root_agent.sub_agents}
        assert sub_names == {"billing_agent", "tech_agent", "general_agent"}

    def test_specialist_agents_have_no_sub_agents(self, agents):
        for specialist in [agents.billing_agent, agents.tech_agent, agents.general_agent]:
            assert specialist.sub_agents == [], f"{specialist.name} should not have sub_agents"
