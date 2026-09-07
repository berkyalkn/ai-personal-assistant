"""
Risk Engine — Confidence-Gated Autonomy for calendar actions.

This module is entirely self-contained with ZERO LLM dependencies.
All risk assessment is deterministic, configurable, and unit-testable.

Architecture:
    Tool call → assess_risk() → AUTO_EXECUTE | CONFIRM_FIRST | ALWAYS_ASK
    If confirmation required → store_pending_action() → user approves → execute
"""

import uuid
import datetime
import json
from typing import Dict, Any, Optional, Tuple
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AutonomyLevel(str, Enum):
    AUTO_EXECUTE = "AUTO_EXECUTE"
    CONFIRM_FIRST = "CONFIRM_FIRST"
    ALWAYS_ASK = "ALWAYS_ASK"


# =============================================================================
# RISK → AUTONOMY MAPPING
# =============================================================================

RISK_TO_AUTONOMY: Dict[RiskLevel, AutonomyLevel] = {
    RiskLevel.LOW: AutonomyLevel.AUTO_EXECUTE,
    RiskLevel.MEDIUM: AutonomyLevel.CONFIRM_FIRST,
    RiskLevel.HIGH: AutonomyLevel.ALWAYS_ASK,
}


# =============================================================================
# ACTION RISK POLICIES
# =============================================================================
# Base risk level for each action type + conditions that elevate risk.

ACTION_RISK_POLICIES: Dict[str, Dict[str, Any]] = {
    "create_event": {
        "base_risk": RiskLevel.MEDIUM,
        "elevate_to_high_when": ["conflict_detected"],
        "description": "Creating a calendar event",
    },
    "delete_event": {
        "base_risk": RiskLevel.HIGH,
        "elevate_to_high_when": [],  # already HIGH
        "description": "Deleting a calendar event (irreversible)",
    },
    "update_event": {
        "base_risk": RiskLevel.MEDIUM,
        "elevate_to_high_when": ["time_change"],
        "description": "Updating a calendar event",
    },
    # Read-only actions — always LOW, included for completeness
    "read_events": {
        "base_risk": RiskLevel.LOW,
        "elevate_to_high_when": [],
        "description": "Reading calendar events",
    },
    "find_free_slot": {
        "base_risk": RiskLevel.LOW,
        "elevate_to_high_when": [],
        "description": "Finding free time slots",
    },
    "check_conflicts": {
        "base_risk": RiskLevel.LOW,
        "elevate_to_high_when": [],
        "description": "Checking for conflicts",
    },
}


# =============================================================================
# RISK REASONS (human-readable explanations)
# =============================================================================

RISK_REASONS: Dict[Tuple[str, RiskLevel], str] = {
    ("create_event", RiskLevel.MEDIUM):
        "Creating an event affects your schedule. Please confirm the details.",
    ("create_event", RiskLevel.HIGH):
        "⚠️ This event conflicts with an existing event. Please review the conflict and confirm.",
    ("delete_event", RiskLevel.HIGH):
        "🗑️ Deleting an event is irreversible. Please confirm you want to proceed.",
    ("update_event", RiskLevel.MEDIUM):
        "Updating event details. Please confirm the changes.",
    ("update_event", RiskLevel.HIGH):
        "⚠️ Rescheduling an event changes its time, which may affect other commitments. Please confirm.",
}


# =============================================================================
# PENDING ACTIONS STORE (in-memory)
# =============================================================================

_pending_actions: Dict[str, Dict[str, Any]] = {}


def store_pending_action(
    action_type: str,
    action_args: Dict[str, Any],
    risk_assessment: Dict[str, Any],
    description: str,
) -> str:
    """
    Store an action for later execution after user approval.
    Returns the action_id.
    """
    action_id = str(uuid.uuid4())[:8]  # short ID for easy reference
    _pending_actions[action_id] = {
        "action_id": action_id,
        "action_type": action_type,
        "action_args": action_args,
        "risk_assessment": risk_assessment,
        "description": description,
        "created_at": datetime.datetime.now().isoformat(),
        "status": "pending",
    }
    print(f"--- Risk Engine: Stored pending action '{action_id}' ({action_type}) ---")
    return action_id


def get_pending_action(action_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a pending action by ID."""
    return _pending_actions.get(action_id)


def remove_pending_action(action_id: str) -> Optional[Dict[str, Any]]:
    """Remove and return a pending action by ID."""
    return _pending_actions.pop(action_id, None)


def list_pending_actions() -> Dict[str, Dict[str, Any]]:
    """Return all currently pending actions."""
    return dict(_pending_actions)


def clear_all_pending_actions() -> None:
    """Clear all pending actions (used in testing)."""
    _pending_actions.clear()


# =============================================================================
# CORE RISK ASSESSMENT
# =============================================================================

def assess_risk(
    action_type: str,
    conflict_detected: bool = False,
    time_change: bool = False,
    number_of_affected_events: int = 1,
    priority_level: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Assess the risk of a calendar action and determine the autonomy level.

    Args:
        action_type: The type of action (e.g., "create_event", "delete_event").
        conflict_detected: Whether a scheduling conflict was detected.
        time_change: Whether the action involves changing event timing.
        number_of_affected_events: How many events are affected.
        priority_level: The priority level of the event (from priority engine).

    Returns:
        {
            "action_type": "create_event",
            "risk_level": "MEDIUM",
            "autonomy_level": "CONFIRM_FIRST",
            "requires_confirmation": true,
            "reason": "Creating an event affects your schedule. Please confirm.",
            "conditions": {"conflict_detected": false, "time_change": false}
        }
    """
    policy = ACTION_RISK_POLICIES.get(action_type)

    if not policy:
        # Unknown action type → treat as HIGH risk (safe default)
        return {
            "action_type": action_type,
            "risk_level": RiskLevel.HIGH.value,
            "autonomy_level": AutonomyLevel.ALWAYS_ASK.value,
            "requires_confirmation": True,
            "reason": f"Unknown action type '{action_type}'. Requiring confirmation for safety.",
            "conditions": {
                "conflict_detected": conflict_detected,
                "time_change": time_change,
            },
        }

    # Start with base risk
    risk = policy["base_risk"]

    # Check elevation conditions
    elevation_conditions = policy.get("elevate_to_high_when", [])
    elevated = False

    if "conflict_detected" in elevation_conditions and conflict_detected:
        risk = RiskLevel.HIGH
        elevated = True

    if "time_change" in elevation_conditions and time_change:
        risk = RiskLevel.HIGH
        elevated = True

    # Multiple affected events always elevates to HIGH
    if number_of_affected_events > 1 and risk != RiskLevel.HIGH:
        risk = RiskLevel.HIGH
        elevated = True

    # Map risk → autonomy
    autonomy = RISK_TO_AUTONOMY[risk]
    requires_confirmation = autonomy != AutonomyLevel.AUTO_EXECUTE

    # Build reason
    reason = RISK_REASONS.get(
        (action_type, risk),
        policy.get("description", "Action requires review.")
    )

    return {
        "action_type": action_type,
        "risk_level": risk.value,
        "autonomy_level": autonomy.value,
        "requires_confirmation": requires_confirmation,
        "reason": reason,
        "conditions": {
            "conflict_detected": conflict_detected,
            "time_change": time_change,
            "number_of_affected_events": number_of_affected_events,
            "elevated": elevated,
        },
    }
