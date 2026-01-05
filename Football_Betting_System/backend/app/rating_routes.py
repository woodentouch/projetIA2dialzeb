from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field as PydField
from sqlmodel import Session, select, create_engine
import os

from .models import TeamRating, Match
from .trueskill_rating import TeamSkill, TRUESKILL_ENV, expected_outcome_probabilities, update_ratings_after_match
from .trueskill_ai_engine import TrueSkillAIEngine


router = APIRouter(prefix="/api", tags=["ratings", "ai"])

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/sports")
engine = create_engine(DATABASE_URL)

# Initialize AI engine
ai_engine = TrueSkillAIEngine()


class RatingUpdateRequest(BaseModel):
    team1: str = PydField(..., min_length=1)
    team2: str = PydField(..., min_length=1)
    score1: int = PydField(..., ge=0)
    score2: int = PydField(..., ge=0)
    store_as_match: bool = True


def _get_or_create(session: Session, team: str) -> TeamRating:
    team = team.strip()
    if not team:
        raise HTTPException(status_code=400, detail="Team name cannot be empty")

    existing = session.exec(select(TeamRating).where(TeamRating.team == team)).first()
    if existing:
        return existing

    rating = TRUESKILL_ENV.create_rating()
    tr = TeamRating(team=team, mu=float(rating.mu), sigma=float(rating.sigma), updated_at=datetime.utcnow())
    session.add(tr)
    session.commit()
    session.refresh(tr)
    return tr


@router.get("/ai-predict")
def ai_predict_match(
    team1: str = Query(..., description="Home team name"),
    team2: str = Query(..., description="Away team name"),
    n_simulations: int = Query(10000, ge=1000, le=50000, description="Monte Carlo simulations"),
):
    """
    🤖 AI-Powered Match Prediction using TrueSkill Model
    
    The main AI prediction endpoint - uses TrueSkill ratings to generate:
    - Win/Draw/Loss probabilities
    - Expected goals for both teams
    - Most likely scorelines
    - Over/Under predictions
    - Both teams to score probability
    - Fair betting odds
    - AI recommendation with confidence
    
    This is the core AI engine of the platform!
    """
    if team1.strip() == team2.strip():
        raise HTTPException(status_code=400, detail="team1 and team2 must be different")
    
    with Session(engine) as session:
        r1 = _get_or_create(session, team1)
        r2 = _get_or_create(session, team2)
        
        skill1 = TeamSkill(team=r1.team, mu=r1.mu, sigma=r1.sigma)
        skill2 = TeamSkill(team=r2.team, mu=r2.mu, sigma=r2.sigma)
        
        prediction = ai_engine.predict_match(skill1, skill2, n_simulations=n_simulations)
        
        return {
            "model": "TrueSkill AI Engine v1.0",
            "teams": {
                "home": {
                    "name": prediction.team1,
                    "rating": {
                        "mu": prediction.team1_rating.mu,
                        "sigma": prediction.team1_rating.sigma,
                        "conservative": prediction.team1_rating.mu - 3 * prediction.team1_rating.sigma,
                    }
                },
                "away": {
                    "name": prediction.team2,
                    "rating": {
                        "mu": prediction.team2_rating.mu,
                        "sigma": prediction.team2_rating.sigma,
                        "conservative": prediction.team2_rating.mu - 3 * prediction.team2_rating.sigma,
                    }
                }
            },
            "outcome_probabilities": {
                "home_win": prediction.team1_win_prob,
                "draw": prediction.draw_prob,
                "away_win": prediction.team2_win_prob,
            },
            "goals_prediction": {
                "expected_home_goals": prediction.team1_expected_goals,
                "expected_away_goals": prediction.team2_expected_goals,
                "expected_total_goals": prediction.team1_expected_goals + prediction.team2_expected_goals,
            },
            "betting_odds": {
                "home_odds": prediction.team1_fair_odds,
                "draw_odds": prediction.draw_fair_odds,
                "away_odds": prediction.team2_fair_odds,
            },
            "most_likely_scores": prediction.most_likely_scores[:10],
            "over_under": {
                "over_2.5": prediction.over_under_2_5["over"],
                "under_2.5": prediction.over_under_2_5["under"],
            },
            "both_teams_score": prediction.both_teams_score_prob,
            "confidence": {
                "prediction_confidence": prediction.prediction_confidence,
                "rating_uncertainty": prediction.rating_uncertainty,
                "level": prediction.confidence_level,
            },
            "recommendation": prediction.recommendation,
            "simulations": n_simulations,
        }


@router.get("/ratings")
def list_ratings(
    limit: int = Query(200, ge=1, le=1000),
    sort_by: str = Query("team", regex="^(team|mu|sigma|conservative)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
):
    """List all team ratings with sorting options"""
    with Session(engine) as session:
        query = select(TeamRating)
        
        # Apply sorting
        if sort_by == "mu":
            query = query.order_by(TeamRating.mu.desc() if order == "desc" else TeamRating.mu)
        elif sort_by == "sigma":
            query = query.order_by(TeamRating.sigma.desc() if order == "desc" else TeamRating.sigma)
        elif sort_by == "conservative":
            # Sort by conservative rating (mu - 3*sigma)
            # Note: This requires computed sorting in Python after fetch
            pass
        else:  # team
            query = query.order_by(TeamRating.team.desc() if order == "desc" else TeamRating.team)
        
        rows = session.exec(query.limit(limit)).all()
        
        # Compute conservative and sort if needed
        ratings_data = [
            {
                "team": r.team,
                "mu": r.mu,
                "sigma": r.sigma,
                "conservative": r.mu - 3 * r.sigma,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in rows
        ]
        
        if sort_by == "conservative":
            ratings_data.sort(key=lambda x: x["conservative"], reverse=(order == "desc"))
        
        return {"ratings": ratings_data, "count": len(ratings_data)}


@router.get("/ratings/{team}")
def get_rating(team: str):
    """Get rating for a specific team (auto-creates if not exists)"""
    with Session(engine) as session:
        r = _get_or_create(session, team)
        return {
            "team": r.team,
            "mu": r.mu,
            "sigma": r.sigma,
            "conservative": r.mu - 3 * r.sigma,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }


@router.get("/predict-rating")
def predict_by_rating(
    team1: str = Query(..., description="Home team"),
    team2: str = Query(..., description="Away team"),
):
    """
    Simple TrueSkill probability prediction (lightweight version of /ai-predict)
    
    Returns basic win/draw/loss probabilities based on current ratings.
    For full AI predictions with expected goals and scorelines, use /ai-predict instead.
    """
    if team1.strip() == team2.strip():
        raise HTTPException(status_code=400, detail="team1 and team2 must be different")

    with Session(engine) as session:
        r1 = _get_or_create(session, team1)
        r2 = _get_or_create(session, team2)

        probs = expected_outcome_probabilities(
            TeamSkill(team=r1.team, mu=r1.mu, sigma=r1.sigma),
            TeamSkill(team=r2.team, mu=r2.mu, sigma=r2.sigma),
        )

        return {
            "team1": {"team": r1.team, "mu": r1.mu, "sigma": r1.sigma},
            "team2": {"team": r2.team, "mu": r2.mu, "sigma": r2.sigma},
            "outcome_probabilities": probs,
            "note": "For full AI prediction with expected goals and score probabilities, use /api/ai-predict",
        }


@router.post("/ratings/update")
def update_ratings(payload: RatingUpdateRequest):
    """Update team ratings after a match result"""
    if payload.team1.strip() == payload.team2.strip():
        raise HTTPException(status_code=400, detail="team1 and team2 must be different")

    with Session(engine) as session:
        db1 = _get_or_create(session, payload.team1)
        db2 = _get_or_create(session, payload.team2)

        new1, new2, result = update_ratings_after_match(
            TeamSkill(team=db1.team, mu=db1.mu, sigma=db1.sigma),
            TeamSkill(team=db2.team, mu=db2.mu, sigma=db2.sigma),
            payload.score1,
            payload.score2,
        )

        db1.mu = new1.mu
        db1.sigma = new1.sigma
        db1.updated_at = datetime.utcnow()

        db2.mu = new2.mu
        db2.sigma = new2.sigma
        db2.updated_at = datetime.utcnow()

        session.add(db1)
        session.add(db2)

        if payload.store_as_match:
            match = Match(
                team1=db1.team,
                team2=db2.team,
                score1=payload.score1,
                score2=payload.score2,
                date=datetime.utcnow().isoformat(),
                source="trueskill",
            )
            session.add(match)

        session.commit()

        probs_next = expected_outcome_probabilities(new1, new2)

        return {
            "result": result,
            "team1": {"team": db1.team, "mu": db1.mu, "sigma": db1.sigma},
            "team2": {"team": db2.team, "mu": db2.mu, "sigma": db2.sigma},
            "next_match_probabilities": probs_next,
        }
