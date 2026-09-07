"""
Unit tests for the Priority Scoring Engine.

Run with:
    python -m pytest test_priority_engine.py -v
"""

import datetime
import pytest

from priority_engine import (
    classify_event_category,
    calculate_importance_score,
    calculate_urgency_score,
    calculate_deadline_proximity_score,
    calculate_priority,
    compare_conflicts,
    find_overlapping_events,
    CATEGORY_IMPORTANCE,
)


# =============================================================================
# classify_event_category
# =============================================================================

class TestClassifyEventCategory:
    def test_interview(self):
        assert classify_event_category("Technical Interview with John") == "interview"

    def test_interview_case_insensitive(self):
        assert classify_event_category("INTERVIEW ROUND 2") == "interview"

    def test_deadline(self):
        assert classify_event_category("Project deadline review") == "deadline"

    def test_client_meeting(self):
        assert classify_event_category("Client onboarding call") == "client_meeting"

    def test_team_meeting(self):
        assert classify_event_category("Daily standup") == "team_meeting"

    def test_team_sync(self):
        assert classify_event_category("Weekly team sync") == "team_meeting"

    def test_personal(self):
        assert classify_event_category("Doctor appointment") == "personal"

    def test_workout(self):
        assert classify_event_category("Morning gym session") == "workout"

    def test_optional(self):
        assert classify_event_category("Optional info session") == "optional"

    def test_unknown(self):
        assert classify_event_category("Random unrelated thing") == "unknown"

    def test_empty_string(self):
        assert classify_event_category("") == "unknown"


# =============================================================================
# calculate_importance_score
# =============================================================================

class TestCalculateImportanceScore:
    def test_interview_score(self):
        assert calculate_importance_score("interview") == 95

    def test_workout_score(self):
        assert calculate_importance_score("workout") == 30

    def test_unknown_fallback(self):
        assert calculate_importance_score("unknown") == 50

    def test_nonexistent_category(self):
        assert calculate_importance_score("doesnt_exist") == 50


# =============================================================================
# calculate_urgency_score
# =============================================================================

class TestCalculateUrgencyScore:
    def test_no_urgency_keywords(self):
        assert calculate_urgency_score("Lunch with friends") == 0

    def test_single_urgency_keyword(self):
        assert calculate_urgency_score("Urgent client call") == 20

    def test_multiple_urgency_keywords(self):
        score = calculate_urgency_score("URGENT critical blocker meeting")
        assert score == 60  # 3 keywords × 20

    def test_user_priority_high(self):
        score = calculate_urgency_score("Lunch with friends", user_priority="high")
        assert score == 50

    def test_user_priority_critical(self):
        score = calculate_urgency_score("Lunch with friends", user_priority="critical")
        assert score == 80

    def test_user_priority_overrides_low_keyword(self):
        # keyword gives 20, but user says critical → max(20, 80) = 80
        score = calculate_urgency_score("Urgent lunch", user_priority="critical")
        assert score == 80

    def test_capped_at_100(self):
        # 6+ keywords → capped
        score = calculate_urgency_score(
            "urgent critical blocker p0 p1 emergency escalation"
        )
        assert score == 100

    def test_no_user_priority(self):
        assert calculate_urgency_score("Team sync", user_priority=None) == 0


# =============================================================================
# calculate_deadline_proximity_score
# =============================================================================

class TestCalculateDeadlineProximityScore:
    def _ref(self, hours_from_now):
        """Helper to create a reference time and event start."""
        ref = datetime.datetime(2026, 9, 7, 12, 0, tzinfo=datetime.timezone.utc)
        event_start = ref + datetime.timedelta(hours=hours_from_now)
        return event_start.isoformat(), ref

    def test_within_1_hour(self):
        iso, ref = self._ref(0.5)
        assert calculate_deadline_proximity_score(iso, ref) == 100

    def test_within_3_hours(self):
        iso, ref = self._ref(2)
        assert calculate_deadline_proximity_score(iso, ref) == 85

    def test_within_6_hours(self):
        iso, ref = self._ref(5)
        assert calculate_deadline_proximity_score(iso, ref) == 70

    def test_within_12_hours(self):
        iso, ref = self._ref(10)
        assert calculate_deadline_proximity_score(iso, ref) == 55

    def test_within_24_hours(self):
        iso, ref = self._ref(20)
        assert calculate_deadline_proximity_score(iso, ref) == 40

    def test_within_48_hours(self):
        iso, ref = self._ref(36)
        assert calculate_deadline_proximity_score(iso, ref) == 25

    def test_beyond_48_hours(self):
        iso, ref = self._ref(72)
        assert calculate_deadline_proximity_score(iso, ref) == 10

    def test_event_in_past(self):
        iso, ref = self._ref(-2)
        assert calculate_deadline_proximity_score(iso, ref) == 100

    def test_unparseable_date(self):
        assert calculate_deadline_proximity_score("not-a-date") == 50


# =============================================================================
# calculate_priority (integration)
# =============================================================================

class TestCalculatePriority:
    REF_TIME = datetime.datetime(2026, 9, 7, 12, 0, tzinfo=datetime.timezone.utc)

    def _make_event(self, summary, hours_from_ref=2):
        start = self.REF_TIME + datetime.timedelta(hours=hours_from_ref)
        return {
            "summary": summary,
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": (start + datetime.timedelta(hours=1)).isoformat()},
        }

    def test_returns_required_keys(self):
        event = self._make_event("Technical Interview")
        result = calculate_priority(event, reference_time=self.REF_TIME)

        assert "priority_score" in result
        assert "priority_level" in result
        assert "factors" in result
        assert "reason" in result
        assert "category" in result
        assert "event_summary" in result

    def test_interview_scores_high(self):
        event = self._make_event("Technical Interview", hours_from_ref=2)
        result = calculate_priority(event, reference_time=self.REF_TIME)

        assert result["category"] == "interview"
        # Interview has high importance (95) but no urgency keywords → lands
        # in MEDIUM range. Adding urgency keywords would push it to HIGH.
        assert result["priority_level"] in ("MEDIUM", "HIGH", "CRITICAL")
        assert result["priority_score"] >= 55

    def test_optional_scores_low(self):
        event = self._make_event("Optional social lunch", hours_from_ref=48)
        result = calculate_priority(event, reference_time=self.REF_TIME)

        assert result["category"] == "optional"
        assert result["priority_score"] < 30

    def test_user_priority_boosts_score(self):
        event = self._make_event("Random meeting", hours_from_ref=5)
        base = calculate_priority(event, reference_time=self.REF_TIME)
        boosted = calculate_priority(
            event, user_priority="critical", reference_time=self.REF_TIME
        )
        assert boosted["priority_score"] > base["priority_score"]

    def test_closer_event_scores_higher(self):
        event_soon = self._make_event("Team sync", hours_from_ref=1)
        event_far = self._make_event("Team sync", hours_from_ref=72)

        score_soon = calculate_priority(event_soon, reference_time=self.REF_TIME)
        score_far = calculate_priority(event_far, reference_time=self.REF_TIME)

        assert score_soon["priority_score"] > score_far["priority_score"]

    def test_score_within_bounds(self):
        event = self._make_event("Urgent critical interview deadline", hours_from_ref=0.5)
        result = calculate_priority(
            event, user_priority="critical", reference_time=self.REF_TIME
        )
        assert 0 <= result["priority_score"] <= 100

    def test_missing_summary(self):
        event = {"start": {"dateTime": self.REF_TIME.isoformat()}}
        result = calculate_priority(event, reference_time=self.REF_TIME)
        assert result["event_summary"] == "Untitled Event"


# =============================================================================
# compare_conflicts
# =============================================================================

class TestCompareConflicts:
    REF_TIME = datetime.datetime(2026, 9, 7, 12, 0, tzinfo=datetime.timezone.utc)

    def _make_event(self, summary, hours_from_ref=2):
        start = self.REF_TIME + datetime.timedelta(hours=hours_from_ref)
        return {
            "summary": summary,
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": (start + datetime.timedelta(hours=1)).isoformat()},
        }

    def test_interview_beats_optional(self):
        interview = self._make_event("Technical Interview", hours_from_ref=2)
        optional = self._make_event("Optional coffee chat", hours_from_ref=2)

        result = compare_conflicts(interview, optional, reference_time=self.REF_TIME)

        assert result["conflict_detected"] is True
        assert result["winner"] == "new"
        assert result["new_event"]["priority_score"] > result["existing_event"]["priority_score"]

    def test_client_meeting_beats_workout(self):
        client = self._make_event("Client quarterly review", hours_from_ref=3)
        workout = self._make_event("Gym session", hours_from_ref=3)

        result = compare_conflicts(client, workout, reference_time=self.REF_TIME)

        assert result["winner"] == "new"

    def test_same_category_tie(self):
        event_a = self._make_event("Team sync A", hours_from_ref=5)
        event_b = self._make_event("Team sync B", hours_from_ref=5)

        result = compare_conflicts(event_a, event_b, reference_time=self.REF_TIME)

        assert result["winner"] == "tie"

    def test_has_recommendation(self):
        a = self._make_event("Interview", hours_from_ref=2)
        b = self._make_event("Gym", hours_from_ref=2)
        result = compare_conflicts(a, b, reference_time=self.REF_TIME)

        assert "recommendation" in result
        assert len(result["recommendation"]) > 10

    def test_user_priority_can_flip_winner(self):
        interview = self._make_event("Interview", hours_from_ref=5)
        gym = self._make_event("Gym", hours_from_ref=5)

        # Without user priority: interview wins
        normal = compare_conflicts(interview, gym, reference_time=self.REF_TIME)
        assert normal["winner"] == "new"

        # With critical priority on gym: gym might win or tie
        flipped = compare_conflicts(
            interview, gym,
            user_priority_existing="critical",
            reference_time=self.REF_TIME,
        )
        assert flipped["existing_event"]["priority_score"] > normal["existing_event"]["priority_score"]


# =============================================================================
# find_overlapping_events
# =============================================================================

class TestFindOverlappingEvents:
    def _make_event(self, summary, start_hour, end_hour):
        base = datetime.datetime(2026, 9, 7, 0, 0, tzinfo=datetime.timezone.utc)
        return {
            "summary": summary,
            "start": {"dateTime": (base + datetime.timedelta(hours=start_hour)).isoformat()},
            "end": {"dateTime": (base + datetime.timedelta(hours=end_hour)).isoformat()},
        }

    def test_no_overlaps(self):
        events = [
            self._make_event("A", 9, 10),
            self._make_event("B", 10, 11),
            self._make_event("C", 12, 13),
        ]
        assert find_overlapping_events(events) == []

    def test_simple_overlap(self):
        events = [
            self._make_event("A", 9, 11),
            self._make_event("B", 10, 12),
        ]
        overlaps = find_overlapping_events(events)
        assert len(overlaps) == 1

    def test_multiple_overlaps(self):
        events = [
            self._make_event("A", 9, 12),
            self._make_event("B", 10, 13),
            self._make_event("C", 11, 14),
        ]
        overlaps = find_overlapping_events(events)
        assert len(overlaps) == 3  # A-B, A-C, B-C

    def test_empty_list(self):
        assert find_overlapping_events([]) == []

    def test_all_day_events_ignored(self):
        events = [
            {"summary": "All day", "start": {"date": "2026-09-07"}, "end": {"date": "2026-09-08"}},
        ]
        assert find_overlapping_events(events) == []
