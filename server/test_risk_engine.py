"""
Unit tests for the Risk Engine (Confidence-Gated Autonomy).

Run with:
    python -m pytest test_risk_engine.py -v
"""

import pytest
from risk_engine import (
    assess_risk,
    store_pending_action,
    get_pending_action,
    remove_pending_action,
    list_pending_actions,
    clear_all_pending_actions,
    RiskLevel,
    AutonomyLevel,
)


# =============================================================================
# assess_risk — action type policies
# =============================================================================

class TestAssessRiskReadActions:
    """Read-only actions should always be LOW / AUTO_EXECUTE."""

    def test_read_events_is_low(self):
        result = assess_risk("read_events")
        assert result["risk_level"] == "LOW"
        assert result["autonomy_level"] == "AUTO_EXECUTE"
        assert result["requires_confirmation"] is False

    def test_find_free_slot_is_low(self):
        result = assess_risk("find_free_slot")
        assert result["risk_level"] == "LOW"
        assert result["requires_confirmation"] is False

    def test_check_conflicts_is_low(self):
        result = assess_risk("check_conflicts")
        assert result["risk_level"] == "LOW"
        assert result["requires_confirmation"] is False


class TestAssessRiskCreateEvent:
    def test_create_event_base_is_medium(self):
        result = assess_risk("create_event")
        assert result["risk_level"] == "MEDIUM"
        assert result["autonomy_level"] == "CONFIRM_FIRST"
        assert result["requires_confirmation"] is True

    def test_create_event_with_conflict_elevates_to_high(self):
        result = assess_risk("create_event", conflict_detected=True)
        assert result["risk_level"] == "HIGH"
        assert result["autonomy_level"] == "ALWAYS_ASK"
        assert result["requires_confirmation"] is True

    def test_create_event_no_conflict_stays_medium(self):
        result = assess_risk("create_event", conflict_detected=False)
        assert result["risk_level"] == "MEDIUM"


class TestAssessRiskDeleteEvent:
    def test_delete_event_is_always_high(self):
        result = assess_risk("delete_event")
        assert result["risk_level"] == "HIGH"
        assert result["autonomy_level"] == "ALWAYS_ASK"
        assert result["requires_confirmation"] is True

    def test_delete_event_stays_high_regardless(self):
        result = assess_risk("delete_event", conflict_detected=False)
        assert result["risk_level"] == "HIGH"


class TestAssessRiskUpdateEvent:
    def test_update_event_base_is_medium(self):
        result = assess_risk("update_event")
        assert result["risk_level"] == "MEDIUM"
        assert result["autonomy_level"] == "CONFIRM_FIRST"
        assert result["requires_confirmation"] is True

    def test_update_event_with_time_change_elevates_to_high(self):
        result = assess_risk("update_event", time_change=True)
        assert result["risk_level"] == "HIGH"
        assert result["autonomy_level"] == "ALWAYS_ASK"

    def test_update_event_without_time_change_stays_medium(self):
        result = assess_risk("update_event", time_change=False)
        assert result["risk_level"] == "MEDIUM"


class TestAssessRiskMultipleEvents:
    def test_multiple_events_elevates_to_high(self):
        result = assess_risk("create_event", number_of_affected_events=3)
        assert result["risk_level"] == "HIGH"
        assert result["conditions"]["elevated"] is True

    def test_single_event_stays_at_base(self):
        result = assess_risk("create_event", number_of_affected_events=1)
        assert result["risk_level"] == "MEDIUM"


class TestAssessRiskUnknownAction:
    def test_unknown_action_defaults_to_high(self):
        result = assess_risk("launch_missiles")
        assert result["risk_level"] == "HIGH"
        assert result["autonomy_level"] == "ALWAYS_ASK"
        assert result["requires_confirmation"] is True
        assert "Unknown" in result["reason"]


# =============================================================================
# assess_risk — output format
# =============================================================================

class TestAssessRiskOutputFormat:
    def test_has_required_keys(self):
        result = assess_risk("create_event")
        required_keys = [
            "action_type", "risk_level", "autonomy_level",
            "requires_confirmation", "reason", "conditions"
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_reason_is_nonempty_string(self):
        result = assess_risk("delete_event")
        assert isinstance(result["reason"], str)
        assert len(result["reason"]) > 10


# =============================================================================
# Pending action store
# =============================================================================

class TestPendingActionStore:
    def setup_method(self):
        clear_all_pending_actions()

    def test_store_and_retrieve(self):
        action_id = store_pending_action(
            action_type="create_event",
            action_args={"summary": "Test Event"},
            risk_assessment={"risk_level": "MEDIUM"},
            description="Create 'Test Event'",
        )
        action = get_pending_action(action_id)
        assert action is not None
        assert action["action_type"] == "create_event"
        assert action["action_args"]["summary"] == "Test Event"
        assert action["status"] == "pending"

    def test_remove_pending_action(self):
        action_id = store_pending_action(
            action_type="delete_event",
            action_args={"event_id": "abc123"},
            risk_assessment={"risk_level": "HIGH"},
            description="Delete event",
        )
        removed = remove_pending_action(action_id)
        assert removed is not None
        assert removed["action_id"] == action_id

        # Should be gone now
        assert get_pending_action(action_id) is None

    def test_remove_nonexistent_returns_none(self):
        assert remove_pending_action("does-not-exist") is None

    def test_list_pending_actions(self):
        store_pending_action("create_event", {}, {}, "A")
        store_pending_action("delete_event", {}, {}, "B")
        actions = list_pending_actions()
        assert len(actions) == 2

    def test_clear_all(self):
        store_pending_action("create_event", {}, {}, "A")
        store_pending_action("delete_event", {}, {}, "B")
        clear_all_pending_actions()
        assert len(list_pending_actions()) == 0

    def test_action_id_is_short(self):
        action_id = store_pending_action("create_event", {}, {}, "Test")
        assert len(action_id) == 8

    def test_get_nonexistent_returns_none(self):
        assert get_pending_action("nonexistent") is None
