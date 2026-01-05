"""
TrueSkill AI Prediction Service - Main AI Engine
Combines TrueSkill ratings with match simulation and advanced statistics
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
from scipy.stats import poisson, norm

from .trueskill_rating import TeamSkill, expected_outcome_probabilities, TRUESKILL_ENV


@dataclass
class MatchPrediction:
    """Complete match prediction with probabilities and statistics"""
    team1: str
    team2: str
    team1_rating: TeamSkill
    team2_rating: TeamSkill
    
    # Outcome probabilities
    team1_win_prob: float
    draw_prob: float
    team2_win_prob: float
    
    # Expected goals
    team1_expected_goals: float
    team2_expected_goals: float
    
    # Confidence metrics
    prediction_confidence: float
    rating_uncertainty: float
    
    # Betting odds
    team1_fair_odds: float
    draw_fair_odds: float
    team2_fair_odds: float
    
    # Score probabilities
    most_likely_scores: List[Dict[str, any]]
    
    # Additional stats
    over_under_2_5: Dict[str, float]
    both_teams_score_prob: float
    
    # AI recommendation
    recommendation: str
    confidence_level: str


class TrueSkillAIEngine:
    """
    Advanced AI engine using TrueSkill for football match predictions
    
    Features:
    - Probabilistic outcome modeling
    - Expected goals simulation
    - Score distribution prediction
    - Confidence quantification
    - Fair odds calculation
    """
    
    def __init__(self):
        self.rating_system = TRUESKILL_ENV
        
    def predict_match(
        self,
        team1: TeamSkill,
        team2: TeamSkill,
        n_simulations: int = 10000,
    ) -> MatchPrediction:
        """
        Generate comprehensive match prediction using TrueSkill ratings
        
        Args:
            team1: Home team skill
            team2: Away team skill
            n_simulations: Number of Monte Carlo simulations for score distribution
            
        Returns:
            Complete MatchPrediction with probabilities, expected goals, and recommendations
        """
        # Get outcome probabilities from TrueSkill model
        outcome_probs = expected_outcome_probabilities(team1, team2)
        
        # Calculate expected goals based on skill difference
        team1_lambda, team2_lambda = self._calculate_expected_goals(team1, team2)
        
        # Run Monte Carlo simulation for score distribution
        score_distribution = self._simulate_scores(team1_lambda, team2_lambda, n_simulations)
        
        # Calculate over/under and both teams score
        over_under = self._calculate_over_under(score_distribution, threshold=2.5)
        btts = self._calculate_btts(score_distribution)
        
        # Calculate fair betting odds
        team1_odds = self._prob_to_odds(outcome_probs["team1_win"])
        draw_odds = self._prob_to_odds(outcome_probs["draw"])
        team2_odds = self._prob_to_odds(outcome_probs["team2_win"])
        
        # Calculate confidence metrics
        confidence = self._calculate_confidence(team1, team2, outcome_probs)
        uncertainty = self._calculate_uncertainty(team1, team2)
        
        # Generate AI recommendation
        recommendation, confidence_level = self._generate_recommendation(
            outcome_probs, confidence, team1_odds, draw_odds, team2_odds
        )
        
        return MatchPrediction(
            team1=team1.team,
            team2=team2.team,
            team1_rating=team1,
            team2_rating=team2,
            team1_win_prob=outcome_probs["team1_win"],
            draw_prob=outcome_probs["draw"],
            team2_win_prob=outcome_probs["team2_win"],
            team1_expected_goals=team1_lambda,
            team2_expected_goals=team2_lambda,
            prediction_confidence=confidence,
            rating_uncertainty=uncertainty,
            team1_fair_odds=team1_odds,
            draw_fair_odds=draw_odds,
            team2_fair_odds=team2_odds,
            most_likely_scores=score_distribution[:10],  # Top 10
            over_under_2_5=over_under,
            both_teams_score_prob=btts,
            recommendation=recommendation,
            confidence_level=confidence_level,
        )
    
    def _calculate_expected_goals(self, team1: TeamSkill, team2: TeamSkill) -> Tuple[float, float]:
        """
        Calculate expected goals using TrueSkill ratings
        
        Based on skill difference and mapped to realistic goal ranges
        """
        # Skill difference relative to initial uncertainty
        skill_diff = (team1.mu - team2.mu) / TRUESKILL_ENV.sigma
        
        # Map skill difference to goal expectation (centered around 1.5 goals per team)
        # Higher skill → more goals, lower opponent skill → more goals
        base_goals = 1.5
        
        # Team1 (home) gets advantage + skill boost
        home_advantage = 0.2
        team1_lambda = base_goals + home_advantage + (skill_diff * 0.15)
        
        # Team2 (away)
        team2_lambda = base_goals - (skill_diff * 0.15)
        
        # Clamp to realistic ranges [0.5, 3.5]
        team1_lambda = max(0.5, min(3.5, team1_lambda))
        team2_lambda = max(0.5, min(3.5, team2_lambda))
        
        return float(team1_lambda), float(team2_lambda)
    
    def _simulate_scores(
        self, lambda1: float, lambda2: float, n_sims: int
    ) -> List[Dict[str, any]]:
        """
        Monte Carlo simulation of match scores using Poisson distribution
        
        Returns top score probabilities sorted by likelihood
        """
        # Generate all reasonable score combinations (0-7 goals each team)
        score_probs = {}
        
        for score1 in range(8):
            for score2 in range(8):
                prob = poisson.pmf(score1, lambda1) * poisson.pmf(score2, lambda2)
                score_probs[(score1, score2)] = prob
        
        # Sort by probability
        sorted_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "score": f"{s[0]}-{s[1]}",
                "home_goals": s[0],
                "away_goals": s[1],
                "probability": float(p),
            }
            for (s, p) in sorted_scores
        ]
    
    def _calculate_over_under(self, score_dist: List[Dict], threshold: float = 2.5) -> Dict[str, float]:
        """Calculate over/under threshold probabilities"""
        over = sum(
            s["probability"]
            for s in score_dist
            if (s["home_goals"] + s["away_goals"]) > threshold
        )
        under = 1.0 - over
        
        return {"over": float(over), "under": float(under)}
    
    def _calculate_btts(self, score_dist: List[Dict]) -> float:
        """Calculate both teams to score probability"""
        btts = sum(
            s["probability"]
            for s in score_dist
            if s["home_goals"] > 0 and s["away_goals"] > 0
        )
        return float(btts)
    
    def _prob_to_odds(self, prob: float, margin: float = 0.05) -> float:
        """Convert probability to fair betting odds (European format)"""
        if prob <= 0:
            return 999.0
        # Add bookmaker margin
        odds = (1.0 / prob) * (1 + margin)
        return round(odds, 2)
    
    def _calculate_confidence(
        self, team1: TeamSkill, team2: TeamSkill, probs: Dict[str, float]
    ) -> float:
        """
        Calculate prediction confidence based on:
        - Rating certainty (low sigma = high confidence)
        - Outcome clarity (dominant probability = high confidence)
        """
        # Lower sigma = more certain
        avg_sigma = (team1.sigma + team2.sigma) / 2
        sigma_confidence = max(0, 1.0 - (avg_sigma / TRUESKILL_ENV.sigma))
        
        # Higher max probability = more certain outcome
        max_prob = max(probs.values())
        outcome_confidence = (max_prob - 0.33) / 0.67  # Normalize from 33% to 100%
        
        # Combined confidence
        confidence = (sigma_confidence * 0.4 + outcome_confidence * 0.6)
        return float(max(0.0, min(1.0, confidence)))
    
    def _calculate_uncertainty(self, team1: TeamSkill, team2: TeamSkill) -> float:
        """Overall rating uncertainty metric"""
        avg_sigma = (team1.sigma + team2.sigma) / 2
        # Normalize to 0-1 scale
        uncertainty = avg_sigma / TRUESKILL_ENV.sigma
        return float(min(1.0, uncertainty))
    
    def _generate_recommendation(
        self,
        probs: Dict[str, float],
        confidence: float,
        odds1: float,
        odds_draw: float,
        odds2: float,
    ) -> Tuple[str, str]:
        """
        Generate AI betting recommendation based on probabilities and odds
        
        Returns (recommendation_text, confidence_level)
        """
        max_prob_outcome = max(probs, key=probs.get)
        max_prob = probs[max_prob_outcome]
        
        # Determine confidence level
        if confidence > 0.75:
            conf_level = "HIGH"
        elif confidence > 0.5:
            conf_level = "MEDIUM"
        else:
            conf_level = "LOW"
        
        # Generate recommendation
        if max_prob < 0.4:
            recommendation = "Match is highly uncertain. Consider avoiding or small stake on draw."
        elif max_prob_outcome == "team1_win":
            recommendation = f"AI predicts home win with {max_prob*100:.1f}% confidence. Fair odds: {odds1}"
        elif max_prob_outcome == "team2_win":
            recommendation = f"AI predicts away win with {max_prob*100:.1f}% confidence. Fair odds: {odds2}"
        else:
            recommendation = f"AI predicts draw with {max_prob*100:.1f}% confidence. Fair odds: {odds_draw}"
        
        if confidence < 0.5:
            recommendation += " ⚠️ Low confidence - ratings still stabilizing."
        
        return recommendation, conf_level
