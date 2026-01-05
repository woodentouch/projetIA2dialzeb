"""
Opta-Level API Routes - Advanced Analytics & Predictions
Enhanced endpoints with form, venue, head-to-head, and comprehensive statistics
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field as PydField
from sqlmodel import Session, select, create_engine, func
import os

from .models import TeamRating, Match
from .models_advanced import (
    TeamFormMetrics, MatchContext, TeamAdvancedRating,
    MatchStatistics, HeadToHeadHistory, VenueType
)
from .trueskill_rating import TeamSkill, TRUESKILL_ENV, expected_outcome_probabilities, update_ratings_after_match
from .opta_engine import OptaAIEngine, OptaMatchPrediction


router = APIRouter(prefix="/api/opta", tags=["opta", "advanced-ai"])

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/sports")
engine = create_engine(DATABASE_URL)


def get_db_session():
    """Dependency for DB session"""
    with Session(engine) as session:
        yield session


class OptaPredictionRequest(BaseModel):
    """Request model for Opta-level prediction"""
    team1: str = PydField(..., min_length=1)
    team2: str = PydField(..., min_length=1)
    venue: VenueType = VenueType.HOME  # home, away, neutral
    match_date: Optional[datetime] = None
    n_simulations: int = PydField(20000, ge=5000, le=50000)
    use_advanced_features: bool = True


class MatchResultInput(BaseModel):
    """Complete match result with statistics"""
    team1: str
    team2: str
    score1: int = PydField(..., ge=0)
    score2: int = PydField(..., ge=0)
    match_date: datetime = PydField(default_factory=datetime.utcnow)
    venue: VenueType = VenueType.HOME
    
    # Optional detailed statistics (Opta-level)
    team1_stats: Optional[dict] = None  # MatchStatistics fields
    team2_stats: Optional[dict] = None
    
    # Context
    context: Optional[dict] = None  # MatchContext fields
    
    store_statistics: bool = True


class FormUpdateRequest(BaseModel):
    """Request to update team form metrics"""
    team: str
    result: str  # "W", "D", "L"
    goals_scored: int
    goals_conceded: int
    venue: VenueType
    match_date: datetime = PydField(default_factory=datetime.utcnow)


@router.post("/predict")
def opta_predict_match(
    request: OptaPredictionRequest,
    db: Session = Depends(get_db_session)
):
    """
    🚀 Opta-Level Match Prediction - Professional Analytics
    
    Advanced AI prediction using:
    - Venue-split TrueSkill ratings (home/away/neutral)
    - Recent form & momentum (last 5-10 matches)
    - Head-to-head history
    - Expected goals (xG) with confidence intervals
    - Half-time predictions & HT/FT markets
    - Comprehensive betting markets (O/U, BTTS, margins)
    - Upset probability detection
    - Advanced metrics (possession, shots, corners)
    
    Returns Opta-level comprehensive match analysis.
    """
    
    if request.team1 == request.team2:
        raise HTTPException(status_code=400, detail="Teams must be different")
    
    # Initialize Opta AI Engine
    ai_engine = OptaAIEngine(db_session=db)
    
    # Generate prediction
    prediction = ai_engine.predict_match(
        team1=request.team1,
        team2=request.team2,
        venue=request.venue.value,
        match_date=request.match_date,
        n_simulations=request.n_simulations,
        use_advanced_features=request.use_advanced_features,
    )
    
    # Convert to plain Python types (avoid numpy types)
    most_likely_scores = [
        {
            "score": s["score"],
            "home_goals": int(s["home_goals"]),
            "away_goals": int(s["away_goals"]),
            "probability": float(s["probability"]),
        }
        for s in prediction.most_likely_scores[:10]
    ]
    
    ht_ft_markets = {k: float(v) for k, v in prediction.ht_ft_predictions.items()}
    
    # Format response
    return {
        "model": "Opta-Level AI Engine v2.0",
        "match": {
            "home": prediction.team1,
            "away": prediction.team2,
            "venue": prediction.venue,
            "date": prediction.match_date.isoformat() if prediction.match_date else None,
        },
        "ratings": {
            "home": {
                "overall": {"mu": float(prediction.team1_rating.mu), "sigma": float(prediction.team1_rating.sigma)},
                "venue_specific": {"mu": float(prediction.team1_rating_home.mu), "sigma": float(prediction.team1_rating_home.sigma)} if prediction.team1_rating_home else None,
            },
            "away": {
                "overall": {"mu": float(prediction.team2_rating.mu), "sigma": float(prediction.team2_rating.sigma)},
                "venue_specific": {"mu": float(prediction.team2_rating_away.mu), "sigma": float(prediction.team2_rating_away.sigma)} if prediction.team2_rating_away else None,
            },
        },
        "outcome_probabilities": {
            "home_win": float(prediction.team1_win_prob),
            "draw": float(prediction.draw_prob),
            "away_win": float(prediction.team2_win_prob),
        },
        "expected_goals": {
            "home": {
                "value": float(prediction.team1_xg),
                "range": {"min": float(prediction.team1_xg_range[0]), "max": float(prediction.team1_xg_range[1])},
            },
            "away": {
                "value": float(prediction.team2_xg),
                "range": {"min": float(prediction.team2_xg_range[0]), "max": float(prediction.team2_xg_range[1])},
            },
            "total": float(prediction.team1_xg + prediction.team2_xg),
        },
        "form_analysis": {
            "home_form_factor": float(prediction.team1_form_factor),
            "away_form_factor": float(prediction.team2_form_factor),
            "home_momentum": str(prediction.team1_momentum),
            "away_momentum": str(prediction.team2_momentum),
        },
        "betting_markets": {
            "over_under": {
                "1.5": {"over": float(prediction.over_under_1_5["over"]), "under": float(prediction.over_under_1_5["under"])},
                "2.5": {"over": float(prediction.over_under_2_5["over"]), "under": float(prediction.over_under_2_5["under"])},
                "3.5": {"over": float(prediction.over_under_3_5["over"]), "under": float(prediction.over_under_3_5["under"])},
            },
            "both_teams_score": float(prediction.both_teams_score_prob),
            "clean_sheet": {
                "home": float(prediction.team1_win_to_nil_prob),
                "away": float(prediction.team2_win_to_nil_prob),
            },
            "margin": {
                "home_by_2_plus": float(prediction.team1_win_by_2_plus),
                "away_by_2_plus": float(prediction.team2_win_by_2_plus),
            },
        },
        "half_time": {
            "probabilities": {
                "home_lead": float(prediction.ht_team1_win_prob),
                "draw": float(prediction.ht_draw_prob),
                "away_lead": float(prediction.ht_team2_win_prob),
            },
            "ht_ft_markets": ht_ft_markets,
        },
        "most_likely_scores": most_likely_scores,
        "advanced_metrics": {
            "predicted_possession": {
                "home": float(prediction.predicted_possession_split[0]),
                "away": float(prediction.predicted_possession_split[1]),
            },
            "expected_shots_on_target": {
                "home": int(prediction.expected_shots_on_target[0]),
                "away": int(prediction.expected_shots_on_target[1]),
            },
            "expected_corners": {
                "home": int(prediction.expected_corners[0]),
                "away": int(prediction.expected_corners[1]),
            },
            "upset_probability": float(prediction.upset_probability),
        },
        "context_factors": {
            "venue_advantage": float(prediction.venue_advantage),
            "h2h_factor": float(prediction.h2h_factor),
            "importance_factor": float(prediction.importance_factor),
        },
        "odds": {
            "home": float(prediction.fair_odds_team1),
            "draw": float(prediction.fair_odds_draw),
            "away": float(prediction.fair_odds_team2),
            "bookmaker_margin": float(prediction.bookmaker_margin * 100),
        },
        "confidence": {
            "level": str(prediction.confidence_level),
            "score": float(prediction.prediction_confidence),
            "data_quality": float(prediction.data_quality_score),
            "model_uncertainty": float(prediction.model_uncertainty),
        },
        "value_bets": prediction.value_bets,
        "recommendation": str(prediction.top_recommendation),
        "simulation_details": {
            "simulations": int(prediction.simulations_run),
            "variance": float(prediction.monte_carlo_variance),
        },
    }


@router.post("/match-result")
def submit_match_result(
    result: MatchResultInput,
    db: Session = Depends(get_db_session)
):
    """
    📊 Submit Complete Match Result with Statistics
    
    Updates ratings, form metrics, and stores detailed match statistics.
    Opta-level data processing.
    """
    
    # 1. Store basic match
    match = Match(
        team1=result.team1,
        team2=result.team2,
        score1=result.score1,
        score2=result.score2,
        date=result.match_date.isoformat(),
        source="opta",
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    
    # 2. Update TrueSkill ratings (overall)
    rating1 = _get_or_create_rating(db, result.team1)
    rating2 = _get_or_create_rating(db, result.team2)
    
    skill1 = TeamSkill(result.team1, rating1.mu, rating1.sigma)
    skill2 = TeamSkill(result.team2, rating2.mu, rating2.sigma)
    
    new_skill1, new_skill2, outcome = update_ratings_after_match(
        skill1, skill2, result.score1, result.score2
    )
    
    rating1.mu = new_skill1.mu
    rating1.sigma = new_skill1.sigma
    rating1.updated_at = datetime.utcnow()
    
    rating2.mu = new_skill2.mu
    rating2.sigma = new_skill2.sigma
    rating2.updated_at = datetime.utcnow()
    
    db.add(rating1)
    db.add(rating2)
    
    # 3. Update venue-specific ratings
    adv1 = _get_or_create_advanced_rating(db, result.team1)
    adv2 = _get_or_create_advanced_rating(db, result.team2)
    
    if result.venue == VenueType.HOME:
        # Update home/away splits
        skill1_home = TeamSkill(result.team1, adv1.mu_home, adv1.sigma_home)
        skill2_away = TeamSkill(result.team2, adv2.mu_away, adv2.sigma_away)
        
        new1, new2, _ = update_ratings_after_match(skill1_home, skill2_away, result.score1, result.score2)
        
        adv1.mu_home = new1.mu
        adv1.sigma_home = new1.sigma
        adv1.matches_home += 1
        
        adv2.mu_away = new2.mu
        adv2.sigma_away = new2.sigma
        adv2.matches_away += 1
    
    adv1.matches_played += 1
    adv2.matches_played += 1
    adv1.last_match_date = result.match_date
    adv2.last_match_date = result.match_date
    
    db.add(adv1)
    db.add(adv2)
    
    # 4. Update form metrics
    _update_form_metrics(db, result.team1, outcome == "team1", result.score1, result.score2, result.venue, result.match_date)
    _update_form_metrics(db, result.team2, outcome == "team2", result.score2, result.score1, 
                         VenueType.AWAY if result.venue == VenueType.HOME else VenueType.HOME, result.match_date)
    
    # 5. Store match statistics (if provided)
    if result.store_statistics and result.team1_stats:
        stats1 = MatchStatistics(
            match_id=match.id,
            team=result.team1,
            **result.team1_stats
        )
        db.add(stats1)
    
    if result.store_statistics and result.team2_stats:
        stats2 = MatchStatistics(
            match_id=match.id,
            team=result.team2,
            **result.team2_stats
        )
        db.add(stats2)
    
    # 6. Store match context (if provided)
    if result.context:
        context = MatchContext(
            match_id=match.id,
            **result.context
        )
        db.add(context)
    
    # 7. Update head-to-head record
    _update_h2h_record(db, result.team1, result.team2, result.score1, result.score2, result.match_date)
    
    db.commit()
    
    return {
        "status": "success",
        "match_id": match.id,
        "result": outcome,
        "ratings_updated": {
            "team1": {"mu": rating1.mu, "sigma": rating1.sigma},
            "team2": {"mu": rating2.mu, "sigma": rating2.sigma},
        },
        "form_updated": True,
        "statistics_stored": result.store_statistics,
    }


@router.get("/team-analysis/{team}")
def get_team_analysis(
    team: str,
    db: Session = Depends(get_db_session)
):
    """
    📈 Comprehensive Team Analysis - Opta Level
    
    Returns complete team profile:
    - Overall & venue-specific ratings
    - Recent form & momentum
    - Attack/defense strength
    - Performance trends
    """
    
    # Get ratings
    rating = _get_or_create_rating(db, team)
    adv_rating = _get_or_create_advanced_rating(db, team)
    form = db.exec(select(TeamFormMetrics).where(TeamFormMetrics.team == team)).first()
    
    # Get recent matches
    recent_matches = db.exec(
        select(Match)
        .where((Match.team1 == team) | (Match.team2 == team))
        .order_by(Match.date.desc())
        .limit(10)
    ).all()
    
    return {
        "team": team,
        "ratings": {
            "overall": {
                "mu": rating.mu,
                "sigma": rating.sigma,
                "conservative": rating.mu - 3 * rating.sigma,
            },
            "venue_split": {
                "home": {"mu": adv_rating.mu_home, "sigma": adv_rating.sigma_home},
                "away": {"mu": adv_rating.mu_away, "sigma": adv_rating.sigma_away},
            },
            "components": {
                "attack": {"mu": adv_rating.mu_attack, "sigma": adv_rating.sigma_attack},
                "defense": {"mu": adv_rating.mu_defense, "sigma": adv_rating.sigma_defense},
            },
        },
        "form": {
            "last_5": form.form_last_5 if form else "",
            "last_10": form.form_last_10 if form else "",
            "points_last_5": form.points_last_5 if form else 0,
            "momentum": _classify_momentum(form) if form else "unknown",
            "goals_scored_last_5": form.goals_scored_last_5 if form else 0,
            "goals_conceded_last_5": form.goals_conceded_last_5 if form else 0,
            "clean_sheets_last_5": form.clean_sheets_last_5 if form else 0,
            "streaks": {
                "wins": form.current_win_streak if form else 0,
                "unbeaten": form.current_unbeaten_streak if form else 0,
                "losses": form.current_loss_streak if form else 0,
            } if form else None,
        },
        "statistics": {
            "matches_played": adv_rating.matches_played,
            "home_matches": adv_rating.matches_home,
            "away_matches": adv_rating.matches_away,
            "last_match": adv_rating.last_match_date.isoformat() if adv_rating.last_match_date else None,
        },
        "recent_matches": [
            {
                "date": m.date,
                "opponent": m.team2 if m.team1 == team else m.team1,
                "score": f"{m.score1}-{m.score2}" if m.team1 == team else f"{m.score2}-{m.score1}",
                "result": _get_result_for_team(m, team),
            }
            for m in recent_matches
        ],
    }


@router.get("/head-to-head")
def get_head_to_head_analysis(
    team1: str = Query(...),
    team2: str = Query(...),
    db: Session = Depends(get_db_session)
):
    """
    🤝 Head-to-Head Historical Analysis
    
    Complete historical record between two teams.
    """
    
    h2h = db.exec(
        select(HeadToHeadHistory).where(
            ((HeadToHeadHistory.team1 == team1) & (HeadToHeadHistory.team2 == team2)) |
            ((HeadToHeadHistory.team1 == team2) & (HeadToHeadHistory.team2 == team1))
        )
    ).first()
    
    if not h2h:
        return {
            "team1": team1,
            "team2": team2,
            "total_matches": 0,
            "message": "No historical data available",
        }
    
    # Normalize to requested team order
    if h2h.team1 != team1:
        team1_wins = h2h.team2_wins
        team2_wins = h2h.team1_wins
        team1_goals = h2h.team2_goals_total
        team2_goals = h2h.team1_goals_total
    else:
        team1_wins = h2h.team1_wins
        team2_wins = h2h.team2_wins
        team1_goals = h2h.team1_goals_total
        team2_goals = h2h.team2_goals_total
    
    return {
        "team1": team1,
        "team2": team2,
        "overall": {
            "total_matches": h2h.total_matches,
            "team1_wins": team1_wins,
            "team2_wins": team2_wins,
            "draws": h2h.draws,
            "team1_win_percentage": (team1_wins / h2h.total_matches * 100) if h2h.total_matches > 0 else 0,
        },
        "goals": {
            "team1_total": team1_goals,
            "team2_total": team2_goals,
            "avg_per_match": (team1_goals + team2_goals) / h2h.total_matches if h2h.total_matches > 0 else 0,
        },
        "recent_form": h2h.recent_form,
        "last_meeting": {
            "date": h2h.last_match_date.isoformat() if h2h.last_match_date else None,
            "score": h2h.last_match_score,
            "winner": h2h.last_match_winner,
        },
    }


@router.get("/leaderboard")
def get_opta_leaderboard(
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("overall", regex="^(overall|home|away|attack|defense|form)$"),
    league: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """
    🏆 Advanced Team Leaderboard - Opta Level
    
    Rankings by various metrics: overall, home, away, attack, defense, form.
    """
    
    query = select(TeamAdvancedRating)
    
    if league:
        query = query.where(TeamAdvancedRating.league == league)
    
    teams = db.exec(query.limit(limit * 2)).all()  # Get more for sorting
    
    # Sort based on requested metric
    if sort_by == "overall":
        teams.sort(key=lambda t: t.mu_overall - 3 * t.sigma_overall, reverse=True)
    elif sort_by == "home":
        teams.sort(key=lambda t: t.mu_home - 3 * t.sigma_home, reverse=True)
    elif sort_by == "away":
        teams.sort(key=lambda t: t.mu_away - 3 * t.sigma_away, reverse=True)
    elif sort_by == "attack":
        teams.sort(key=lambda t: t.mu_attack - 3 * t.sigma_attack, reverse=True)
    elif sort_by == "defense":
        teams.sort(key=lambda t: t.mu_defense - 3 * t.sigma_defense, reverse=True)
    elif sort_by == "form":
        # Load form metrics for sorting
        form_dict = {
            f.team: f.points_last_5
            for f in db.exec(select(TeamFormMetrics)).all()
        }
        teams.sort(key=lambda t: form_dict.get(t.team, 0), reverse=True)
    
    teams = teams[:limit]
    
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "team": t.team,
                "ratings": {
                    "overall": t.mu_overall - 3 * t.sigma_overall,
                    "home": t.mu_home - 3 * t.sigma_home,
                    "away": t.mu_away - 3 * t.sigma_away,
                },
                "matches_played": t.matches_played,
            }
            for i, t in enumerate(teams)
        ],
        "sort_by": sort_by,
        "total_teams": len(teams),
    }


# Helper functions

def _get_or_create_rating(db: Session, team: str) -> TeamRating:
    """Get or create basic TeamRating"""
    rating = db.exec(select(TeamRating).where(TeamRating.team == team)).first()
    if not rating:
        default_rating = TRUESKILL_ENV.create_rating()
        rating = TeamRating(team=team, mu=float(default_rating.mu), sigma=float(default_rating.sigma))
        db.add(rating)
        db.commit()
        db.refresh(rating)
    return rating


def _get_or_create_advanced_rating(db: Session, team: str) -> TeamAdvancedRating:
    """Get or create TeamAdvancedRating"""
    rating = db.exec(select(TeamAdvancedRating).where(TeamAdvancedRating.team == team)).first()
    if not rating:
        rating = TeamAdvancedRating(team=team)
        db.add(rating)
        db.commit()
        db.refresh(rating)
    return rating


def _update_form_metrics(
    db: Session,
    team: str,
    won: bool,
    goals_for: int,
    goals_against: int,
    venue: VenueType,
    match_date: datetime
):
    """Update team form metrics after match"""
    
    form = db.exec(select(TeamFormMetrics).where(TeamFormMetrics.team == team)).first()
    if not form:
        form = TeamFormMetrics(team=team)
        db.add(form)
    
    # Update result strings
    result_char = "W" if won else ("D" if goals_for == goals_against else "L")
    form.form_last_5 = (result_char + form.form_last_5)[:5]
    form.form_last_10 = (result_char + form.form_last_10)[:10]
    
    # Update counters (last 5)
    if won:
        form.wins_last_5 = min(5, form.wins_last_5 + 1)
        form.current_win_streak += 1
        form.current_loss_streak = 0
    elif goals_for == goals_against:
        form.draws_last_5 = min(5, form.draws_last_5 + 1)
        form.current_win_streak = 0
    else:
        form.losses_last_5 = min(5, form.losses_last_5 + 1)
        form.current_win_streak = 0
        form.current_loss_streak += 1
    
    form.goals_scored_last_5 += goals_for
    form.goals_conceded_last_5 += goals_against
    
    if goals_against == 0:
        form.clean_sheets_last_5 += 1
    
    # Points
    points = 3 if won else (1 if goals_for == goals_against else 0)
    form.points_last_5 += points
    
    # Venue-specific
    if venue == VenueType.HOME:
        if won:
            form.home_wins_last_5 += 1
        form.home_form = (result_char + form.home_form)[:5]
    else:
        if won:
            form.away_wins_last_5 += 1
        form.away_form = (result_char + form.away_form)[:5]
    
    form.updated_at = datetime.utcnow()
    db.add(form)


def _update_h2h_record(
    db: Session,
    team1: str,
    team2: str,
    score1: int,
    score2: int,
    match_date: datetime
):
    """Update head-to-head record"""
    
    h2h = db.exec(
        select(HeadToHeadHistory).where(
            ((HeadToHeadHistory.team1 == team1) & (HeadToHeadHistory.team2 == team2)) |
            ((HeadToHeadHistory.team1 == team2) & (HeadToHeadHistory.team2 == team1))
        )
    ).first()
    
    if not h2h:
        h2h = HeadToHeadHistory(team1=team1, team2=team2)
        db.add(h2h)
    
    h2h.total_matches += 1
    
    # Normalize to h2h.team1 perspective
    if h2h.team1 == team1:
        h2h.team1_goals_total += score1
        h2h.team2_goals_total += score2
        if score1 > score2:
            h2h.team1_wins += 1
            winner = team1
        elif score2 > score1:
            h2h.team2_wins += 1
            winner = team2
        else:
            h2h.draws += 1
            winner = "draw"
    else:
        h2h.team1_goals_total += score2
        h2h.team2_goals_total += score1
        if score2 > score1:
            h2h.team1_wins += 1
            winner = team2
        elif score1 > score2:
            h2h.team2_wins += 1
            winner = team1
        else:
            h2h.draws += 1
            winner = "draw"
    
    h2h.last_match_date = match_date
    h2h.last_match_score = f"{score1}-{score2}"
    h2h.last_match_winner = winner
    
    db.add(h2h)


def _classify_momentum(form: TeamFormMetrics) -> str:
    """Classify team momentum"""
    if form.current_win_streak >= 4:
        return "strong"
    elif form.current_win_streak >= 2:
        return "good"
    elif form.current_loss_streak >= 3:
        return "crisis"
    elif form.points_last_5 <= 5:
        return "poor"
    else:
        return "neutral"


def _get_result_for_team(match: Match, team: str) -> str:
    """Get match result from team perspective"""
    if match.team1 == team:
        if match.score1 > match.score2:
            return "W"
        elif match.score1 < match.score2:
            return "L"
        else:
            return "D"
    else:
        if match.score2 > match.score1:
            return "W"
        elif match.score2 < match.score1:
            return "L"
        else:
            return "D"
