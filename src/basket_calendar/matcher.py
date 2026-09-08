"""Explainable, conservative matching of Profixio events to SportAdmin events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .models import CalendarEvent
from .normalize import normalize_team, normalize_venue, similarity
from .teams import extract_teams

MAX_CANDIDATE_TIME_DIFFERENCE = timedelta(hours=2)
CONFIDENT_SCORE = 0.85
PROBABLE_SCORE = 0.70
AMBIGUITY_MARGIN = 0.08
MIN_TEAM_SIMILARITY = 0.65


@dataclass(frozen=True)
class Candidate:
    event: CalendarEvent
    score: float
    reasons: list[str]


@dataclass(frozen=True)
class MatchResult:
    status: str
    score: float | None
    event: CalendarEvent | None
    reasons: list[str]
    candidate_count: int


def score_candidate(profixio: CalendarEvent, sportadmin: CalendarEvent) -> Candidate | None:
    """Score a candidate. Teams dominate score; venue alone can never produce a match."""
    if profixio.is_all_day != sportadmin.is_all_day:
        return None
    day_difference = abs((profixio.start.date() - sportadmin.start.date()).days)
    if day_difference > 0:
        return None
    time_difference = abs(profixio.start - sportadmin.start)
    if not profixio.is_all_day and time_difference > MAX_CANDIDATE_TIME_DIFFERENCE:
        return None

    reasons = ["same local date"]
    score = 0.30
    if not profixio.is_all_day:
        time_score = max(0.0, 0.20 * (1 - time_difference / MAX_CANDIDATE_TIME_DIFFERENCE))
        score += time_score
        reasons.append(f"start times differ by {int(time_difference.total_seconds() // 60)} minutes")

    p_teams, s_teams = extract_teams(profixio), extract_teams(sportadmin)
    home_similarity = similarity(normalize_team(p_teams.home), normalize_team(s_teams.home))
    away_similarity = similarity(normalize_team(p_teams.away), normalize_team(s_teams.away))
    if p_teams.home and s_teams.home:
        score += 0.25 * home_similarity
        reasons.append(f"home team similarity {home_similarity:.0%}")
    if p_teams.away and s_teams.away:
        score += 0.25 * away_similarity
        reasons.append(f"away team similarity {away_similarity:.0%}")

    venue_similarity = similarity(normalize_venue(profixio.location), normalize_venue(sportadmin.location))
    if profixio.location and sportadmin.location:
        score += 0.05 * venue_similarity
        reasons.append(f"venue similarity {venue_similarity:.0%}")
    return Candidate(event=sportadmin, score=min(score, 1.0), reasons=reasons)


def match_event(profixio: CalendarEvent, sportadmin_events: list[CalendarEvent]) -> MatchResult:
    candidates = [candidate for event in sportadmin_events if (candidate := score_candidate(profixio, event))]
    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    if not candidates:
        return MatchResult("unmatched", None, None, ["no candidates on same date and nearby time"], 0)
    best = candidates[0]
    if len(candidates) > 1 and best.score - candidates[1].score < AMBIGUITY_MARGIN:
        return MatchResult("ambiguous", best.score, None, best.reasons, len(candidates))
    p_teams, s_teams = extract_teams(profixio), extract_teams(best.event)
    home_similarity = similarity(normalize_team(p_teams.home), normalize_team(s_teams.home))
    away_similarity = similarity(normalize_team(p_teams.away), normalize_team(s_teams.away))
    if home_similarity < MIN_TEAM_SIMILARITY or away_similarity < MIN_TEAM_SIMILARITY:
        return MatchResult(
            "unmatched",
            best.score,
            None,
            best.reasons + ["teams did not meet the minimum similarity threshold"],
            len(candidates),
        )
    if best.score >= CONFIDENT_SCORE:
        return MatchResult("matched_confident", best.score, best.event, best.reasons, len(candidates))
    if best.score >= PROBABLE_SCORE:
        return MatchResult("matched_probable", best.score, best.event, best.reasons, len(candidates))
    return MatchResult("unmatched", best.score, None, best.reasons, len(candidates))
