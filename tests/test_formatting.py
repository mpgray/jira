"""Tests for the pure helpers: time parsing/formatting and env-driven config.

These are the parts that decide what gets written to Jira as a worklog, so a
regression here logs the wrong time against a real ticket rather than failing.
"""
from datetime import datetime

import pytest

from config import get_default_comments, get_frequent_tickets
from controllers.time import TimeController
from jira_lib.jira_worklog import format_worklog_time, seconds_to_hours
from ui.ui_utils import format_time_display, format_time_with_hours


@pytest.fixture
def controller():
    return TimeController(jira=None)


@pytest.mark.parametrize("value", ["2h", "30m", "1h 30m", "2d 4h", "1w", "1.5h", " 45M "])
def test_valid_jira_durations_are_accepted(controller, value):
    assert controller.validate_time_format(value) == (True, None)


@pytest.mark.parametrize("value", ["", "   ", "2", "h", "2 hours", "-1h", "1x"])
def test_invalid_durations_are_rejected_before_reaching_jira(controller, value):
    ok, message = controller.validate_time_format(value)
    assert ok is False
    assert message


@pytest.mark.parametrize(
    "value, hour, minute",
    [("2:30pm", 14, 30), ("2:30 PM", 14, 30), ("09:05", 9, 5), ("14:45", 14, 45)],
)
def test_start_times_parse_to_today(controller, value, hour, minute):
    ok, started = controller.parse_start_time(value)
    assert ok is True
    assert (started.hour, started.minute) == (hour, minute)
    assert started.date() == datetime.now().date()


def test_blank_start_time_means_now(controller):
    assert controller.parse_start_time("") == (True, None)


def test_unparseable_start_time_is_reported(controller):
    assert controller.parse_start_time("half past two") == (False, None)


@pytest.mark.parametrize(
    "seconds, expected",
    [(0, "0m"), (59, "0m"), (60, "1m"), (3600, "1h"), (5400, "1h 30m"), (9000, "2h 30m")],
)
def test_format_worklog_time(seconds, expected):
    assert format_worklog_time(seconds) == expected


def test_format_time_display_hides_zero():
    assert format_time_display(0) == ""
    assert format_time_display(None) == ""
    assert format_time_display(5400) == "1h 30m"


def test_hours_helpers_agree():
    assert seconds_to_hours(5400) == 1.5
    assert format_time_with_hours(5400) == "1h 30m (1.50 hours)"


def test_only_configured_frequent_tickets_are_offered(monkeypatch):
    for var in ("TICKET_STAND_UP", "TICKET_SPRINT_PLANNING", "TICKET_SPRINT_RETRO",
                "TICKET_SPRINT_REFINEMENT", "TICKET_SPRINT_REVIEW", "TICKET_REGRESSION_REVIEW"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("TICKET_STAND_UP", "PROJ-1")
    monkeypatch.setenv("TICKET_SPRINT_REVIEW", "PROJ-5")

    assert get_frequent_tickets() == {"1": ("PROJ-1", "Stand Up"), "5": ("PROJ-5", "Sprint Review")}
    assert get_default_comments() == {
        "PROJ-1": "attend standup",
        "PROJ-5": "prepare for, present, and attend sprint review",
    }
