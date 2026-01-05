"""
Opta-Level Advanced AI Prediction Engine
Incorporates form, venue effects, head-to-head, and comprehensive match statistics
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import numpy as np
from scipy.stats import poisson, norm, beta as beta_dist
from sqlmodel import Session, select

from .trueskill_rating import TeamSkill, expected_outcome_probabilities, TRUESKILL_ENV
from .models import TeamRating, Match
from .models_advanced import (
    TeamFormMetrics, MatchContext, TeamAdvancedRating, 
    MatchStatistics, HeadToHeadHistory
)


@dataclass
class OptaMatchPrediction:
    """Comprehensive Opta-level match prediction"""
    
    # Basic Info
    team1: str
    team2: str
    match_date: Optional[datetime] = None
    venue: str = "home"  # home, away, neutral
    
    # Ratings
    team1_rating: TeamSkill = None
    team2_rating: TeamSkill = None
    team1_rating_home: Optional[TeamSkill] = None
    team2_rating_away: Optional[TeamSkill] = None
    
    # Core Probabilities (Form-Weighted)
    team1_win_prob: float = 0.0
    draw_prob: float = 0.0
    team2_win_prob: float = 0.0
    
    # Expected Goals (xG)
    team1_xg: float = 0.0
    team2_xg: float = 0.0
    team1_xg_range: Tuple[float, float] = (0.0, 0.0)  # (min, max) 90% CI
    team2_xg_range: Tuple[float, float] = (0.0, 0.0)
    
    # Score Predictions
    most_likely_scores: List[Dict] = field(default_factory=list)
    correct_score_probs: Dict[str, float] = field(default_factory=dict)
    
    # Betting Markets
    over_under_1_5: Dict[str, float] = field(default_factory=dict)
    over_under_2_5: Dict[str, float] = field(default_factory=dict)
    over_under_3_5: Dict[str, float] = field(default_factory=dict)
    both_teams_score_prob: float = 0.0
    
    # Margin Markets
    team1_win_to_nil_prob: float = 0.0
    team2_win_to_nil_prob: float = 0.0
    team1_win_by_2_plus: float = 0.0
    team2_win_by_2_plus: float = 0.0
    
    # Half-Time Predictions
    ht_team1_win_prob: float = 0.0
    ht_draw_prob: float = 0.0
    ht_team2_win_prob: float = 0.0
    ht_ft_predictions: Dict[str, float] = field(default_factory=dict)  # "W-W", "D-W", etc.
    
    # Advanced Metrics
    upset_probability: float = 0.0  # Probability of underdog winning
    expected_goal_difference: float = 0.0
    predicted_possession_split: Tuple[float, float] = (50.0, 50.0)
    expected_shots_on_target: Tuple[int, int] = (0, 0)
    expected_corners: Tuple[int, int] = (0, 0)
    
    # Form Factors
    team1_form_factor: float = 1.0
    team2_form_factor: float = 1.0
    team1_momentum: str = "neutral"  # "strong", "good", "neutral", "poor", "crisis"
    team2_momentum: str = "neutral"
    
    # Context Factors
    venue_advantage: float = 0.0  # Home advantage boost
    h2h_factor: float = 0.0  # Head-to-head psychological advantage
    rest_advantage: float = 0.0  # Rest days differential impact
    importance_factor: float = 1.0  # Match importance multiplier
    
    # Confidence & Quality
    prediction_confidence: float = 0.0
    data_quality_score: float = 0.0  # 0-100, based on available data
    model_uncertainty: float = 0.0
    
    # Odds (Fair & Offered)
    fair_odds_team1: float = 0.0
    fair_odds_draw: float = 0.0
    fair_odds_team2: float = 0.0
    bookmaker_margin: float = 0.05
    
    # Recommendations
    value_bets: List[Dict] = field(default_factory=list)
    top_recommendation: Optional[str] = None
    confidence_level: str = "MEDIUM"  # LOW, MEDIUM, HIGH, VERY_HIGH
    
    # Simulation Details
    simulations_run: int = 0
    monte_carlo_variance: float = 0.0


class OptaAIEngine:
    """Advanced AI Engine with Opta-level analytics"""
    
    def __init__(self, db_session: Session):
        self.session = db_session
        self.home_advantage_boost = 0.3  # Home team xG boost
        self.form_weight_decay = 0.15  # Exponential decay for older matches
        
    def predict_match(
        self,
        team1: str,
        team2: str,
        venue: str = "home",
        match_date: Optional[datetime] = None,
        n_simulations: int = 20000,
        use_advanced_features: bool = True,
    ) -> OptaMatchPrediction:
        """Generate comprehensive Opta-level match prediction"""
        
        prediction = OptaMatchPrediction(
            team1=team1,
            team2=team2,
            match_date=match_date or datetime.utcnow(),
            venue=venue,
            simulations_run=n_simulations,
        )
        
        # 1. Load team ratings (with venue splits)
        team1_adv = self._get_advanced_rating(team1)
        team2_adv = self._get_advanced_rating(team2)
        
        prediction.team1_rating = TeamSkill(team1, team1_adv.mu_overall, team1_adv.sigma_overall)
        prediction.team2_rating = TeamSkill(team2, team2_adv.mu_overall, team2_adv.sigma_overall)
        
        if venue == "home":
            prediction.team1_rating_home = TeamSkill(team1, team1_adv.mu_home, team1_adv.sigma_home)
            prediction.team2_rating_away = TeamSkill(team2, team2_adv.mu_away, team2_adv.sigma_away)
            active_rating_1 = prediction.team1_rating_home
            active_rating_2 = prediction.team2_rating_away
        elif venue == "away":
            prediction.team1_rating_home = TeamSkill(team1, team1_adv.mu_away, team1_adv.sigma_away)
            prediction.team2_rating_away = TeamSkill(team2, team2_adv.mu_home, team2_adv.sigma_home)
            active_rating_1 = prediction.team1_rating_home
            active_rating_2 = prediction.team2_rating_away
        else:  # neutral
            active_rating_1 = prediction.team1_rating
            active_rating_2 = prediction.team2_rating
        
        # 2. Calculate base probabilities from TrueSkill
        base_probs = expected_outcome_probabilities(active_rating_1, active_rating_2)
        
        # 3. Load form metrics and apply form weighting
        if use_advanced_features:
            team1_form = self._get_form_metrics(team1)
            team2_form = self._get_form_metrics(team2)
            
            prediction.team1_form_factor = self._calculate_form_factor(team1_form, venue == "home")
            prediction.team2_form_factor = self._calculate_form_factor(team2_form, venue == "away")
            
            prediction.team1_momentum = self._classify_momentum(team1_form)
            prediction.team2_momentum = self._classify_momentum(team2_form)
            
            # Adjust probabilities based on form
            adjusted_probs = self._apply_form_adjustment(
                base_probs,
                prediction.team1_form_factor,
                prediction.team2_form_factor
            )
        else:
            adjusted_probs = base_probs
            prediction.team1_form_factor = 1.0
            prediction.team2_form_factor = 1.0
        
        prediction.team1_win_prob = adjusted_probs["team1_win"]
        prediction.draw_prob = adjusted_probs["draw"]
        prediction.team2_win_prob = adjusted_probs["team2_win"]
        
        # 4. Calculate expected goals (xG) with advanced factors
        skill_diff = active_rating_1.mu - active_rating_2.mu
        base_xg_1, base_xg_2 = self._skill_to_expected_goals(skill_diff, venue)
        
        # Apply form multipliers to xG
        prediction.team1_xg = base_xg_1 * prediction.team1_form_factor
        prediction.team2_xg = base_xg_2 * prediction.team2_form_factor
        
        # Calculate xG confidence intervals
        prediction.team1_xg_range = (
            max(0.3, prediction.team1_xg - 0.5),
            min(4.0, prediction.team1_xg + 0.5)
        )
        prediction.team2_xg_range = (
            max(0.3, prediction.team2_xg - 0.5),
            min(4.0, prediction.team2_xg + 0.5)
        )
        
        # 5. Run Monte Carlo score simulation
        score_distribution = self._monte_carlo_scores(
            prediction.team1_xg,
            prediction.team2_xg,
            n_simulations
        )
        
        prediction.most_likely_scores = self._extract_top_scores(score_distribution, top_n=15)
        prediction.correct_score_probs = {
            f"{s['home_goals']}-{s['away_goals']}": s['probability']
            for s in prediction.most_likely_scores[:25]
        }
        
        # 6. Calculate betting markets
        prediction.over_under_1_5 = self._calculate_over_under(score_distribution, 1.5)
        prediction.over_under_2_5 = self._calculate_over_under(score_distribution, 2.5)
        prediction.over_under_3_5 = self._calculate_over_under(score_distribution, 3.5)
        prediction.both_teams_score_prob = self._btts_probability(score_distribution)
        
        # Margin markets
        prediction.team1_win_to_nil_prob = self._win_to_nil_prob(score_distribution, "team1")
        prediction.team2_win_to_nil_prob = self._win_to_nil_prob(score_distribution, "team2")
        prediction.team1_win_by_2_plus = self._win_by_margin_prob(score_distribution, "team1", 2)
        prediction.team2_win_by_2_plus = self._win_by_margin_prob(score_distribution, "team2", 2)
        
        # 7. Half-time predictions
        ht_xg_1 = prediction.team1_xg * 0.45  # ~45% of goals in first half
        ht_xg_2 = prediction.team2_xg * 0.45
        ht_scores = self._monte_carlo_scores(ht_xg_1, ht_xg_2, n_simulations // 2)
        
        ht_probs = self._outcome_probabilities_from_scores(ht_scores)
        prediction.ht_team1_win_prob = ht_probs["team1_win"]
        prediction.ht_draw_prob = ht_probs["draw"]
        prediction.ht_team2_win_prob = ht_probs["team2_win"]
        
        prediction.ht_ft_predictions = self._calculate_ht_ft_markets(
            ht_probs, adjusted_probs
        )
        
        # 8. Advanced contextual factors
        if use_advanced_features:
            h2h = self._get_h2h_record(team1, team2)
            prediction.h2h_factor = self._calculate_h2h_advantage(h2h, team1)
            
            prediction.venue_advantage = self.home_advantage_boost if venue == "home" else 0.0
            prediction.importance_factor = 1.0  # Could be loaded from match_context
        
        # 9. Upset probability (when underdog has > 25% chance)
        favorite_prob = max(prediction.team1_win_prob, prediction.team2_win_prob)
        underdog_prob = min(prediction.team1_win_prob, prediction.team2_win_prob)
        prediction.upset_probability = underdog_prob if favorite_prob > 0.5 else 0.0
        
        # 10. Expected stats (possession, shots, corners)
        prediction.predicted_possession_split = self._predict_possession(
            active_rating_1.mu, active_rating_2.mu
        )
        prediction.expected_shots_on_target = self._predict_shots_on_target(
            prediction.team1_xg, prediction.team2_xg
        )
        prediction.expected_corners = self._predict_corners(
            prediction.team1_xg, prediction.team2_xg
        )
        
        # 11. Fair odds calculation
        prediction.fair_odds_team1 = 1.0 / prediction.team1_win_prob if prediction.team1_win_prob > 0 else 999.0
        prediction.fair_odds_draw = 1.0 / prediction.draw_prob if prediction.draw_prob > 0 else 999.0
        prediction.fair_odds_team2 = 1.0 / prediction.team2_win_prob if prediction.team2_win_prob > 0 else 999.0
        
        # Apply bookmaker margin
        margin_factor = 1.0 - prediction.bookmaker_margin
        prediction.fair_odds_team1 *= margin_factor
        prediction.fair_odds_draw *= margin_factor
        prediction.fair_odds_team2 *= margin_factor
        
        # 12. Confidence & quality scoring
        prediction.prediction_confidence = self._calculate_confidence(
            active_rating_1, active_rating_2,
            prediction.team1_form_factor, prediction.team2_form_factor,
            team1_adv.matches_played, team2_adv.matches_played
        )
        
        prediction.model_uncertainty = (active_rating_1.sigma + active_rating_2.sigma) / 2
        prediction.confidence_level = self._classify_confidence(prediction.prediction_confidence)
        
        # Data quality (0-100 score based on available metrics)
        prediction.data_quality_score = self._assess_data_quality(
            team1_adv, team2_adv, use_advanced_features
        )
        
        # 13. Value bet detection
        prediction.value_bets = self._identify_value_bets(prediction)
        
        # 14. Top recommendation
        prediction.top_recommendation = self._generate_recommendation(prediction)
        
        return prediction
    
    def _get_advanced_rating(self, team: str) -> TeamAdvancedRating:
        """Get or create advanced rating for team"""
        stmt = select(TeamAdvancedRating).where(TeamAdvancedRating.team == team)
        rating = self.session.exec(stmt).first()
        
        if not rating:
            rating = TeamAdvancedRating(team=team)
            self.session.add(rating)
            self.session.commit()
            self.session.refresh(rating)
        
        return rating
    
    def _get_form_metrics(self, team: str) -> Optional[TeamFormMetrics]:
        """Get team form metrics"""
        stmt = select(TeamFormMetrics).where(TeamFormMetrics.team == team)
        return self.session.exec(stmt).first()
    
    def _get_h2h_record(self, team1: str, team2: str) -> Optional[HeadToHeadHistory]:
        """Get head-to-head history"""
        stmt = select(HeadToHeadHistory).where(
            ((HeadToHeadHistory.team1 == team1) & (HeadToHeadHistory.team2 == team2)) |
            ((HeadToHeadHistory.team1 == team2) & (HeadToHeadHistory.team2 == team1))
        )
        return self.session.exec(stmt).first()
    
    def _calculate_form_factor(self, form: Optional[TeamFormMetrics], is_home: bool) -> float:
        """Calculate form adjustment factor (0.7 - 1.3 range)"""
        if not form:
            return 1.0
        
        # Base factor from recent results
        if form.points_last_5 >= 13:  # 4+ wins
            base = 1.25
        elif form.points_last_5 >= 10:  # 3 wins + draw
            base = 1.15
        elif form.points_last_5 >= 7:  # 2 wins
            base = 1.05
        elif form.points_last_5 >= 4:  # 1 win
            base = 0.95
        else:  # Poor form
            base = 0.80
        
        # Venue-specific adjustment
        venue_form = form.home_wins_last_5 if is_home else form.away_wins_last_5
        venue_bonus = (venue_form - 1.5) * 0.05  # ±0.1 range
        
        # Momentum (win streaks)
        if form.current_win_streak >= 3:
            momentum_bonus = 0.1
        elif form.current_loss_streak >= 3:
            momentum_bonus = -0.1
        else:
            momentum_bonus = 0.0
        
        final_factor = base + venue_bonus + momentum_bonus
        return max(0.7, min(1.3, final_factor))  # Clamp to reasonable range
    
    def _classify_momentum(self, form: Optional[TeamFormMetrics]) -> str:
        """Classify team momentum"""
        if not form:
            return "neutral"
        
        if form.current_win_streak >= 4 or form.points_last_5 >= 13:
            return "strong"
        elif form.current_win_streak >= 2 or form.points_last_5 >= 10:
            return "good"
        elif form.current_loss_streak >= 3 or form.points_last_5 <= 3:
            return "crisis"
        elif form.points_last_5 <= 5:
            return "poor"
        else:
            return "neutral"
    
    def _apply_form_adjustment(
        self,
        base_probs: Dict[str, float],
        form1: float,
        form2: float
    ) -> Dict[str, float]:
        """Adjust win probabilities based on form"""
        
        # Form differential
        form_diff = form1 - form2
        
        # Shift probabilities (max ±15% shift)
        shift = form_diff * 0.15
        
        adjusted_p1 = base_probs["team1_win"] + shift
        adjusted_p2 = base_probs["team2_win"] - shift
        adjusted_draw = base_probs["draw"]
        
        # Normalize
        total = adjusted_p1 + adjusted_draw + adjusted_p2
        if total > 0:
            adjusted_p1 /= total
            adjusted_draw /= total
            adjusted_p2 /= total
        
        # Clamp to valid range
        adjusted_p1 = max(0.05, min(0.90, adjusted_p1))
        adjusted_p2 = max(0.05, min(0.90, adjusted_p2))
        adjusted_draw = max(0.05, min(0.40, adjusted_draw))
        
        # Renormalize
        total = adjusted_p1 + adjusted_draw + adjusted_p2
        return {
            "team1_win": adjusted_p1 / total,
            "draw": adjusted_draw / total,
            "team2_win": adjusted_p2 / total,
        }
    
    def _skill_to_expected_goals(self, skill_diff: float, venue: str) -> Tuple[float, float]:
        """Convert skill difference to expected goals"""
        # Base xG calculation
        base_xg_home = 1.5 + (skill_diff / 12)  # More sensitive scaling
        base_xg_away = 1.5 - (skill_diff / 12)
        
        # Apply home advantage
        if venue == "home":
            base_xg_home += self.home_advantage_boost
        elif venue == "away":
            base_xg_away += self.home_advantage_boost
        
        # Clamp to realistic range
        xg1 = max(0.3, min(3.5, base_xg_home))
        xg2 = max(0.3, min(3.5, base_xg_away))
        
        return xg1, xg2
    
    def _monte_carlo_scores(
        self,
        xg1: float,
        xg2: float,
        n_sims: int
    ) -> Dict[Tuple[int, int], int]:
        """Run Monte Carlo simulation for score distribution"""
        
        # Sample from Poisson distributions
        goals1 = np.random.poisson(xg1, n_sims)
        goals2 = np.random.poisson(xg2, n_sims)
        
        # Count score frequencies
        score_counts = {}
        for g1, g2 in zip(goals1, goals2):
            # Cap at 7 goals per team
            g1 = min(g1, 7)
            g2 = min(g2, 7)
            score = (g1, g2)
            score_counts[score] = score_counts.get(score, 0) + 1
        
        return score_counts
    
    def _extract_top_scores(
        self,
        score_distribution: Dict[Tuple[int, int], int],
        top_n: int = 15
    ) -> List[Dict]:
        """Extract most likely scores"""
        
        total_sims = sum(score_distribution.values())
        
        scores = [
            {
                "score": f"{s[0]}-{s[1]}",
                "home_goals": s[0],
                "away_goals": s[1],
                "probability": count / total_sims,
                "count": count,
            }
            for s, count in score_distribution.items()
        ]
        
        scores.sort(key=lambda x: x["probability"], reverse=True)
        return scores[:top_n]
    
    def _calculate_over_under(
        self,
        score_distribution: Dict[Tuple[int, int], int],
        line: float
    ) -> Dict[str, float]:
        """Calculate over/under probabilities"""
        
        total = sum(score_distribution.values())
        over_count = sum(
            count for (g1, g2), count in score_distribution.items()
            if (g1 + g2) > line
        )
        
        over_prob = over_count / total if total > 0 else 0.0
        under_prob = 1.0 - over_prob
        
        return {"over": over_prob, "under": under_prob}
    
    def _btts_probability(self, score_distribution: Dict[Tuple[int, int], int]) -> float:
        """Both teams to score probability"""
        total = sum(score_distribution.values())
        btts_count = sum(
            count for (g1, g2), count in score_distribution.items()
            if g1 > 0 and g2 > 0
        )
        return btts_count / total if total > 0 else 0.0
    
    def _win_to_nil_prob(
        self,
        score_distribution: Dict[Tuple[int, int], int],
        team: str
    ) -> float:
        """Win to nil probability"""
        total = sum(score_distribution.values())
        
        if team == "team1":
            count = sum(c for (g1, g2), c in score_distribution.items() if g1 > g2 and g2 == 0)
        else:
            count = sum(c for (g1, g2), c in score_distribution.items() if g2 > g1 and g1 == 0)
        
        return count / total if total > 0 else 0.0
    
    def _win_by_margin_prob(
        self,
        score_distribution: Dict[Tuple[int, int], int],
        team: str,
        margin: int
    ) -> float:
        """Win by N+ goals probability"""
        total = sum(score_distribution.values())
        
        if team == "team1":
            count = sum(c for (g1, g2), c in score_distribution.items() if (g1 - g2) >= margin)
        else:
            count = sum(c for (g1, g2), c in score_distribution.items() if (g2 - g1) >= margin)
        
        return count / total if total > 0 else 0.0
    
    def _outcome_probabilities_from_scores(
        self,
        score_distribution: Dict[Tuple[int, int], int]
    ) -> Dict[str, float]:
        """Calculate win/draw/loss from score distribution"""
        total = sum(score_distribution.values())
        
        team1_wins = sum(c for (g1, g2), c in score_distribution.items() if g1 > g2)
        draws = sum(c for (g1, g2), c in score_distribution.items() if g1 == g2)
        team2_wins = sum(c for (g1, g2), c in score_distribution.items() if g2 > g1)
        
        return {
            "team1_win": team1_wins / total if total > 0 else 0.0,
            "draw": draws / total if total > 0 else 0.0,
            "team2_win": team2_wins / total if total > 0 else 0.0,
        }
    
    def _calculate_ht_ft_markets(
        self,
        ht_probs: Dict[str, float],
        ft_probs: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate half-time/full-time probabilities"""
        
        # Simplified independent model (could be enhanced with correlation)
        return {
            "W-W": ht_probs["team1_win"] * ft_probs["team1_win"],
            "W-D": ht_probs["team1_win"] * ft_probs["draw"],
            "W-L": ht_probs["team1_win"] * ft_probs["team2_win"],
            "D-W": ht_probs["draw"] * ft_probs["team1_win"],
            "D-D": ht_probs["draw"] * ft_probs["draw"],
            "D-L": ht_probs["draw"] * ft_probs["team2_win"],
            "L-W": ht_probs["team2_win"] * ft_probs["team1_win"],
            "L-D": ht_probs["team2_win"] * ft_probs["draw"],
            "L-L": ht_probs["team2_win"] * ft_probs["team2_win"],
        }
    
    def _calculate_h2h_advantage(self, h2h: Optional[HeadToHeadHistory], team: str) -> float:
        """Calculate psychological advantage from head-to-head"""
        if not h2h or h2h.total_matches < 5:
            return 0.0
        
        if h2h.team1 == team:
            win_rate = h2h.team1_wins / h2h.total_matches
        else:
            win_rate = h2h.team2_wins / h2h.total_matches
        
        # Convert to advantage factor (-0.1 to +0.1)
        return (win_rate - 0.5) * 0.2
    
    def _predict_possession(self, mu1: float, mu2: float) -> Tuple[float, float]:
        """Predict possession split"""
        skill_diff = mu1 - mu2
        
        # Base 50-50, adjust by skill (max ±20%)
        poss1 = 50.0 + (skill_diff / 15) * 10
        poss1 = max(30.0, min(70.0, poss1))
        poss2 = 100.0 - poss1
        
        return (poss1, poss2)
    
    def _predict_shots_on_target(self, xg1: float, xg2: float) -> Tuple[int, int]:
        """Predict shots on target"""
        # Rule of thumb: ~3-4 shots on target per goal
        sot1 = int(xg1 * 3.5 + 1)
        sot2 = int(xg2 * 3.5 + 1)
        return (sot1, sot2)
    
    def _predict_corners(self, xg1: float, xg2: float) -> Tuple[int, int]:
        """Predict corner kicks"""
        # Rule of thumb: ~4-6 corners per goal
        corners1 = int(xg1 * 5 + 2)
        corners2 = int(xg2 * 5 + 2)
        return (corners1, corners2)
    
    def _calculate_confidence(
        self,
        rating1: TeamSkill,
        rating2: TeamSkill,
        form1: float,
        form2: float,
        matches1: int,
        matches2: int
    ) -> float:
        """Calculate overall prediction confidence"""
        
        # Rating certainty (lower sigma = higher confidence)
        avg_sigma = (rating1.sigma + rating2.sigma) / 2
        rating_confidence = 1.0 - (avg_sigma / 8.333)  # 0-1 scale
        
        # Form confidence (closer to 1.0 = more stable)
        form_stability = 1.0 - abs(1.0 - (form1 + form2) / 2) / 0.3  # 0-1 scale
        
        # Experience (more matches = more confidence)
        min_matches = min(matches1, matches2)
        experience_factor = min(1.0, min_matches / 15)  # Saturates at 15 matches
        
        # Outcome clarity (probability separation)
        max_prob = max(
            expected_outcome_probabilities(rating1, rating2).values()
        )
        outcome_clarity = (max_prob - 0.333) / 0.667  # Normalize to 0-1
        
        # Weighted average
        confidence = (
            rating_confidence * 0.35 +
            form_stability * 0.20 +
            experience_factor * 0.20 +
            outcome_clarity * 0.25
        )
        
        return max(0.0, min(1.0, confidence))
    
    def _classify_confidence(self, confidence: float) -> str:
        """Classify confidence level"""
        if confidence >= 0.80:
            return "VERY_HIGH"
        elif confidence >= 0.65:
            return "HIGH"
        elif confidence >= 0.45:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _assess_data_quality(
        self,
        rating1: TeamAdvancedRating,
        rating2: TeamAdvancedRating,
        advanced_enabled: bool
    ) -> float:
        """Assess data quality score (0-100)"""
        
        score = 50.0  # Base score
        
        # Rating data quality
        if rating1.matches_played >= 10:
            score += 15.0
        elif rating1.matches_played >= 5:
            score += 7.0
        
        if rating2.matches_played >= 10:
            score += 15.0
        elif rating2.matches_played >= 5:
            score += 7.0
        
        # Advanced features
        if advanced_enabled:
            score += 20.0
        
        return min(100.0, score)
    
    def _identify_value_bets(self, prediction: OptaMatchPrediction) -> List[Dict]:
        """Identify value betting opportunities"""
        
        # Placeholder for value bet detection
        # Would compare fair odds vs market odds to find +EV bets
        value_bets = []
        
        # Example: If high confidence and clear favorite
        if prediction.confidence_level in ["HIGH", "VERY_HIGH"]:
            if prediction.team1_win_prob > 0.60:
                value_bets.append({
                    "market": "Home Win",
                    "fair_odds": prediction.fair_odds_team1,
                    "confidence": prediction.confidence_level,
                    "value": "HIGH",
                })
            elif prediction.team2_win_prob > 0.60:
                value_bets.append({
                    "market": "Away Win",
                    "fair_odds": prediction.fair_odds_team2,
                    "confidence": prediction.confidence_level,
                    "value": "HIGH",
                })
        
        # Over/Under value
        if prediction.over_under_2_5["over"] > 0.65:
            value_bets.append({
                "market": "Over 2.5 Goals",
                "probability": prediction.over_under_2_5["over"],
                "confidence": "MEDIUM",
                "value": "GOOD",
            })
        
        return value_bets
    
    def _generate_recommendation(self, prediction: OptaMatchPrediction) -> str:
        """Generate human-readable recommendation"""
        
        # Find strongest prediction
        max_prob = max(
            prediction.team1_win_prob,
            prediction.draw_prob,
            prediction.team2_win_prob
        )
        
        if max_prob == prediction.team1_win_prob:
            outcome = f"{prediction.team1} to win"
            prob_pct = prediction.team1_win_prob * 100
            odds = prediction.fair_odds_team1
        elif max_prob == prediction.team2_win_prob:
            outcome = f"{prediction.team2} to win"
            prob_pct = prediction.team2_win_prob * 100
            odds = prediction.fair_odds_team2
        else:
            outcome = "Draw"
            prob_pct = prediction.draw_prob * 100
            odds = prediction.fair_odds_draw
        
        # Add xG context
        xg_str = f"xG: {prediction.team1_xg:.2f} - {prediction.team2_xg:.2f}"
        
        # Add form/momentum context
        momentum_note = ""
        if prediction.team1_momentum == "strong" and max_prob == prediction.team1_win_prob:
            momentum_note = " 🔥 Team on hot streak!"
        elif prediction.team2_momentum == "strong" and max_prob == prediction.team2_win_prob:
            momentum_note = " 🔥 Team on hot streak!"
        elif prediction.team1_momentum == "crisis" or prediction.team2_momentum == "crisis":
            momentum_note = " ⚠️ One team in poor form"
        
        # Confidence indicator
        conf_emoji = {
            "VERY_HIGH": "✅",
            "HIGH": "✓",
            "MEDIUM": "→",
            "LOW": "⚠️"
        }
        
        recommendation = (
            f"{conf_emoji.get(prediction.confidence_level, '→')} "
            f"{outcome} ({prob_pct:.1f}% | Fair odds: {odds:.2f}). "
            f"{xg_str}.{momentum_note} "
            f"Confidence: {prediction.confidence_level}."
        )
        
        return recommendation
