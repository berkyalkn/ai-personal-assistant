"""
Priority Scoring Engine — Deterministic priority calculation for calendar events.

This module is entirely self-contained with ZERO LLM dependencies.
All scoring is deterministic, configurable, and unit-testable.
"""

import datetime
import re
from typing import Dict, List, Optional, Any, Tuple


# =============================================================================
# CONFIGURABLE SCORING WEIGHTS
# =============================================================================
# These weights control how much each factor contributes to the final score.
# They must sum to 1.0 for a normalized 0–100 output.

SCORING_WEIGHTS: Dict[str, float] = {
    "urgency": 0.30,
    "importance": 0.35,
    "deadline_proximity": 0.35,
}


# =============================================================================
# CATEGORY IMPORTANCE SCORES  (0–100 scale)
# =============================================================================
# Higher score = more important. These are the raw importance values before
# weighting is applied.

CATEGORY_IMPORTANCE: Dict[str, int] = {
    "interview":      95,
    "deadline":        90,
    "client_meeting":  85,
    "team_meeting":    60,
    "personal":        55,
    "workout":         30,
    "optional":        20,
    "unknown":         50,   # fallback for unrecognized events
}


# =============================================================================
# CATEGORY KEYWORD MAP
# =============================================================================
# Each category has a list of keywords. The first match (case-insensitive)
# against the event summary determines the category.

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "interview":      ["interview", "screening", "hiring", "recruit", "candidate"],
    "deadline":       ["deadline", "due", "submission", "final", "deliverable", "release"],
    "client_meeting": ["client", "customer", "stakeholder", "vendor", "partner", "external"],
    "team_meeting":   ["standup", "stand-up", "sync", "team", "1:1", "one-on-one",
                       "retro", "sprint", "scrum", "huddle", "all-hands"],
    "personal":       ["personal", "doctor", "dentist", "appointment", "errand",
                       "school", "pickup", "family"],
    "workout":        ["gym", "workout", "yoga", "run", "exercise", "walk",
                       "fitness", "training", "meditation"],
    "optional":       ["optional", "fyi", "info session", "social", "happy hour",
                       "lunch", "coffee chat", "catch-up"],
}


# =============================================================================
# URGENCY KEYWORDS  (boost urgency score when found in summary)
# =============================================================================

URGENCY_KEYWORDS: List[str] = [
    "urgent", "asap", "critical", "blocker", "p0", "p1",
    "emergency", "escalation", "important", "high priority",
    "must attend", "mandatory", "required",
]


# =============================================================================
# PRIORITY LEVEL THRESHOLDS
# =============================================================================

PRIORITY_THRESHOLDS: Dict[str, Tuple[int, int]] = {
    "CRITICAL": (90, 100),
    "HIGH":     (70, 89),
    "MEDIUM":   (40, 69),
    "LOW":      (0,  39),
}


# =============================================================================
# CORE SCORING FUNCTIONS
# =============================================================================

def classify_event_category(summary: str) -> str:
    """
    Classify an event into a category by keyword-matching its summary.

    Returns the first matching category key, or 'unknown' if no match.
    Pure function — no side effects.

    >>> classify_event_category("Technical Interview with John")
    'interview'
    >>> classify_event_category("Team standup meeting")
    'team_meeting'
    >>> classify_event_category("Random thing")
    'unknown'
    """
    summary_lower = summary.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in summary_lower:
                return category

    return "unknown"


def calculate_importance_score(category: str) -> int:
    """
    Return the raw importance score (0–100) for a given category.

    >>> calculate_importance_score("interview")
    95
    >>> calculate_importance_score("unknown")
    50
    """
    return CATEGORY_IMPORTANCE.get(category, CATEGORY_IMPORTANCE["unknown"])


def calculate_urgency_score(
    summary: str,
    user_priority: Optional[str] = None,
) -> int:
    """
    Calculate an urgency score (0–100) based on:
      1. Urgency keywords found in the event summary.
      2. User-defined priority level (if provided).

    The score is capped at 100.

    >>> calculate_urgency_score("Urgent client call")
    60
    >>> calculate_urgency_score("Lunch with friends", user_priority="high")
    50
    """
    score = 0
    summary_lower = summary.lower()

    # Each matched urgency keyword adds 20 points (capped later)
    matched_keywords = [kw for kw in URGENCY_KEYWORDS if kw in summary_lower]
    score += len(matched_keywords) * 20

    # User-defined priority overrides / boosts
    if user_priority:
        priority_map = {
            "critical": 80,
            "high":     50,
            "medium":   30,
            "low":      10,
        }
        score = max(score, priority_map.get(user_priority.lower(), 0))

    return min(score, 100)


def calculate_deadline_proximity_score(
    event_start_iso: str,
    reference_time: Optional[datetime.datetime] = None,
) -> int:
    """
    Calculate a deadline proximity score (0–100) based on how soon the event
    starts relative to `reference_time` (defaults to now).

    Scoring curve:
      - ≤ 1 hour  away  → 100
      - ≤ 3 hours away  → 85
      - ≤ 6 hours away  → 70
      - ≤ 12 hours away → 55
      - ≤ 24 hours away → 40
      - ≤ 48 hours away → 25
      - > 48 hours away → 10

    >>> # (output depends on current time — use reference_time for testing)
    """
    if reference_time is None:
        reference_time = datetime.datetime.now(datetime.timezone.utc)

    try:
        event_start = datetime.datetime.fromisoformat(event_start_iso)
        # Make timezone-aware if naive
        if event_start.tzinfo is None:
            event_start = event_start.replace(tzinfo=datetime.timezone.utc)
        if reference_time.tzinfo is None:
            reference_time = reference_time.replace(tzinfo=datetime.timezone.utc)

        hours_until = (event_start - reference_time).total_seconds() / 3600.0
    except (ValueError, TypeError):
        return 50  # fallback for unparseable dates

    if hours_until <= 0:
        return 100  # already started or in the past — max urgency
    elif hours_until <= 1:
        return 100
    elif hours_until <= 3:
        return 85
    elif hours_until <= 6:
        return 70
    elif hours_until <= 12:
        return 55
    elif hours_until <= 24:
        return 40
    elif hours_until <= 48:
        return 25
    else:
        return 10


def _score_to_level(score: int) -> str:
    """Convert a numeric score to a priority level string."""
    for level, (low, high) in PRIORITY_THRESHOLDS.items():
        if low <= score <= high:
            return level
    return "MEDIUM"


def _build_reason(
    summary: str,
    category: str,
    priority_level: str,
    hours_until: float,
    urgency_score: int,
) -> str:
    """Build a human-readable explanation of why this event has its score."""
    parts = []

    # Category context
    category_display = category.replace("_", " ").title()
    parts.append(f"'{summary}' is categorized as {category_display}")

    # Importance note
    importance = CATEGORY_IMPORTANCE.get(category, 50)
    if importance >= 85:
        parts.append("which has high importance")
    elif importance >= 55:
        parts.append("which has medium importance")
    else:
        parts.append("which has low importance")

    # Deadline proximity note
    if hours_until <= 1:
        parts.append("and is starting very soon (within 1 hour)")
    elif hours_until <= 6:
        parts.append(f"and is coming up in about {hours_until:.0f} hours")
    elif hours_until <= 24:
        parts.append("and is scheduled for today")
    elif hours_until <= 48:
        parts.append("and is scheduled for tomorrow")

    # Urgency note
    if urgency_score >= 50:
        parts.append("with high urgency markers")

    reason = ", ".join(parts) + "."
    return reason


# =============================================================================
# MAIN PUBLIC API
# =============================================================================

def calculate_priority(
    event: Dict[str, Any],
    user_priority: Optional[str] = None,
    reference_time: Optional[datetime.datetime] = None,
) -> Dict[str, Any]:
    """
    Calculate the deterministic priority score for a single calendar event.

    Args:
        event: A Google Calendar event dict with at least 'summary' and
               'start' → 'dateTime' fields.
        user_priority: Optional user-supplied priority ('critical', 'high',
                       'medium', 'low').
        reference_time: Optional reference datetime for deadline proximity
                        calculation (defaults to now).

    Returns:
        A structured dict:
        {
            "event_summary": "...",
            "priority_score": 85,
            "priority_level": "HIGH",
            "category": "interview",
            "factors": {
                "urgency": 30,
                "importance": 33,
                "deadline_proximity": 25
            },
            "reason": "..."
        }
    """
    summary = event.get("summary", "Untitled Event")

    # Extract start time
    start_info = event.get("start", {})
    start_iso = start_info.get("dateTime", start_info.get("date", ""))

    # 1. Classify category
    category = classify_event_category(summary)

    # 2. Calculate raw factor scores (each 0–100)
    raw_urgency = calculate_urgency_score(summary, user_priority)
    raw_importance = calculate_importance_score(category)
    raw_deadline = calculate_deadline_proximity_score(start_iso, reference_time)

    # 3. Apply weights to get weighted contributions
    weighted_urgency = raw_urgency * SCORING_WEIGHTS["urgency"]
    weighted_importance = raw_importance * SCORING_WEIGHTS["importance"]
    weighted_deadline = raw_deadline * SCORING_WEIGHTS["deadline_proximity"]

    # 4. Final score (0–100)
    priority_score = round(weighted_urgency + weighted_importance + weighted_deadline)
    priority_score = max(0, min(100, priority_score))

    # 5. Map to level
    priority_level = _score_to_level(priority_score)

    # 6. Build reason
    if reference_time is None:
        reference_time = datetime.datetime.now(datetime.timezone.utc)
    try:
        event_start = datetime.datetime.fromisoformat(start_iso)
        if event_start.tzinfo is None:
            event_start = event_start.replace(tzinfo=datetime.timezone.utc)
        if reference_time.tzinfo is None:
            reference_time = reference_time.replace(tzinfo=datetime.timezone.utc)
        hours_until = max(0, (event_start - reference_time).total_seconds() / 3600.0)
    except (ValueError, TypeError):
        hours_until = 24  # fallback

    reason = _build_reason(summary, category, priority_level, hours_until, raw_urgency)

    return {
        "event_summary": summary,
        "priority_score": priority_score,
        "priority_level": priority_level,
        "category": category,
        "factors": {
            "urgency": round(weighted_urgency),
            "importance": round(weighted_importance),
            "deadline_proximity": round(weighted_deadline),
        },
        "reason": reason,
    }


def compare_conflicts(
    new_event: Dict[str, Any],
    existing_event: Dict[str, Any],
    user_priority_new: Optional[str] = None,
    user_priority_existing: Optional[str] = None,
    reference_time: Optional[datetime.datetime] = None,
) -> Dict[str, Any]:
    """
    Compare two conflicting events and recommend which should take precedence.

    Args:
        new_event: The event the user is trying to create.
        existing_event: The event already on the calendar that conflicts.
        user_priority_new: User-defined priority for the new event.
        user_priority_existing: User-defined priority for the existing event.
        reference_time: Reference time for scoring (defaults to now).

    Returns:
        {
            "conflict_detected": True,
            "new_event": { ...priority result... },
            "existing_event": { ...priority result... },
            "recommendation": "The existing event '...' has higher priority (score: 85 vs 60). Consider rescheduling the new event.",
            "winner": "existing"
        }
    """
    new_result = calculate_priority(new_event, user_priority_new, reference_time)
    existing_result = calculate_priority(existing_event, user_priority_existing, reference_time)

    new_score = new_result["priority_score"]
    existing_score = existing_result["priority_score"]

    new_summary = new_result["event_summary"]
    existing_summary = existing_result["event_summary"]

    if new_score > existing_score:
        winner = "new"
        recommendation = (
            f"⚡ The new event '{new_summary}' has higher priority "
            f"(score: {new_score} vs {existing_score}). "
            f"Consider rescheduling the existing event '{existing_summary}'."
        )
    elif existing_score > new_score:
        winner = "existing"
        recommendation = (
            f"🛡️ The existing event '{existing_summary}' has higher priority "
            f"(score: {existing_score} vs {new_score}). "
            f"Consider rescheduling the new event '{new_summary}'."
        )
    else:
        winner = "tie"
        recommendation = (
            f"⚖️ Both events have equal priority (score: {new_score}). "
            f"Please decide which one to keep: '{new_summary}' vs '{existing_summary}'."
        )

    return {
        "conflict_detected": True,
        "new_event": new_result,
        "existing_event": existing_result,
        "recommendation": recommendation,
        "winner": winner,
    }


def find_overlapping_events(events: List[Dict[str, Any]]) -> List[Tuple[Dict, Dict]]:
    """
    Given a list of Google Calendar event dicts, find all pairs that overlap
    in time. Returns a list of (event_a, event_b) tuples.

    Only considers timed events (with 'dateTime'), not all-day events.
    """
    timed_events = []
    for ev in events:
        start_info = ev.get("start", {})
        end_info = ev.get("end", {})
        start_dt_str = start_info.get("dateTime")
        end_dt_str = end_info.get("dateTime")
        if start_dt_str and end_dt_str:
            try:
                start_dt = datetime.datetime.fromisoformat(start_dt_str)
                end_dt = datetime.datetime.fromisoformat(end_dt_str)
                timed_events.append((start_dt, end_dt, ev))
            except (ValueError, TypeError):
                continue

    # Sort by start time
    timed_events.sort(key=lambda x: x[0])

    overlaps = []
    for i in range(len(timed_events)):
        for j in range(i + 1, len(timed_events)):
            start_a, end_a, ev_a = timed_events[i]
            start_b, end_b, ev_b = timed_events[j]

            # If event B starts after event A ends, no overlap (and none further)
            if start_b >= end_a:
                break

            # Overlap exists
            overlaps.append((ev_a, ev_b))

    return overlaps
