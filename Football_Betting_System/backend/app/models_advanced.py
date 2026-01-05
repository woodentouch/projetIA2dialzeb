"""
Advanced Opta-Level Data Models
Comprehensive match statistics, team performance metrics, and contextual data
"""

from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class VenueType(str, Enum):
    HOME = "home"
    AWAY = "away"
    NEUTRAL = "neutral"


class WeatherCondition(str, Enum):
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    WIND = "wind"
    EXTREME = "extreme"


class MatchStatistics(SQLModel, table=True):
    """Opta-level detailed match statistics"""
    __tablename__ = "match_statistics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    team: str = Field(index=True)
    
    # Possession & Ball Control
    possession_pct: Optional[float] = None  # Ball possession %
    passes_total: Optional[int] = None
    passes_completed: Optional[int] = None
    pass_accuracy_pct: Optional[float] = None
    long_balls: Optional[int] = None
    crosses: Optional[int] = None
    
    # Attacking
    shots_total: Optional[int] = None
    shots_on_target: Optional[int] = None
    shots_off_target: Optional[int] = None
    shots_blocked: Optional[int] = None
    big_chances: Optional[int] = None  # Clear goal-scoring opportunities
    big_chances_missed: Optional[int] = None
    expected_goals: Optional[float] = None  # xG
    expected_assists: Optional[float] = None  # xA
    
    # Attacking Zones
    attacks_total: Optional[int] = None
    attacks_dangerous: Optional[int] = None
    touches_in_box: Optional[int] = None
    
    # Defensive
    tackles_total: Optional[int] = None
    tackles_won: Optional[int] = None
    interceptions: Optional[int] = None
    clearances: Optional[int] = None
    blocks: Optional[int] = None
    
    # Duels
    duels_won: Optional[int] = None
    duels_lost: Optional[int] = None
    aerial_duels_won: Optional[int] = None
    aerial_duels_lost: Optional[int] = None
    
    # Discipline
    fouls_committed: Optional[int] = None
    fouls_suffered: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    
    # Set Pieces
    corners: Optional[int] = None
    offsides: Optional[int] = None
    free_kicks: Optional[int] = None
    penalties_scored: Optional[int] = None
    penalties_missed: Optional[int] = None
    
    # Goalkeeper (if applicable)
    saves: Optional[int] = None
    saves_inside_box: Optional[int] = None
    
    # Advanced Metrics
    pressing_intensity: Optional[float] = None  # High press actions per minute
    counter_attacks: Optional[int] = None
    fast_breaks: Optional[int] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TeamFormMetrics(SQLModel, table=True):
    """Rolling form metrics for recent performance"""
    __tablename__ = "team_form_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    team: str = Field(index=True, unique=True)
    
    # Form Windows (Last N matches)
    form_last_5: str = Field(default="")  # e.g., "WWDLW"
    form_last_10: str = Field(default="")
    
    # Recent Performance
    wins_last_5: int = 0
    draws_last_5: int = 0
    losses_last_5: int = 0
    goals_scored_last_5: int = 0
    goals_conceded_last_5: int = 0
    clean_sheets_last_5: int = 0
    
    # Venue-Specific Form
    home_wins_last_5: int = 0
    home_form: str = Field(default="")
    away_wins_last_5: int = 0
    away_form: str = Field(default="")
    
    # Momentum Indicators
    points_last_5: int = 0  # Total points (3 for win, 1 for draw)
    avg_xg_last_5: Optional[float] = None
    avg_xa_conceded_last_5: Optional[float] = None
    
    # Streak Tracking
    current_win_streak: int = 0
    current_unbeaten_streak: int = 0
    current_loss_streak: int = 0
    
    # Rest & Fitness
    days_since_last_match: Optional[int] = None
    matches_in_last_7_days: int = 0
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MatchContext(SQLModel, table=True):
    """Contextual factors affecting match outcome"""
    __tablename__ = "match_context"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True, unique=True)
    
    # Venue Details
    venue_name: Optional[str] = None
    venue_city: Optional[str] = None
    venue_capacity: Optional[int] = None
    attendance: Optional[int] = None
    attendance_pct: Optional[float] = None
    
    # Environmental
    weather: Optional[WeatherCondition] = None
    temperature_celsius: Optional[float] = None
    humidity_pct: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    
    # Match Officials
    referee: Optional[str] = None
    referee_cards_per_game: Optional[float] = None  # Historical avg
    
    # Timing
    kickoff_time: Optional[datetime] = None
    match_week: Optional[int] = None
    competition: Optional[str] = None
    stage: Optional[str] = None  # group, knockout, final, etc.
    
    # Team Context
    team1_injuries: int = 0
    team1_suspensions: int = 0
    team1_days_rest: Optional[int] = None
    team2_injuries: int = 0
    team2_suspensions: int = 0
    team2_days_rest: Optional[int] = None
    
    # Historical
    head_to_head_matches: int = 0
    team1_h2h_wins: int = 0
    team2_h2h_wins: int = 0
    h2h_draws: int = 0
    
    # Stakes
    importance_factor: float = 1.0  # Derby, title decider, etc.
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TeamAdvancedRating(SQLModel, table=True):
    """Enhanced TrueSkill with venue splits and form weighting"""
    __tablename__ = "team_advanced_rating"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    team: str = Field(index=True, unique=True)
    
    # Overall TrueSkill
    mu_overall: float = 25.0
    sigma_overall: float = 8.333
    
    # Venue-Split Ratings
    mu_home: float = 25.0
    sigma_home: float = 8.333
    mu_away: float = 25.0
    sigma_away: float = 8.333
    
    # Attack & Defense Components
    mu_attack: float = 25.0
    sigma_attack: float = 8.333
    mu_defense: float = 25.0
    sigma_defense: float = 8.333
    
    # Performance Metrics
    matches_played: int = 0
    matches_home: int = 0
    matches_away: int = 0
    
    # Volatility (for time decay)
    last_match_date: Optional[datetime] = None
    activity_decay_factor: float = 1.0
    
    # League Context
    league: Optional[str] = None
    league_strength_factor: float = 1.0  # Normalization across leagues
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlayerPerformance(SQLModel, table=True):
    """Individual player performance in a match"""
    __tablename__ = "player_performance"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    
    # Basic Info
    team: str
    minutes_played: int = 0
    position: str
    
    # Goals & Assists
    goals: int = 0
    assists: int = 0
    expected_goals: Optional[float] = None
    expected_assists: Optional[float] = None
    
    # Shooting
    shots: int = 0
    shots_on_target: int = 0
    big_chances_created: int = 0
    
    # Passing
    passes: int = 0
    passes_completed: int = 0
    key_passes: int = 0
    
    # Defensive
    tackles: int = 0
    interceptions: int = 0
    clearances: int = 0
    
    # Duels
    duels_won: int = 0
    aerial_duels_won: int = 0
    
    # Rating
    performance_rating: Optional[float] = None  # 0-10 scale
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HeadToHeadHistory(SQLModel, table=True):
    """Historical head-to-head record between two teams"""
    __tablename__ = "head_to_head_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    team1: str = Field(index=True)
    team2: str = Field(index=True)
    
    # Overall H2H
    total_matches: int = 0
    team1_wins: int = 0
    team2_wins: int = 0
    draws: int = 0
    
    # Goals
    team1_goals_total: int = 0
    team2_goals_total: int = 0
    
    # Recent Form (Last 5 H2H)
    recent_form: str = Field(default="")  # e.g., "12D21" (1=team1, 2=team2, D=draw)
    
    # Venue Splits
    team1_home_wins: int = 0
    team2_away_wins_at_team1: int = 0
    
    # Last Encounter
    last_match_date: Optional[datetime] = None
    last_match_score: Optional[str] = None
    last_match_winner: Optional[str] = None
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
