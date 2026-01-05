"""
Advanced Prediction Routes with Caching and Enhanced Features
"""

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select, create_engine
from typing import Optional, List
import os
import json
from datetime import datetime, timedelta

from .models import Event, Player, Match, TeamRating
from .bayesian_model import BayesianFootballModel

router = APIRouter(prefix="/api", tags=["predictions"])

# Global state with caching
bayesian_model = BayesianFootballModel()
model_fitted = False
last_training_time = None
prediction_cache = {}
CACHE_DURATION_MINUTES = 15

# Engine
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/sports")
engine = create_engine(DATABASE_URL)


def ensure_model_fitted(force_retrain: bool = False):
    """
    Ensure model is trained with latest data
    Includes intelligent caching to avoid unnecessary retraining
    """
    global model_fitted, last_training_time
    
    # Check if we need to retrain
    if model_fitted and not force_retrain and last_training_time:
        time_since_training = (datetime.now() - last_training_time).total_seconds() / 60
        if time_since_training < 30:  # Retrain max every 30 minutes
            return
    
    with Session(engine) as session:
        # Load historical matches
        matches = session.exec(select(Match)).all()
        
        # Load current events (treat as potential future training data)
        events = session.exec(select(Event)).all()
        
        # Load player data for team quality assessment
        players = session.exec(select(Player)).all()

        # Load TrueSkill ratings
        ratings = session.exec(select(TeamRating)).all()
        ratings_dict = {r.team: r.mu for r in ratings}
        
        # Set ratings in model
        if ratings_dict:
            bayesian_model.set_trueskill_ratings(ratings_dict)
        
        # Prepare training data
        training_matches = []
        
        # Add historical match data from Match table
        for match in matches:
            if match.score1 is not None and match.score2 is not None:
                training_matches.append({
                    'team1': match.team1 or 'Unknown',
                    'team2': match.team2 or 'Unknown',
                    'home_score': match.score1,
                    'away_score': match.score2,
                    'date': match.date or datetime.now().isoformat(),
                    'league': match.league or 'default'
                })
        
        # Add synthetic data if insufficient historical data
        if len(training_matches) < 10:
            training_matches.extend(_generate_synthetic_training_data())
        
        # Prepare player data
        player_data = []
        for player in players:
            player_data.append({
                'team': player.team,
                'name': player.name,
                'attack': player.attack,
                'defense': player.defense,
                'speed': player.speed,
                'strength': player.strength,
                'dexterity': player.dexterity,
                'stamina': player.stamina
            })
        
        try:
            # Train model with player integration
            bayesian_model.fit(training_matches, player_data=player_data, draws=1000, tune=1000)
            model_fitted = True
            last_training_time = datetime.now()
            
            # Clear prediction cache after retraining
            prediction_cache.clear()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")


def _generate_synthetic_training_data() -> List[dict]:
    """Generate realistic synthetic training data for better model initialization"""
    synthetic_matches = []
    
    # Common teams with realistic score distributions
    teams = [
        ('PSG', 'Lyon'), ('Manchester United', 'Liverpool'), 
        ('Real Madrid', 'Barcelona'), ('Bayern Munich', 'Borussia Dortmund'),
        ('Arsenal', 'Chelsea'), ('Inter Milan', 'AC Milan'),
        ('Atletico Madrid', 'Sevilla'), ('Juventus', 'Napoli')
    ]
    
    import random
    random.seed(42)
    
    for _ in range(50):
        team1, team2 = random.choice(teams)
        
        # Realistic score distribution (most matches are low-scoring)
        home_score = random.choices([0, 1, 2, 3, 4], weights=[10, 30, 35, 20, 5])[0]
        away_score = random.choices([0, 1, 2, 3], weights=[15, 35, 30, 20])[0]
        
        date = (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        
        synthetic_matches.append({
            'team1': team1,
            'team2': team2,
            'home_score': home_score,
            'away_score': away_score,
            'date': date
        })
    
    return synthetic_matches


def _get_cached_prediction(team1: str, team2: str) -> Optional[dict]:
    """Get cached prediction if still valid"""
    cache_key = f"{team1}_vs_{team2}"
    
    if cache_key in prediction_cache:
        cached = prediction_cache[cache_key]
        cache_time = datetime.fromisoformat(cached['cached_at'])
        
        if (datetime.now() - cache_time).total_seconds() / 60 < CACHE_DURATION_MINUTES:
            cached['from_cache'] = True
            return cached
    
    return None


def _cache_prediction(team1: str, team2: str, prediction: dict):
    """Cache prediction result"""
    cache_key = f"{team1}_vs_{team2}"
    prediction['cached_at'] = datetime.now().isoformat()
    prediction_cache[cache_key] = prediction


@router.api_route("/predict-match", methods=["GET", "POST"])
async def predict_match(
    team1: str = Query(..., description="Home team name"),
    team2: str = Query(..., description="Away team name"),
    use_cache: bool = Query(True, description="Use cached predictions if available"),
    include_h2h: bool = Query(True, description="Include head-to-head analysis")
):
    """
    Predict match outcome with comprehensive Bayesian analysis
    
    Returns:
    - Outcome probabilities (win/draw/loss)
    - Betting odds with bookmaker margin
    - Expected goals with confidence intervals
    - Most likely scores
    - Over/under predictions
    - Both teams to score probability
    - AI recommendation
    - Team form and statistics
    """
    try:
        # Check cache first
        if use_cache:
            cached = _get_cached_prediction(team1, team2)
            if cached:
                return cached
        
        # Ensure model is trained
        ensure_model_fitted()
        
        # Get prediction
        result = bayesian_model.predict_match(team1, team2, n_samples=10000, include_h2h=include_h2h)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Cache the result
        _cache_prediction(team1, team2, result)
        result['from_cache'] = False
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/team-stats")
async def get_team_stats(team: Optional[str] = Query(None, description="Specific team name (optional)")):
    """
    Get comprehensive team statistics
    
    Returns:
    - Match records (W/D/L)
    - Goals statistics
    - Home/away performance
    - Strength ratings
    - Recent form
    - Player quality metrics
    """
    try:
        ensure_model_fitted()
        
        all_stats = bayesian_model.get_team_stats()
        
        if 'error' in all_stats:
            raise HTTPException(status_code=400, detail=all_stats['error'])
        
        if team:
            if team not in all_stats:
                raise HTTPException(status_code=404, detail=f"Team '{team}' not found")
            return {team: all_stats[team]}
        
        return all_stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get team stats: {str(e)}")


@router.get("/head-to-head")
async def get_head_to_head(
    team1: str = Query(..., description="First team"),
    team2: str = Query(..., description="Second team")
):
    """
    Get head-to-head statistics between two teams
    
    Returns:
    - Historical match results
    - Win/draw/loss record
    - Average goals
    - Recent meetings
    """
    try:
        ensure_model_fitted()
        
        result = bayesian_model.get_head_to_head(team1, team2)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get H2H stats: {str(e)}")


@router.post("/train-model")
async def train_model(force: bool = Query(False, description="Force retrain even if recently trained")):
    """
    Manually trigger model retraining
    
    Use this after:
    - Adding new match results
    - Updating player data
    - Significant data changes
    """
    global model_fitted, last_training_time
    
    try:
        previous_training = last_training_time
        
        model_fitted = False
        ensure_model_fitted(force_retrain=True)
        
        return {
            "status": "success",
            "message": "Model retrained successfully",
            "previous_training": previous_training.isoformat() if previous_training else None,
            "current_training": last_training_time.isoformat(),
            "cache_cleared": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/model-info")
async def get_model_info():
    """
    Get information about the current model state
    
    Returns:
    - Is model fitted
    - Last training time
    - Number of teams in model
    - Cache status
    - Model configuration
    """
    try:
        ensure_model_fitted()
        
        return {
            "is_fitted": model_fitted,
            "last_training": last_training_time.isoformat() if last_training_time else None,
            "teams_count": len(bayesian_model.team_stats),
            "teams": list(bayesian_model.team_stats.keys()),
            "cache_size": len(prediction_cache),
            "cache_duration_minutes": CACHE_DURATION_MINUTES,
            "model_config": {
                "global_avg_goals": bayesian_model.global_avg_goals,
                "home_advantage": bayesian_model.home_advantage,
                "sample_size": 10000
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-tournament")
async def predict_tournament(matches: List[dict]):
    """
    Predict outcomes for multiple matches (tournament mode)
    
    Request body:
    [
        {"team1": "PSG", "team2": "Lyon"},
        {"team1": "Real Madrid", "team2": "Barcelona"}
    ]
    
    Returns list of predictions for all matches
    """
    try:
        ensure_model_fitted()
        
        predictions = []
        for match in matches:
            team1 = match.get('team1')
            team2 = match.get('team2')
            
            if not team1 or not team2:
                predictions.append({
                    'error': 'Missing team names',
                    'match': match
                })
                continue
            
            # Check cache
            cached = _get_cached_prediction(team1, team2)
            if cached:
                predictions.append(cached)
            else:
                result = bayesian_model.predict_match(team1, team2)
                if 'error' not in result:
                    _cache_prediction(team1, team2, result)
                predictions.append(result)
        
        return {
            "tournament_predictions": predictions,
            "total_matches": len(predictions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tournament prediction failed: {str(e)}")


@router.delete("/clear-cache")
async def clear_prediction_cache():
    """Clear all cached predictions"""
    cache_size = len(prediction_cache)
    prediction_cache.clear()
    
    return {
        "status": "success",
        "message": f"Cleared {cache_size} cached predictions",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/export-model")
async def export_model():
    """Export model state for persistence or analysis"""
    try:
        ensure_model_fitted()
        
        model_state = bayesian_model.export_model_state()
        
        return {
            "model_state": json.loads(model_state),
            "export_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

